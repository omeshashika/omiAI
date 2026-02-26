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
        self.token = self.cfg["token"]
        self.statusIsText = self.cfg['useStatusesInsteadOfModel']
        self.customStatuses = self.cfg['discordStatuses']
        self.allowDMs = self.cfg['discordAllowDM']
        self.ownerID = self.cfg['discordBotOwnerID']
        self.guildLock = self.cfg["discordGuildLock"]
        self.allowedGuilds = self.cfg["discordAllowedGuilds"]

        # AI config
        self.defaultAPIurl = self.cfg["defaultAPIurl"]
        self.defaultAPIkey = self.cfg['defaultAPIkey']

        self.currModel = self.cfg['defaultModel']
        self.genOptions = self.cfg['APIOptions']

        self.fixSystemPrompt = self.cfg["systemPromptFix"]

        if self.fixSystemPrompt:
            printt("NOTE: systemPromptFix is enabled, it should be only used if A: You are using external API; B: You get errors from the provider.")

        if not any(model.get('id') == self.currModel for model in self.cfg['models']): 
            printt(f'!!! !!! WARNING: Model {self.currModel} not in model list! You probably will encounter issues! if the model in defaultModelID is not valid.')

        # UI
        self.doStreaming = self.cfg['doStreaming']
        self.secondsPerUpd = self.cfg['secondsBetweenMessageUpdates']
        
        # memory
        self.historyLen = self.cfg['numOfMessagesInMemory']
        self.doLists = self.cfg['experimentalCompressedMemory']
        self.historySavePeriod = self.cfg['hoursBetweenMemorySaves']

        # paths
        self.baseDir = str( Path(file).parent.resolve() / self.cfg['baseDir'] )
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