from omiAI_classes.omiAI_utils import util
import os

# Loaded file formating will be like this:
# "index": {
#     "path": ["parent_folder", "sub_folder", "file_name.json"] (if json is not specified it'll assume it's json)
#     "content": anything that can be turned into json,
#     "remainingLifetime": 30 (INT)
# }

# Path example: ["folder1", "folder-inside-folder1", "file_name"]

class omiDB:
    def __init__(self, dbPath, defaultLifetime=10):
        self.defaultLifetime = int(defaultLifetime)
        self.rootPath = dbPath

        self.loadedFiles = {}


    def loadIntoMemory(self, file):
        if self.fileExists(file):
            file = util.removeObfPrefixes(file)
            objIndex = util.hashify(file)
            contents = util.loadFile(
                util.formatPath(self.rootPath, file)
            )

            self.loadedFiles[objIndex] = {
                "path": file,
                "content": contents,
                "remainingLifetime": self.defaultLifetime
            }

            return contents
        else:
            raise Exception("Couldn't load file that doesn't even exist")
    

    def saveFile(self, file, content):
        file = util.removeObfPrefixes(file)
        path = util.formatPath(self.rootPath, file)

        util.saveFile(path.replace('/', '\\'), content)


    def fileExists(self, file):
        file = util.removeObfPrefixes(file)
        path = util.formatPath(self.rootPath, file)
        objIndex = util.hashify(file)
        
        if os.path.exists(path):
            return True
        
        if objIndex in self.loadedFiles:
            return True
        
        return False


    def loadFile(self, path):
        path = util.removeObfPrefixes(path)
        objIndex = util.hashify(path)

        if objIndex in self.loadedFiles:
            return self.loadedFiles[objIndex].get("content")
        else:
            return self.loadIntoMemory(path)


    def editFile(self, path, contents):
        path = util.removeObfPrefixes(path)
        objIndex = util.hashify(path)

        if objIndex in self.loadedFiles:
            self.loadedFiles[objIndex]["content"] = contents
            self.loadedFiles[objIndex]["remainingLifetime"] = self.defaultLifetime
        else:
            self.loadedFiles[objIndex] = {
                "path": path,
                "content": contents,
                "remainingLifetime": self.defaultLifetime
            }

    def deleteFile(self, path):
        path = util.removeObfPrefixes(path)
        objIndex = util.hashify(path)

        if objIndex in self.loadedFiles:
            del self.loadedFiles[objIndex]
        
        pathFormatted = util.formatPath(self.rootPath, path)
        if os.path.exists(pathFormatted):
            os.remove(pathFormatted)
    

    def decreaseLifetime(self): # make all the files smoke a fat joint
        keysToDelete = []

        for key in self.loadedFiles.keys():
            lifetime = self.loadedFiles[key]["remainingLifetime"] 

            if lifetime <= 1:
                self.saveFile(
                    self.loadedFiles[key]["path"], 
                    self.loadedFiles[key]["content"]
                )
                
                keysToDelete.append( key )
            else:
                self.loadedFiles[key]["remainingLifetime"]  -= 1

        if keysToDelete:
            for key in keysToDelete:
                del self.loadedFiles[key]


    def saveAll(self):
        for key in self.loadedFiles.keys():
            self.saveFile(
                self.loadedFiles[key]["path"], 
                self.loadedFiles[key]["content"]
            )

    def loadedFragments(self):
        return len(self.loadedFiles.keys())
    
    def unloadAllFragments(self):
        self.saveAll()
        self.loadedFiles = {}