# omiAI
omiAI is a base for LLM-powered discord bot that can respond to messages and with customizable personality.

> This base was initially designed to work with [Ollama](https://ollama.com/), but it's compatible with other APIs and was tested with OpenRouter.

### Features
1. Fully customizable personality
2. Flexible configuration
3. Ollama and (partial) external API support
4. Response streaming (the response is updated as it's generated)
Features that will be implemented:
1. Context compression (Bot will auto-generate summaries of conversation)
2. ChatGPT-style memories

# How to setup
## Setting up discord bot
1. Create the bot itself, if you don't know how to do that, please google it.
2. After initial creation of the bot, go to `Settings > Bot` and enable parameters like this:
   ![Bot settings](/images/img_bot.png)
   You can disable "Public Bot" so random people won't add it to their server.
   > To disable it you should set Install link in `Settings > Installation` to None.
   > I also recommend disabling it *after* you add your bot to your server, since adding it without public bot enabled is tricky.
3. Then head to `Settings > Installation` and set it up like this:
   ![Bot settings](/images/img_installation.png)
4. Acquire bot's token in `Settings > Bot`. Make sure to save it somewhere safe if you don't want to lose it.
5. Done! Now let's setup the bot itself.

## Getting omiAI itself
1. First of all, if you will be using this with Ollama, check if you have Ollama installed and if you have some models. You can check both things by simply executing:
   ```
   ollama list
   ```
   If not, install Ollama (installation instructions can be found on https://ollama.com/) and download a model:
   ```
   ollama pull gemma3n:e2b
   ```
   (Or any other model that fits you)

### Linux
2. Clone the repository:
   ```
   git clone https://github.com/omeshashika/omiAI.git
   ```
   (or any other way to download the repository)
3. Run the installation script:
   ```
   ./setup.sh
   ```
   or these commands:
   ```
   python3 -m venv .omiAIvenv
   source .omiAIvenv/bin/activate
   python3 -m pip install -r requirements.txt
   ```

### Windows
1. Download repository (Either manually or using `git`)
2. Open Terminal in the same folder where you have omiAI and install requirements:
   ```
   python -m pip install -r requirements.txt
   ```
Done! Now omiAI needs to be configured.
## Configuring
1. Use the provided configuration tool `configure_bot.py` to configure the bot.
2. If you need to tweak the config, edit the generated file.

## Running and using the bot
1. Once you've done all the preparations, make sure Ollama is running, if not, start Ollama server: (Skip if using external API)
   ```
   ollama serve
   ```
2. Run the bot itself:
   ```
   python omiAI_V2.py
   ```
3. It should appear online in the member list. Try pinging it and saying hello!

## Customization
omiAI base has feature for customizing the system prompt, thus customizing it's personality and etc
1. The system prompt file is located in the folder that you've specified.
2. The default system prompt should look like this, use it as reference:
   ```
   You are a helpful assistant.
   Your AI model: %model% LLM. 
   User's namee is %name% or %discordUsername%. (Provided automatically, see privacy policy.) 
   The current time is %curTime%. Previous interaction with the user happened at %lastInteractionTime%.
   
   %privacyPolicy%
   ```
3. The system prompt in omiAI can have the following variables, none of them are truly necessary but it's good for the model to know them:
   Essential ones:
   `%name%` - User's name (Display name on discord)
   `%discordUsername%` - User's discord username, the one that's used for sending friend requests.
   `%curTime%` - So the model will know what time it is. (The time is specified in UTC timezone)
   Extra ones:
   `%model%` - Name of the model the bot is using.
   `%lastInteractionTime%` - The time when user send previous message.
   `%privacyPolicy%` - A long text that's not really useful, however the bot becomes aware of it's privacy policy.

## Useful internal commands:
These are commands that can be sent only by the owner, otherwise they are ignored completely:
1. `omiAIbase.saveMemory` - Forces the bot to save it's memory.
2. `omiAIbase.reloadConfig` - Reload bot's config, for example when you are changing the system prompt, so you don't have to restart it everytime.
3. `omiAIbase.changeModel <model ID here>` - Change bot's model. Won't work if the model isn't in the config, so you won't change the model to "fhak;lfhalk;fh;la" accidentally.
4. `omiAIbase.clearBuffer` - Save and clear temporalily loaded memory fragments.

