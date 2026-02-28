import datetime as date
import os
from omiAI_classes.omiAI_utils import util
from omiAI_classes.omiAI_database import omiDB
from omiAI_classes.omiAI_defaultTexts import privacyPolicy, systemPrompt

def printt(string):
    print(f"> [{date.datetime.now().strftime("%H:%M:%S")}] {string}")

class AIMemory: 
    def __init__(self, config, database):
        self.cfg = config
        self.database = database

        if os.path.exists(self.cfg.pathsSystemPrompt):
            self.systemPrompt = util.loadFileRaw(self.cfg.pathsSystemPrompt)
        else:
            self.systemPrompt = systemPrompt.default()
            with open(self.cfg.pathsSystemPrompt, 'w', encoding='utf-8') as file:
                file.write(systemPrompt.default())

        self.listMemory = self.cfg.doLists
        self.historyLenWithLists = 8
        self.historyLen = self.cfg.historyLen

    def linkAI(self, AI):
        self.ai = AI

    def getSystemPrompt(self, userID):
        templates = {
            '%model%': self.cfg.getModelDisplayName(self.ai.currentModel),
            '%curTime%': date.datetime.now(date.timezone.utc).strftime('%H:%M UTC, %a %d %B, %Y'),
            '%name%': self.getUserParameter(userID, 'name', 'Unknown'),
            '%discordUsername%': self.getUserParameter(userID, 'usertag', 'Unknown'),
            '%lastInteractionTime%': self.getUserParameter(userID, 'lastInteractionTime', 'Unknown'),
            '%privacyPolicy%': privacyPolicy.getPolicy(self.ai.isOllama(self.ai.currentModel))
        }

        pr = self.systemPrompt

        for variable, value in templates.items():
            pr = pr.replace(variable, value)

        return pr
    

    def updUserInfo(self, userID, name, usertag):
        self.editUserParameter(userID, 'name', name)
        self.editUserParameter(userID, 'usertag', usertag)


    def editUserParameter(self, userID, param, value, overwrite=True):
        userID = util.processID(userID)
        path = ['db', 'userdata', userID]
        userdata = {}

        if value is None:
            value = util.obfuscateString("None")
        elif isinstance(value, str):
            value = util.obfuscateString(value)

        if self.database.fileExists(path):
            userdata = self.database.loadFile(path)

        if overwrite or param not in userdata:
            userdata[param] = value
            self.database.editFile(path, userdata)


    def getUserParameter(self, userID, param, defaultVal):
        userID = util.processID(userID)
        path = ['db', 'userdata', userID]

        if self.database.fileExists(path):
            userdata = self.database.loadFile(path)
            if param in userdata:
                return util.deobfuscateString(userdata[param])
            
        return defaultVal


    def addMessage(self, UserID, ChatID, role, content):
        if not UserID or not ChatID:
            printt("Incorrect User/Chat ID! Make sure you've set it")
            raise ValueError
        
        content = util.obfuscateString(content)
        UserID = str(UserID)
        ChatID = str(ChatID)

        file = util.processID(f'{UserID}-{ChatID}')
        path = ['db', 'conversations', file]
        lenLimit = (self.historyLenWithLists if self.listMemory else self.historyLen) * 2 # store more messages than bot can see
        messages = []
        
        if self.database.fileExists(path):
            messages = self.database.loadFile(path)

        messages.append({
            "role": role,
            "content": content
        })

        self.database.editFile(path, messages[-lenLimit:])
        

    def getMessages(self, UserID, ChatID):
        systemPrompt = self.getSystemPrompt(UserID)
        UserID = str(UserID)
        ChatID = str(ChatID)

        file = util.processID(f'{UserID}-{ChatID}')
        path = ['db', 'conversations', file]
        lenLimit = self.historyLenWithLists if self.listMemory else self.historyLen
        history = []
        
        if self.cfg.fixSystemPrompt and not self.ai.isOllama(self.ai.currentModel):
            userQ = f'From now you should follow this system prompt: \n\n{systemPrompt}'
            history = [{'role': 'user', 'content': userQ}, {'role': 'assistant', 'content': 'Okay! I will follow this system prompt from now on.'}]

        else:
            history = [{'role': 'system', 'content': systemPrompt}]

        if self.database.fileExists(path):
            messages = self.database.loadFile(path)
            messages = util.deobfuscateMessages(
                messages[-lenLimit:]
            )

            history.extend(messages)
            
        return history
    
    def saveMemory(self):
        self.database.saveAll()
    
    def unloadStep(self):
        self.database.decreaseLifetime()
    
    def getFragmentCount(self):
        return self.database.loadedFragments()

    def chatExists(self, UserID, ChatID):
        UserID = str(UserID)
        ChatID = str(ChatID)

        file = util.processID(f'{UserID}-{ChatID}')
        path = ['db', 'conversations', file]
        return self.database.fileExists(path)

    def deleteChat(self, UserID, ChatID):
        UserID = str(UserID)
        ChatID = str(ChatID)

        file = util.processID(f'{UserID}-{ChatID}')
        path = ['db', 'conversations', file]

        self.database.deleteFile(path)

    def getSession(self, userID, chatID, userMSG=None):
        context = self.getMessages(userID, chatID)
        reason = self.getUserParameter(userID, 'reasoning', True)

        if userMSG:
            context.append({"role": "user", "content": userMSG})

        return self.ai.assembleRequest(context)