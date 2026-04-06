import aiohttp, os
import datetime as date
from omiAI_classes.omiAI_utils import util

def printt(string):
    print(f"> [{date.datetime.now().strftime("%H:%M:%S")}] {string}")

import logging
logger = logging.getLogger(__name__)

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
            url = f'http://localhost:{os.environ.get("OLLAMA_PORT", 11434)}/api/chat'

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers, timeout=300) as post:
                    async for line in post.content:
                        try: 
                            yield util.extractJson(line.decode())
                        except Exception as e:
                            logger.error("Failed to yield util.extractJson(line.decode()): %s", e)
                            continue
        except Exception as e:
            logger.error(f"Failed to reach AI API: {e}")
    

    def decodeChunk(self, chunk):
        try:
            if "message" in chunk:
                return chunk.get("message").get("content", '')
            
            elif "messages" in chunk:
                return chunk.get("messages")[0].get("content", '')
            
            elif "choices" in chunk:
                return chunk.get("choices")[0].get("delta").get("content", '')
            
            elif "response" in chunk:
                return chunk.get("response", '')
            
            else:
                if 'error' in chunk:
                    logger.critical(chunk.get("error").get('message', 'Unknown Error Occured'))
                logger.debug("Couldn't retrieve message/messages/choices/response from chunk: %s", str(chunk))

        except Exception as e:
            logger.error("Error while decoding chunk: %s", e)
            pass # ¯\_(ツ)_/¯ commenting this off because some external APIs send empty responses for no reason which causes the console go crazy
        
        return ''