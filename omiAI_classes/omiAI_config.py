import datetime as date
import os
import re
from pathlib import Path
from omiAI_classes.omiAI_utils import util

def printt(string):
    print(f"> [{date.datetime.now().strftime("%H:%M:%S")}] {string}")

class AIConfig:
    def __init__(self, file):
        self.file = file
        self.initConfig()
        self.filename = file.replace('/', '\\').split('\\')[-1]

        # discord
        self.token = self.cfg.get("token")
        self.statusIsText = self.cfg.get('useStatusesInsteadOfModel', False)
        self.customStatuses = self.cfg.get('discordStatuses')
        self.allowDMs = self.cfg.get('discordAllowDM', True)
        self.ownerID = self.cfg.get('discordBotOwnerID')
        self.guildLock = self.cfg.get("discordGuildLock", False)
        self.allowedGuilds = self.cfg.get("discordAllowedGuilds")

        # AI config
        self.defaultAPIurl = self.cfg.get("defaultAPIurl", "ollama")
        self.defaultAPIkey = self.cfg.get('defaultAPIkey', '-')

        self.currModel = self.cfg.get('defaultModel', self.cfg.get("models")[0].get("id"))
        self.genOptions = self.cfg.get('APIOptions', {})

        self.fixSystemPrompt = self.cfg.get("systemPromptFix", False)

        if self.fixSystemPrompt:
            printt("NOTE: systemPromptFix is enabled, it should be only used if A: You are using external API; B: You get errors from the provider.")

        if not any(model.get('id') == self.currModel for model in self.cfg['models']): 
            printt(f'!!! WARNING: Model {self.currModel} not in model list! You probably will encounter issues! if the model in defaultModelID is not valid.')

        # UI
        self.doStreaming = self.cfg.get('doStreaming', True)
        self.secondsPerUpd = self.cfg.get('secondsBetweenMessageUpdates', 1)
        
        # memory
        self.historyLen = self.cfg('numOfMessagesInMemory', 30)
        self.doLists = self.cfg('experimentalCompressedMemory', True)
        self.historySavePeriod = self.cfg('hoursBetweenMemorySaves', 6)

        # paths
        self.baseDir = str( Path(file).parent.resolve() / self.cfg.get("baseDir", "omiAI_Data") )
        os.makedirs(self.baseDir, exist_ok=True)

        self.pathsSystemPrompt = self.baseDir + "/systemPrompt.txt"

        # printt(f"Running on {self.getModelDisplayName( self.currModel )}")
        

    def changeModel(self, model):
        self.currModel = model


    def getRawConfig(self):
        return self.cfg
    

    def getModelDisplayName(self, model):
        for mdl in self.cfg.get('models'):
            if model == mdl.get('id') and 'title' in mdl:
                return mdl.get('title')
        
        # if nothing has been found: 
        return model    
    
    def getModelProvider(self, model):
        for mdl in self.cfg.get('models'):
            if model == mdl.get('id') and 'apiurl' in mdl:
                return mdl.get('apiurl')
        
        # if nothing has been found: 
        return self.defaultAPIurl    
    
    def getModelAPIKey(self, model):
        for mdl in self.cfg.get('models'):
            if model == mdl.get('id') and 'apikey' in mdl:
                return mdl.get('apikey')
        
        # if nothing has been found: 
        return self.defaultAPIkey    


    def initConfig(self):
        file = self.file
        try:
            self.cfg = util.loadFile(file)
            # printt(f"config loaded ({file})")
        except Exception as e:
            printt(f"Config failed to load : {e}")
            print()