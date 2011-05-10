import os
import re
import sys
import ast
import json
import shutil
from templates import *
from PyQt4 import QtCore, QtGui, uic

SYS_ROOT = r'C:\Program Files (x86)'
STARFARER_ROOT = SYS_ROOT + r'\Fractal Softworks\Starfarer\starfarer-all'

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi('mainWindow.ui')
        self.ui.show()
        
        self.connect(self.ui.actionLoad_Mission, QtCore.SIGNAL('triggered()'), self.loadMissionCallback)
        self.connect(self.ui.actionSave_Mission, QtCore.SIGNAL('triggered()'), self.saveMissionCallback)
        
        self.connect(self.ui.addPlayerShipButton, QtCore.SIGNAL('clicked()'), lambda: self.addShipCallback(True))
        self.connect(self.ui.removePlayerShipButton, QtCore.SIGNAL('clicked()'), lambda: self.removeShipCallback(True))
        self.connect(self.ui.makePlayerShipImportantButton, QtCore.SIGNAL('clicked()'), lambda: self.makeShipImportantCallback(True))
        
        self.connect(self.ui.addEnemyShipButton, QtCore.SIGNAL('clicked()'), lambda: self.addShipCallback(False))
        self.connect(self.ui.removeEnemyShipButton, QtCore.SIGNAL('clicked()'), lambda: self.removeShipCallback(False))
        self.connect(self.ui.makeEnemyShipImportantButton, QtCore.SIGNAL('clicked()'), lambda: self.makeShipImportantCallback(False))
        
        self.init_data(STARFARER_ROOT)
    
    def init_data(self, sfRoot):
        self.sfRoot = sfRoot
        self.sfData = self.sfRoot + r'\data'
        self.sfMissions = self.sfData + r'\missions'
        self.sfMissionList = self.sfMissions + r'\mission_list.json'
        self.sfHulls = self.sfData + r'\hulls'
        self.sfVariants = self.sfData + r'\variants'
        self.sfFighters = self.sfVariants + r'\fighters'
        
        self.missionData = None
        
        self.allShips = {}
        for variant in (item for item in os.listdir(self.sfVariants) if '.variant' in item):
            with open(self.sfVariants + os.sep + variant, 'r') as f:
                v = ast.literal_eval(f.read())
                self.allShips[v['variantId']] = v
        
        self.allWings = {}
        for wing in (item for item in os.listdir(self.sfFighters) if '.variant' in item):
            with open(self.sfFighters + os.sep + wing, 'r') as f:
                v = ast.literal_eval(f.read())
                self.allWings[v['variantId']] = v
        
        self.allHulls = {}
        for ship in (item for item in os.listdir(self.sfHulls) if '.ship' in item):
            with open(self.sfHulls + os.sep + ship, 'r') as f:
                s = ast.literal_eval(f.read())
                self.allHulls[s['hullId']] = s
        
        self.allSprites = {}
        for id, hull in self.allHulls.iteritems():
            spriteLocation = self.sfRoot + os.sep + hull['spriteName']
            icon = QtGui.QIcon(spriteLocation)
            self.allSprites[id] = icon
        
        self.wingData = self.readDataFile(self.sfHulls + os.sep + 'wing_data.csv')
        self.shipData = self.readDataFile(self.sfHulls + os.sep + 'ship_data.csv')
        
        with open(self.sfMissionList, 'r') as file:
            self.missionList = ast.literal_eval(file.read())
        
        self.populateShipBrowser()
    
    def populateShipBrowser(self):
        self.ui.shipBrowserTree.clear()
    
        shipData = dict([ (ship['id'], ship) for ship in self.shipData.values() ])
        for ship in sorted(self.allShips.values(), key=lambda x: x['variantId'].lower()):
            hullName = ship['hullId']
            variantName = ship['variantId']
            icon = self.allSprites[hullName]
            displayName = ' '.join((shipData[hullName]['name'] + '-class', ship['displayName'], shipData[hullName]['designation']))
            
            fleetPts = '% 3d' % int(shipData[hullName]['fleet pts'])
            
            newItem = QtGui.QTreeWidgetItem(['', displayName, fleetPts, variantName, 'SHIP'])
            newItem.setIcon(0, icon)
            self.ui.shipBrowserTree.addTopLevelItem(newItem)
        
        wingData = dict([ (wing['variant'], wing) for wing in self.wingData.values() ])
        for fighter in sorted(self.allWings.values(), key=lambda x: x['variantId'].lower()):
            print fighter
            hullName = fighter['hullId']
            variantName = fighter['variantId']
            icon = self.allSprites[hullName]
            wingInfo = wingData[variantName]
            wingName = wingInfo['id']
            
            displayHullName = hullName.split('_')
            for i, v in enumerate(displayHullName):
                displayHullName[i] = v[0].upper() + v[1:]
            displayHullName = ' '.join(displayHullName)
            displayName = ' '.join((displayHullName, fighter['displayName'], 'Wing'))
            
            fleetPts = '% 3d' % int(wingInfo['fleet pts'])
            
            newItem = QtGui.QTreeWidgetItem(['x%s' % wingInfo['num'], displayName, fleetPts, wingName, 'FIGHTER_WING'])
            newItem.setIcon(0, icon)
            self.ui.shipBrowserTree.addTopLevelItem(newItem)
        
        self.ui.shipBrowserTree.sortItems(1, 0)
        self.ui.shipBrowserTree.sortItems(2, 0)
        for col in xrange(self.ui.shipBrowserTree.columnCount()):
            self.ui.shipBrowserTree.resizeColumnToContents(col)
    
    def readDataFile(self, dataFilePath):
        with open(dataFilePath) as f:
            dataLines = map(lambda x: x.strip('\n').split(','), f.readlines())
        dataHeaders = dataLines[0]
        idIndex = dataHeaders.index('id')
        data = dict([
            (dataLine[idIndex], dict(zip(dataHeaders, dataLine)))
            for dataLine in dataLines[1:]
            if len(dataLine) > idIndex and dataLine[idIndex] != ''
        ])
        return data
    
    def loadMissionCallback(self):
        missionPath = QtGui.QFileDialog.getExistingDirectory(self, 'Select Mission Directory', self.sfMissions)
        if not os.path.exists(missionPath):
            return
        self.loadMission(missionPath)
    
    def loadMission(self, missionPath):
        missionShips = []
        missionObjectives = []
        with open(missionPath + '\MissionDefinition.java', 'r') as file:
            for line in file.readlines():
                line = line.split('//')[0].strip()
                if 'api.addToFleet' in line:
                    # Find all the lines that add ships to the battle
                    matchPattern = r'api\.addToFleet *?\( *?FleetSide\.(.+?) *?, *?"(.+?)" *?, *?FleetMemberType\.(.+?) *?,( *?"(.+?)" *?,)? *? ?(.+?) *?\)'
                    line = re.match(matchPattern, line)
                    if line != None:
                        groups = line.groups()
                        missionShips.append({
                            'side':      groups[0],
                            'variant':   groups[1],
                            'type':      groups[2],
                            'name':      groups[4],
                            'flagship':  groups[5]
                        })
                elif 'api.addBriefingItem' in line:
                    matchPattern = r'api.addBriefingItem *?\( *?"(.+?)" *?\)'
                    line = re.match(matchPattern, line)
                    if line != None:
                        groups = line.groups()
                        missionObjectives.append(groups[0])
        
        with open(missionPath + '\descriptor.json', 'r') as file:
            missionDescriptor = ast.literal_eval(file.read())
        
        with open(missionPath + '\mission_text.txt', 'r') as file:
            missionText = file.read()
        
        self.missionData = {
            'path': missionPath,
            'fleets': missionShips,
            'text': missionText,
            'descriptor': missionDescriptor,
            'objectives': missionObjectives,
        }
        
        self.populateMissionObjectives(self.missionData['objectives'])
        self.populateMissionName(self.missionData['descriptor']['title'])
        self.populateMissionText(self.missionData['text'])
        self.populateFleets(self.missionData['fleets'])
    
    def populateMissionObjectives(self, objectives):
        for objective in objectives:
            print objective
    
    def populateMissionName(self, missionName):
        self.ui.missionNameEdit.setText(missionName)
    
    def populateMissionText(self, missionText):
        self.ui.missionText.setPlainText(missionText)
    
    def populateFleets(self, missionShips):
        self.playerListModel = QtGui.QStandardItemModel()
        self.enemyListModel = QtGui.QStandardItemModel()
        
        vo = self.ui.playerShips.viewOptions()
        vo.displayAlignment = QtCore.Qt.AlignCenter
        self.ui.playerShips.setModel(self.playerListModel)
        self.ui.enemyShips.setModel(self.enemyListModel)
        
        for listModel in (self.playerListModel, self.enemyListModel):
            listModel.setVerticalHeaderItem(0, QtGui.QStandardItem("Ship"))
            listModel.setVerticalHeaderItem(1, QtGui.QStandardItem("Variant"))
            listModel.setVerticalHeaderItem(2, QtGui.QStandardItem("Name"))
            listModel.setVerticalHeaderItem(3, QtGui.QStandardItem("Value"))
            listModel.setVerticalHeaderItem(4, QtGui.QStandardItem("Flagship"))
            listModel.setVerticalHeaderItem(5, QtGui.QStandardItem("Critical"))
        
        playerCol = 0
        enemyCol = 0
        # get values of missionShips
        missionShipValues = {}
        for ship in missionShips:
            if ship['type'] == 'SHIP':
                variant = self.allShips[ship['variant']]
                value = self.shipData[variant['hullId']]['fleet pts']
            else:
                value = self.wingData[ship['variant']]['fleet pts']
            missionShipValues[ship['variant']] = value
        
        missionShips = sorted(missionShips, key=lambda x: -int(missionShipValues[x['variant']]))
        missionShips = sorted(missionShips, key=lambda x: x['flagship'] == 'false')
        for ship in missionShips:
            if ship['type'] == 'SHIP':
                variant = self.allShips[ship['variant']]
                iconText = ''
                value = missionShipValues[ship['variant']]
            else:
                variantName = self.wingData[ship['variant']]['variant']
                variant = self.allWings[variantName]
                iconText = "x%s" % self.wingData[ship['variant']]['num']
                value = missionShipValues[ship['variant']]
            
            flagShip = ship['flagship']
            variantName = ship['variant']
            hullId = variant['hullId']
            shipName = ship['name']
            
            if ship['side'] == 'PLAYER':
                listModel = self.playerListModel
                playerCol += 1
                col = playerCol
            else:
                listModel = self.enemyListModel
                enemyCol += 1
                col = enemyCol
            listModel.setItem(0, col-1, QtGui.QStandardItem(self.allSprites[hullId], iconText))
            listModel.setItem(1, col-1, QtGui.QStandardItem(variantName))
            listModel.setItem(2, col-1, QtGui.QStandardItem(shipName if shipName else ''))
            listModel.setItem(3, col-1, QtGui.QStandardItem(value))
            listModel.setItem(4, col-1, QtGui.QStandardItem(flagShip))
        
        self.ui.playerShips.resizeRowsToContents()
        self.ui.playerShips.resizeColumnsToContents()
        self.ui.enemyShips.resizeRowsToContents()
        self.ui.enemyShips.resizeColumnsToContents()
    
    def makeShipLines(self, fleets, side='PLAYER', indent = '        '):
        lines = []
        lineWithoutName = indent + 'api.addToFleet(FleetSide.%(side)s, "%(variant)s", FleetMemberType.%(type)s, %(flagship)s);'
        lineWithName    = indent + 'api.addToFleet(FleetSide.%(side)s, "%(variant)s", FleetMemberType.%(type)s, "%(name)s", %(flagship)s);'
        for ship in fleets:
            if ship['side'] == side:
                lines.append((lineWithName if ship['name'] else lineWithoutName) % ship)
        return '\n'.join(lines)
    
    def makeBreifingLines(self, objectives, indent = '        '):
        return '\n'.join([indent + 'api.addBriefingItem("' + objective + '");' for objective in objectives])
    
    def getSaveData(self):
        missionShips = []
        for side, listModel in (('PLAYER', self.playerListModel), ('ENEMY', self.enemyListModel)):
            for column in xrange(listModel.columnCount()):
                thisShip = {
                    'variant': listModel.item(1, column).text(),
                    'name': listModel.item(2, column).text(),
                    'side': side,
                    'flagship': listModel.item(4, column).text(),
                }
                thisShip['type'] = 'SHIP' if thisShip['variant'] in self.allShips.keys() else 'FIGHTER_WING'
                missionShips.append(thisShip)
        
        missionDescriptor = {
            'title': str(self.ui.missionNameEdit.text()),
            'icon': 'icon.jpg',
            'difficulty': 'EASY',               # Not finished yet
        }
        
        saveData = {
            'fleets': missionShips,
            'text': self.ui.missionText.toPlainText(),
            'objectives': self.missionData['objectives'],    # Not finished yet
            'mission_list': self.missionList,
            'descriptor': missionDescriptor,
        }
        return saveData
    
    def saveMissionCallback(self):
        saveData = self.getSaveData()
        
        indent = '        '
        packageName = saveData['descriptor']['title']
        packageName = packageName.lower().replace(' ', '')
        
        os.mkdir(packageName)
        saveDir = packageName + os.sep
        
        replaceText = {
            'package_name': packageName,
            'briefing': self.makeBreifingLines(saveData['objectives'], indent),
            'player_fleet': self.makeShipLines(saveData['fleets'], 'PLAYER', indent),
            'enemy_fleet': self.makeShipLines(saveData['fleets'], 'ENEMY', indent),
        }
        
        saveData['mission_list']['missions'].append(packageName)
        
        with open(saveDir + 'MissionDefinition.java', 'w') as f:
            f.write(missionDefinition % replaceText)
        with open(saveDir + 'mission_text.txt', 'w') as f:
            f.write(saveData['text'])
        with open(saveDir + 'descriptor.json', 'w') as f:
            f.write(json.dumps(saveData['descriptor'], indent=4))
        shutil.copy('icon.jpg', saveDir)
        
        with open('mission_list.json', 'w') as f:
            f.write(json.dumps(saveData['mission_list'], indent=8))
        
        self.init_data(self.sfRoot)
        self.loadMission(saveDir)
    
    def addShipCallback(self, player=True):
        item = self.ui.shipBrowserTree.currentItem()
        print item.text(1)
        variant = str(item.text(3))
        type = str(item.text(4))
        
        newShip = {
            'variant': variant,
            'name': '',
            'flagship': 'false',
            'type': type,
        }
        if player:
            newShip['side'] = 'PLAYER'
        else:
            newShip['side'] = 'ENEMY'
        
        self.missionData['fleets'].append(newShip)
        self.populateFleets(self.missionData['fleets'])
    
    def removeShipCallback(self, player=True):
        if player:
            print "Remove player ship"
        else:
            print "Remove enemy ship"
    
    def makeShipImportantCallback(self, player=True):
        if player:
            print "Make player ship important"
        else:
            print "Make enemy ship important"
    
    def quitCallback(self):
        self.Quit()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    sys.exit(app.exec_())
