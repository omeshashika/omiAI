import json, re, math, aiohttp, os, random, time, asyncio, base64
import datetime as date
import hashlib as hasher

def printt(string):
    print(f"> [{date.datetime.now().strftime("%H:%M:%S")}] {string}")

class util:
    @staticmethod
    def saveFile(filename, file):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(file, f, ensure_ascii=False)
        # print(f"File has been saved succesfully as {filename}!")

    @staticmethod
    def loadFile(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
            # print(f"Loaded {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found.")

    @staticmethod
    def loadFileRaw(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
            # print(f"Loaded {filename}")
        except FileNotFoundError:
            print(f"File {filename} not found.")

    @staticmethod
    def _find_safe_split(text, max_length):
        last_space = text.rfind(' ', 0, max_length)
        if last_space > max_length * 0.8:  # Если пробел в последних 20%
            return last_space + 1
        
        # Ищем последний знак препинания
        for punct in [',', '.', '!', '?', ';', ':']:
            pos = text.rfind(punct, 0, max_length)
            if pos > max_length * 0.7:
                return pos + 1
        
        # Вынужденный разрыв
        return max_length

    @staticmethod
    def ensureNeededFiles(basePath='omiAI_Data'):
        defaultMemory = {
            'users': {},
            'conversations': {}
        }
        defaultSysPrompt = 'Current AI model: %model% LLM. \nUser is named %name% or %discordUsername%. (Provided automatically, see privacy policy.) \nThe current time is %curTime%. Previous interaction with the user happened at %lastInteractionTime%.\n\n%privacyPolicy%'

        filesToCheck = {'memory.json': defaultMemory, 'systemPrompt.txt': defaultSysPrompt}
        os.makedirs(basePath, exist_ok=True)
        
        for file, content in filesToCheck.items():
            filepath = f"{basePath}/{file}"

            if not os.path.exists(filepath):
                printt(f"Missing {file}, creating...")

                with open(filepath, 'w', encoding='utf-8') as f:
                    if filepath.endswith('.json'):
                        json.dump(content, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(content)
    
    @staticmethod
    def extractJson(dirty):
        match = re.search(r'\{.*\}', dirty, re.DOTALL)

        if match:
            try: 
                jsonStr = match.group(0)
                jsonStr = jsonStr.strip()
                return json.loads(jsonStr)
            except Exception as e:
                # printt(f"JSON extraction failed: {e}")
                return None
        return None
    
    @staticmethod
    def processID(ID):
        obfuscatePrefix = "omiAIbase-obf:"

        ID = str(ID)
        if ID.startswith(obfuscatePrefix):
            return ID
        else:
            ID = ID.encode('utf-8')
            processed = hasher.md5(ID)
            return obfuscatePrefix + processed.hexdigest()
    
    @staticmethod
    def obfuscateString(string):
        obfuscatePrefix = "omiAIbase-obf:"

        if string.startswith(obfuscatePrefix):
            return string
        else:
            string = string.encode('utf-8')
            stringB64 = base64.b64encode(string)
            return obfuscatePrefix + stringB64.decode('utf-8')
    
    @staticmethod
    def deobfuscateString(stringB64):
        obfuscatePrefix = "omiAIbase-obf:"

        if stringB64.startswith(obfuscatePrefix):
            string = base64.b64decode(stringB64.removeprefix(obfuscatePrefix))
            return string.decode('utf-8')
        else:
            return stringB64
    
    @staticmethod
    def deobfuscateMessages(chat):
        output = []

        for message in chat:
            try:
                output.append({
                    "role": message.get("role"),
                    "content": util.deobfuscateString(
                        message.get("content")
                    )
                })
            except Exception as e:
                print("watafak", e )

        return output
    
    @staticmethod
    def removeObfPrefix(string):
        obfuscatePrefix = "omiAIbase-obf:"
        return string.removeprefix(obfuscatePrefix)
    
    def removeObfPrefixes(filepath):
        obfuscatePrefix = "omiAIbase-obf:"

        return [p.removeprefix(obfuscatePrefix) for p in filepath]
    
    @staticmethod
    def hashify(thingToHash):
        thingToHash = str(thingToHash)
        theHash = hasher.md5(thingToHash.encode('utf-8'))
        return str(theHash.hexdigest())
    
    @staticmethod
    def lenghtSplit(text, lenght=2000, divider='\n'):
        if len(text) < lenght:
            return [text]

        parts = text.split(divider)
        processedParts = []
        for part in parts:
            while len(part) > lenght:
                splitPos = util._find_safe_split(part, lenght)
                processedParts.append(part[:splitPos])
                part = part[splitPos:]
            processedParts.append(part)

        truncated = [[]]
        index = 0
        currentLenght = 0

        for part in processedParts:
            if currentLenght + len(part) + len(divider) > lenght:
                truncated.append([])
                index += 1
                currentLenght = 0

            truncated[index].append(part)
            currentLenght += len(part) + len(divider)

        return [divider.join(chunk) for chunk in truncated if chunk]
    
    @staticmethod
    def niceProgressBar(cur, max, text="Please wait...", elements=50):
        percentage = min(1, cur / max)
        print(f"\r{text} <" + ("#" * math.floor(percentage * elements)) + "-" * ( elements - math.floor(percentage * elements)) + f"> {math.floor(percentage * 1000)/10}/100%", flush=False, end = '')

    @staticmethod
    def niceTokenSpeedBar(cur, max, text="Please wait...", elements=50):
        percentage = min(1, cur / max)
        print(f"\r> [API] {text} <" + ("#" * math.floor(percentage * elements)) + "-" * ( elements - math.floor(percentage * elements)) + f"> {math.floor(cur * 10)/10} t/s" + " " * 10, flush=False, end = '')

    @staticmethod
    def formatPath(baseDir, path):
        path = '/'.join(path)
        if path.endswith(".json"):
            return baseDir + "/" + path
        else:
            return baseDir + "/" + path + ".json"
    
    @staticmethod
    def truncateText(text, maxLen):
        if len(text) <= maxLen:
            return text
        else:
            return text[:maxLen-3] + '...' 
        
    @staticmethod
    def timeToString(time):
        days, remaining_hours = divmod(time, 86400)
        hours, remaining_seconds = divmod(remaining_hours, 3600)
        minutes, final_seconds = divmod(remaining_seconds, 60)
        string = ''

        if days:
            string += f'{days}d '

        string += f"{hours:02d}:{minutes:02d}:{final_seconds:02d}"

        return string
    
    @staticmethod
    def includeCitation(message, citation=None, author=None):
        if citation:
            return message + f'\n\n<system>\nThe user is referecing a message by {author}: \n"{citation}"\n</system>"'
        
        return message
    
    @staticmethod
    def removeThinking(string):
        cleared = re.sub(r'<think>.*?</think>', "", string)

        if string.startswith("<think>") and not cleared:
            return ""
        
        return cleared