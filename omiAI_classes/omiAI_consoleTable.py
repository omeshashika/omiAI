from omiAI_classes.omiAI_utils import util

class omiAIconsole:
    def __init__(self, config):
        self.config = config
        self.filename = self.config.filename.split('.')[0].removesuffix('_default')
        self.header = f'omiAI base • {self.filename} • {self.config.getModelDisplayName(self.config.currModel)}'
        self.uptime = 0

        self.contents = {
            "header": self.header,
            "LLM status": ['Idling', '- tokens/s'],
            "Memory": ['0 fragments', f'Saving in <{self.config.historySavePeriod} hrs.'],
            "Status": ['OK', '-'],
            "footer": ['Uptime', self.uptime]
        }

    def updateLMStatus(self, status, tps):
        if isinstance(tps, str):
            self.contents['LLM status'] = [status, f"{tps} tokens/s"]
        else:
            self.contents['LLM status'] = [status, f"{tps:.2f} tokens/s"]
        
            

    def updateMemoryStatus(self, fragments, savetime=None, override=None):
        if not savetime:
            savetime = f'{self.config.historySavePeriod} hrs.'

        self.contents['Memory'] = [f"{fragments} fragments", f"Saving in <{savetime}"]

        if override:
            self.contents['Memory'][0] = override
    
    def updateStatus(self, title, subtitle):
        self.contents['Status'] = [title, subtitle]

    def getData(self):
        return self.uptime
    
    def replaceData(self, newData):
        self.uptime = newData

    def buildTable(tbl):
        table = []

        for key, value in tbl.items():
            if key == 'header':
                table.append( f"+{'-' * 49}+" )
                table.append( f": {value:<47} :" )
                table.append( f"+{'-' * 49}+" )

            elif key == 'footer':
                spaces = ' ' * (47 - len(value[0]) - len(util.timeToString(value[1])))

                table.pop(-1)
                table.append( f"+{'-' * 49}+" )
                table.append(f': {value[0]}{spaces}{util.timeToString(value[1])} :')
                table.append( f"+{'-' * 49}+" )
            
            else:
                first = True
                for el in value:
                    el = util.truncateText(el, 30)
                    if first:
                        first = False
                        spaces = ' ' * (47 - len(el) - len(key))
                        table.append(f': {key}{spaces}{el} :')
                    else:
                        spaces = ' ' * (47 - len(el))
                        table.append(f': {spaces}{el} :')
                
                table.append(f': {'- ' * 24}:')

        result = '\n'.join(table) + '\n'
        return result + f'\033[{len(table)}A\r'
    
    def tableDraw(self):
        print(omiAIconsole.buildTable(self.contents), end='')

    def updateUptime(self, model=None):
        self.uptime += 1

        if model:
            self.contents['header'] = f'omiAI base • {self.filename} • {model}'
        self.contents['footer'][1] = self.uptime

        self.tableDraw()