import os
import re
import sys
import ast
from PyQt4 import QtCore, QtGui, uic

STARFARER_ROOT = r'C:\Program Files (x86)\Fractal Softworks\Starfarer\starfarer-all'
STARFARER_DATA = STARFARER_ROOT + r'\data'
STARFARER_MISSIONS = STARFARER_DATA + r'\missions'
STARFARER_MISSIONS_LIST = STARFARER_MISSIONS + '\mission_list.json'

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi('mainWindow.ui')
        self.ui.show()
        
        self.connect(self.ui.actionLoad_Mission, QtCore.SIGNAL('triggered()'), self.loadMissionCallback)
        
        self.connect(self.ui.addPlayerShipButton, QtCore.SIGNAL('clicked()'), lambda: self.addShipCallback(True))
        self.connect(self.ui.removePlayerShipButton, QtCore.SIGNAL('clicked()'), lambda: self.removeShipCallback(True))
        
        self.connect(self.ui.addEnemyShipButton, QtCore.SIGNAL('clicked()'), lambda: self.addShipCallback(False))
        self.connect(self.ui.removeEnemyShipButton, QtCore.SIGNAL('clicked()'), lambda: self.removeShipCallback(False))
        
        self.init_data(STARFARER_ROOT)
        return
    
    def init_data(self, sfRoot):
        self.sfRoot = sfRoot
        self.sfData = self.sfRoot + r'\data'
        self.sfMissions = self.sfData + r'\missions'
        self.sfMissionList = self.sfMissions + r'\mission_list.json'
        self.sfHulls = self.sfData + r'\hulls'
        self.sfVariants = self.sfData + r'\variants'
        self.sfFighters = self.sfVariants + r'\fighters'
        
        self.allShips = Null
        for variant in os.listdir(self.sfVariants):
            print variant
    
    def loadMissionCallback(self):
        missionPath = filename=QtGui.QFileDialog.getExistingDirectory(self, 'Select Mission Directory', STARFARER_MISSIONS)
        
        self.missionShips = []
        with open(missionPath + '\MissionDefinition.java', 'r') as file:
            for line in file.readlines():
                line = line.split('//')[0].strip()
                if 'api.addToFleet' in line:
                    # Find all the lines that add ships to the battle
                    matchPattern = r'api\.addToFleet *?\( *?FleetSide\.(.+?) *?, *?"(.+?)" *?, *?FleetMemberType\.(.+?) *?,( *?"(.+?) *?,)? *? ?(.+?) *?\) *?;'
                    line = re.match(matchPattern, line)
                    if line != None:
                        groups = line.groups()
                        self.missionShips.append({
                            'side':      groups[0],
                            'variant':   groups[1],
                            'type':      groups[2],
                            'name':      groups[4],
                            'important': groups[5]
                        })
        
        wingData = {}
        with open(self.sfHulls + '\wing_data.csv', 'r') as f:
            fileLines = f.readlines()
            headers = fileLines[0].split(',')
            idIndex = headers.index('id')
            for line in fileLines[1:]:
                line = line.strip('\n')
                line = line.split(',')
                wingData[line[idIndex]] = dict([(headers[i], data) for i, data in enumerate(line)])
        
        playerListModel = QtGui.QStandardItemModel()
        enemyListModel = QtGui.QStandardItemModel()
        for listModel in (playerListModel, enemyListModel):
            listModel.setVerticalHeaderItem(0, QtGui.QStandardItem("Ship"))
            listModel.setVerticalHeaderItem(1, QtGui.QStandardItem("Variant"))
        
        playerCol = 0
        enemyCol = 0
        for ship in self.missionShips:
            if ship['type'] == 'SHIP':
                variantLocation = self.sfVariants + os.sep + ship['variant'] + '.variant'
                iconText = ''
            else:
                variant = wingData[ship['variant']]['variant']
                variantLocation = self.sfFighters + os.sep + variant + '.variant'
                iconText = "x%s" % wingData[ship['variant']]['num']
            print variantLocation
            if os.path.exists(variantLocation):
                with open(variantLocation, 'r') as f:
                    variantData = ast.literal_eval(f.read())
                hullLocation = self.sfHulls + os.sep + variantData['hullId'] + '.ship'
                if os.path.exists(hullLocation):
                    with open(hullLocation, 'r') as f:
                        hullData = ast.literal_eval(f.read())
                    spriteLocation = self.sfRoot + os.sep + hullData['spriteName']
                    if os.path.exists(spriteLocation):
                        icon = QtGui.QIcon(spriteLocation)
                        if ship['side'] == 'PLAYER':
                            listModel = playerListModel
                            playerCol += 1
                            col = playerCol
                        else:
                            listModel = enemyListModel
                            enemyCol += 1
                            col = enemyCol
                        listModel.setItem(0, col-1, QtGui.QStandardItem(icon, iconText))
                        listModel.setItem(1, col-1, QtGui.QStandardItem(ship['variant']))
        
        self.ui.playerShips.setModel(playerListModel)
        self.ui.playerShips.resizeRowsToContents()
        self.ui.playerShips.resizeColumnsToContents()
        
        self.ui.enemyShips.setModel(enemyListModel)
        self.ui.enemyShips.resizeRowsToContents()
        self.ui.enemyShips.resizeColumnsToContents()
        
        with open(missionPath + '\descriptor.json', 'r') as file:
            self.missionDescriptor = ast.literal_eval(file.read())
        
        with open(self.sfMissionList, 'r') as file:
            self.missionList = ast.literal_eval(file.read())
    
    def addShipCallback(self, player=True):
        if player:
            print "Add player ship"
        else:
            print "Add enemy ship"
    
    def removeShipCallback(self, player=True):
        if player:
            print "Remove player ship"
        else:
            print "Remove enemy ship"
    
    def quitCallback(self):
        self.Quit()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    sys.exit(app.exec_())