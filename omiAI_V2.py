import re, random, time, asyncio
from glob import glob
from pathlib import Path
import datetime as date
import logging

import discord
from discord import app_commands
from discord.ext import tasks
from discord.ui import Button, View

from omiAI_classes.omiAI_utils import util
from omiAI_classes.omiAI_config import AIConfig
from omiAI_classes.omiAI_memory import AIMemory
from omiAI_classes.omiAI_AIengine import AIsystem
from omiAI_classes.omiAI_database import omiDB
from omiAI_classes.omiAI_consoleTable import omiAIconsole



def printt(string):
    print(f"> [{date.datetime.now().strftime("%H:%M:%S")}] {string}")


class OmiAICore:
    def __init__(self, cfg, aisys):
        self.cfgPath = cfg
        self._aisysLink = aisys

        self._config = AIConfig(self.cfgPath)
        self._disp = omiAIconsole(self._config)
        self._database = omiDB(self._config.baseDir)
        self._memory = AIMemory(self._config, self._database)
        self._ai = self._aisysLink(self._config, self._memory)
        self._memory.linkAI(self._ai) # link AI to memory since how do you link AI before it can be initialized 

        self._intents = discord.Intents.default()
        self._intents.message_content = True
        self._intents.members = True

        self._bot = discord.Client(intents=self._intents)
        self._tree = app_commands.CommandTree(self._bot)

        self._firstTimeSaving = True
        

    async def slashMessageUpdater(self, interaction, content, messages):
        for num, text in enumerate(content):
            if num < len(messages):
                if not text == messages[num][1]:
                    await messages[num][0].edit(content=text)
            else:
                messages.append([await interaction.followup.send(content=text), text])

        return messages
    

    async def discordMessageUpdater(self, ctx, content, messages):
        for num, text in enumerate(content):
            if num < len(messages):
                if not text == messages[num][1]:
                    await messages[num][0].edit(content=text)
            else:
                if num:
                    messages.append([await ctx.channel.send(text), text])
                else:
                    messages.append([await ctx.reply(text), text])

        return messages


    async def reloadConfigCommand(self, message, command='omiAIbase.reload'):
        if str(message.author.id) == self._config.ownerID and message.content.strip().startswith(command):
            try:

                self._config = AIConfig(self.cfgPath)
                self._memory = AIMemory(self._config, self._database)

                await message.add_reaction('✅')

                self._disp.updateStatus('Reloading config...', 'This changes model to default')
                await asyncio.sleep(2)
                self._disp.updateStatus('OK', '-')

            except Exception as e:
                await message.add_reaction('❌')
                printt(f'Failed to reload: {e}')
                print()

        return


    async def saveMemoryCommand(self, message, command='omiAIbase.saveMemory'):
        if str(message.author.id) == self._config.ownerID and message.content.strip().startswith(command):
            try:
                self._memory.saveMemory()

                await message.add_reaction('✅')
                self._disp.updateMemoryStatus(self._memory.getFragmentCount(), "0 s.", override='Forced save')
                await asyncio.sleep(2)
                self._disp.updateMemoryStatus(self._memory.getFragmentCount(), "0 s.", override='Forced save')
            except Exception as e:
                await message.add_reaction('❌')
                printt(f'Failed to save memory: {e}')
                print()

        return
    

    async def saveMemoryCommand(self, message, command='omiAIbase.clearBuffer'):
        if str(message.author.id) == self._config.ownerID and message.content.strip().startswith(command):
            try:
                self._database.unloadAllFragments()

                await message.add_reaction('✅')
            except Exception as e:
                await message.add_reaction('❌')
                printt(f'Failed to clear buffer: {e}')
                print()

        return


    async def changeModelCommand(self, message, command='omiAIbase.changeModel'):
        inputModel = message.content.replace(command, '').strip()

        if str(message.author.id) == self._config.ownerID and message.content.strip().startswith(command):
            if any(model.get('id') == inputModel for model in self._config.getRawConfig()['models']): 
                try:
                    self._ai.changeModel(inputModel)

                    await message.add_reaction('✅')

                    self._disp.updateStatus('Changing', 'model...')
                    await asyncio.sleep(2)
                    self._disp.updateStatus('OK', '-')
                except Exception as e:
                    printt(f"Failed to change model: {e}")
                    print()
                    await message.add_reaction('❌')
            else:
                await message.add_reaction('❓')

        return


    async def manageMessage(self, message):
        shouldRespond = False
        shouldCite = None

        if message.content.startswith('omiAIbase.') or message.author == self._bot.user or message.author.bot:
            return False, None

        if message.guild is None:
            shouldRespond = self._config.allowDMs
        elif not message.guild.id in self._config.allowedGuilds and self._config.guildLock:
            return False, None
        
        if not message.content.replace(f'<@{self._bot.user.id}>', '').strip():
            return False, None

        if self._bot.user in message.mentions:
            shouldRespond = True

        if message.reference:
            try:
                replyTo = await message.channel.fetch_message(message.reference.message_id)

                if replyTo.author == self._bot.user:
                    shouldRespond = True

                    if replyTo.reference:
                        inreplyReference = await message.channe.fetch_message(replyTo.reference.message_id)

                        if not inreplyReference.author == self._bot.user:
                            shouldCite = replyTo
                else:
                    shouldCite = replyTo

            except discord.NotFound:
                printt("Message not found (Deleted?)")
            except discord.HTTPException as e:
                printt(f"Error: {e}")
            
        return shouldRespond, shouldCite
    
    
    def getCitation(self, citation):
        if citation:
            if citation.author == self._bot.user:
                return citation.content.strip(), "you (you were replying to another user)"

            return citation.content.strip(), citation.author.global_name

        return None, None


    def _setupCommands(self):
        printt("Setting up commands")

        @self._bot.event
        async def on_error(event):
            printt(f'Error in {event}')
            print()

        @self._bot.event
        async def on_message(message):
            await self.reloadConfigCommand(message)
            await self.saveMemoryCommand(message)
            await self.changeModelCommand(message)

            shouldRespond, shouldCitate = await self.manageMessage(message)
            citationContent, citationAuthor = self.getCitation(shouldCitate)
            
            if shouldRespond:
                userID = message.author.id
                chatID = str(message.channel.id)
                userMessage = util.includeCitation(
                    message.content.replace(f'<@{self._bot.user.id}>', '').strip(),
                    citation=citationContent, author=citationAuthor
                )

                self._memory.updUserInfo(
                    userID, 
                    message.author.global_name, 
                    message.author.name
                )
                
                response = ''
                responseTime = 0
                messages = []
                startTime = time.perf_counter()
                self._disp.updateLMStatus("Preparing", '-')
                
                try:
                    async with message.channel.typing(): 
                        async for chunk in self._ai.generateResponse( self._memory.getSession(userID, chatID, userMessage) ):
                            response += self._ai.decodeChunk(chunk)
                            response = util.removeThinking(response)

                            responseTime += time.perf_counter() - startTime
                            
                            currTPS, startTime = 1 / (time.perf_counter() - startTime), time.perf_counter()
                            self._disp.updateLMStatus("Generating", currTPS)

                            if responseTime > self._config.secondsPerUpd and self._config.doStreaming:
                                messages = await self.discordMessageUpdater(
                                    message,
                                    util.lenghtSplit(response + "... ⏳"), 
                                    messages
                                    )
                                responseTime = 0

                        await self.discordMessageUpdater(message, 
                            util.lenghtSplit(response), 
                            messages
                        )
                        
                        self._memory.addMessage(userID, chatID, 'user', userMessage)
                        self._memory.addMessage(userID, chatID, 'assistant', response.strip())

                        self._memory.editUserParameter(userID, 'lastInteractionTime', date.datetime.now(date.timezone.utc).strftime('%H:%M UTC, %a %d %B, %Y'))
                except Exception as e:
                    print(f"Error: {e}")

                self._disp.updateLMStatus("Idling", '-')
            # Broo why is this code such a nested mess???

            return 
        
        
        @self._tree.command(name='chat', description='chat with me')
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @app_commands.user_install()
        @app_commands.guild_install()
        @app_commands.describe(message = "your message")
        async def chat(interaction: discord.Interaction, message: str):
            userID = interaction.user.id
            chatID = f'slash{interaction.channel_id}'

            self._memory.updUserInfo(userID, interaction.user.global_name, interaction.user.name)
            
            response = ''
            responseTime = 0
            messages = []

            startTime = time.perf_counter()
            self._disp.updateLMStatus("Preparing", '-')
            await interaction.response.defer()

            try:
                async for chunk in self._ai.generateResponse( self._memory.getSession(userID, chatID, message) ):
                    response += self._ai.decodeChunk(chunk)
                    response = util.removeThinking(response)

                    responseTime += time.perf_counter() - startTime
                    
                    currTPS, startTime = 1 / (time.perf_counter() - startTime), time.perf_counter()
                    self._disp.updateLMStatus("Generating", currTPS)

                    if responseTime > self._config.secondsPerUpd and self._config.doStreaming:
                        messages = await self.slashMessageUpdater(
                            interaction, 
                            util.lenghtSplit(response + "... ⏳"),
                            messages
                            )
                        responseTime = 0

                await self.slashMessageUpdater(
                    interaction, 
                    util.lenghtSplit(response), 
                    messages
                )
                # print()

                self._memory.addMessage(userID, chatID, 'user', message)
                self._memory.addMessage(userID, chatID, 'assistant', response.strip())

                self._memory.editUserParameter(userID, 'lastInteractionTime', date.datetime.now(date.timezone.utc).strftime('%H:%M UTC, %a %d %B, %Y'))
            except Exception as e:
                print(f"Error: {e}")

            # print(self._memory.memory) # Debug
            self._disp.updateLMStatus("Idling", '-')


        @self._tree.command(name="delete_chat", description='delete your chat in this channel')
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @app_commands.user_install()
        @app_commands.guild_install()
        async def memoryWipe(interaction: discord.Interaction):
            userID = interaction.user.id
            chatIDslash = f'slash{interaction.channel_id}'
            chatIDnormal = str(interaction.channel_id) if interaction.guild else 'private'
            slashExists = self._memory.chatExists(userID, chatIDslash)
            normalExists = self._memory.chatExists(userID, chatIDnormal)

            await interaction.response.defer(ephemeral=True)

            async def memoryButtonFn(btn_interaction: discord.Interaction):
                await btn_interaction.response.defer(ephemeral=True)
                await btn_interaction.delete_original_response()

                self._memory.deleteChat(userID, chatIDnormal)
                await btn_interaction.followup.send(content='wiped normal memory', ephemeral=True)


            async def slashButtonFn(btn_interaction: discord.Interaction):
                await btn_interaction.response.defer(ephemeral=True)
                await btn_interaction.delete_original_response()

                self._memory.deleteChat(userID, chatIDnormal)
                await btn_interaction.followup.send(content='wiped /chat memory', ephemeral=True)


            async def cancelButtonFn(btn_interaction: discord.Interaction):
                await btn_interaction.response.defer(ephemeral=True)
                await btn_interaction.delete_original_response()


            if not slashExists and not normalExists:
                await interaction.followup.send("you don't any chats here")
            else:
                view = View()

                slashButton = Button(label="delete /chat memory", style=discord.ButtonStyle.primary)
                memoryButton = Button(label="delete regular memory", style=discord.ButtonStyle.primary)
                cancelButton = Button(label="cancel", style=discord.ButtonStyle.red)

                slashButton.callback = slashButtonFn
                memoryButton.callback = memoryButtonFn
                cancelButton.callback = cancelButtonFn
                
                if normalExists:
                    view.add_item(memoryButton)
                if slashExists:
                    view.add_item(slashButton)

                view.add_item(cancelButton)

                await interaction.followup.send("which chat would you like to delete?\n-# ⚠️ this cannot be undone", view=view)
        

        @self._tree.command(name='reasoning', description='enable/disable reasoning on supported models')
        @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
        @app_commands.user_install()
        @app_commands.guild_install()
        @app_commands.choices(reasoning=[
            app_commands.Choice(name='Enabled (Smarter)', value=1),
            app_commands.Choice(name='Disabled (Faster)', value=0)
        ])
        async def reasoning_command(interaction: discord.Interaction, reasoning: int):
            self._memory.editUserParameter(
                interaction.user.id, 
                'reasoning',
                True if reasoning else False
                )
            
            if reasoning:
                await interaction.response.send_message('enabled reasoning', ephemeral=True)
            else:
                await interaction.response.send_message('disabled reasoning', ephemeral=True)



    def _setupEvents(self):
        printt("Setting up events")

        @self._bot.event
        async def on_ready():
            await self._tree.sync()
            print('> [VERSION] omiAI Base V2 (Beta) - made by omi', end='\r')

            @tasks.loop(hours=self._config.historySavePeriod)
            async def memorySave():
                if self._firstTimeSaving:
                    self._firstTimeSaving = False
                else:
                    try:
                        self._disp.updateMemoryStatus(self._memory.getFragmentCount(), "60 s.")
                        await asyncio.sleep(60)
                        
                        self._memory.saveMemory()
                        self._disp.updateMemoryStatus(self._memory.getFragmentCount(), "0 s.", override='Auto-saved!')
                        await asyncio.sleep(5)
                        self._disp.updateMemoryStatus(self._memory.getFragmentCount())
                    except Exception as e:
                        printt(f"Failed to save memory: {e}")
                        print()


            @tasks.loop(minutes=30)
            async def fun_statusUpdate():
                if self._config.statusIsText:
                    await self._bot.change_presence( 
                        status=discord.Status.online,
                        activity=discord.Activity( type=discord.ActivityType.watching, name=random.choice(self._config.customStatuses) )  
                    )
                else:
                    await self._bot.change_presence(  
                        status=discord.Status.online,
                        activity=discord.Activity( type=discord.ActivityType.watching, name= self._ai.getCurrentModel() )  
                    )
            
            time.sleep(1)
            @tasks.loop(seconds=1)
            async def updTheTable():
                self._disp.updateMemoryStatus(self._memory.getFragmentCount())
                self._disp.updateUptime(model=self._ai.getCurrentModel())

            @tasks.loop(minutes=2)
            async def decayFragments():
                self._memory.unloadStep()
            
            decayFragments.start()
            updTheTable.start()
            fun_statusUpdate.start()
            memorySave.start()

        async def on_disconnect():
            self._memory.saveMemory()
            self._disp.updateStatus('Disconnected', 'Issues with connecting to discord')
        
        async def on_resumed():
            self._disp.updateStatus('OK', 'Connection resumed')


    def run(self):
        self._setupCommands()
        self._setupEvents()

        self._bot.run(self._config.token, log_level=logging.CRITICAL)





if __name__ == "__main__":
    parentFolder = Path(__file__).parent.resolve()
    extensions = '.json', '.cfg'
    cfgs, defaultCFG = [], []

    for extension in extensions:
        cfgs.extend(
            glob( str(parentFolder / f'*{extension}') )
        )
        defaultCFG.extend(
            glob( str(parentFolder / f'*default{extension}') )
        )

    if defaultCFG:
        selection = defaultCFG[0]
        printt(f"Loaded { selection.split('\\')[-1] } (Auto-selected default config)")
    else:
        printt("Please select config file:")
        for num, file in enumerate(cfgs):
            print(f"{num+1}. { file.split('\\')[-1] }")

        selection = cfgs[
            int(input( 'Choice: ') )-1
        ]

    omiAI = OmiAICore(selection, AIsystem)
    omiAI.run()