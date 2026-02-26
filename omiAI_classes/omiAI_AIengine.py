import aiohttp
import datetime as date
from omiAI_classes.omiAI_utils import util

def printt(string):
    print(f"> [{date.datetime.now().strftime("%H:%M:%S")}] {string}")

class AIsystem:
    def __init__(self, config, memory):
        self.cfg = config
        self.memory = memory

        self.currentModel = self.cfg.currModel

    def changeModel(self, model):
        self.currentModel = model

    def getCurrentModel(self):
        return self.cfg.getModelDisplayName(self.currentModel)
    
    def isOllama(self, model): 
        if self.cfg.getModelProvider(model) == 'ollama':
            return True
        else:
            return False


    def assembleRequest(self, context, stream=True, think=True):
        data = {
            "model": self.currentModel,
            "messages": context,
            "think": think,
            'stream': stream
        }
        
        if self.isOllama(self.currentModel):
            data["keep_alive"] = '1h'
            if self.cfg.genOptions:
                data["options"] = self.cfg.genOptions

        return data


    async def generateResponse(self, data):
        apikey = self.cfg.getModelAPIKey(self.currentModel)
        headers = {"Authorization": f"Bearer {apikey}"}
        url = self.cfg.getModelProvider(self.currentModel)
        if self.isOllama(self.currentModel):
            url = 'http://localhost:11434/api/chat'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=300) as post:
                    async for line in post.content:
                        try: 
                            yield util.extractJson(line.decode())
                        except Exception as e:
                            print(f"something's wrong: {e}")
                            continue
        except Exception as e:
            printt(f"Failed to reach AI API : {e}")
    

    def decodeChunk(self, chunk):
        try:
            if "message" in chunk:
                return chunk["message"].get("content")
            
            elif "messages" in chunk:
                return chunk["messages"][0].get("content")
            
            elif "choices" in chunk:
                return chunk["choices"][0]["delta"].get("content")
            
            else:
                if 'error' in chunk:
                    print(chunk['error'].get('message'))
                print(chunk)

        except Exception as e:
            # printt(f"Failed: {e}")
            # print(chunk)
            pass # ¯\_(ツ)_/¯ commenting this off because some external APIs send empty responses for no reason which causes the console go crazy
        
        return ''