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
    
    def loadMissionCallback(self):
        missionPath = filename=QtGui.QFileDialog.getExistingDirectory(self, 'Select Mission Directory', STARFARER_MISSIONS)
        print missionPath
        print STARFARER_MISSIONS_LIST
        
        self.ships = []
        
        with open(missionPath + '\MissionDefinition.java', 'r') as file:
            for line in file.readlines():
                line = line.split('//')[0].strip()
                if 'api.addToFleet' in line:
                    # Find all the lines that add ships to the battle
                    matchPattern = r'api\.addToFleet *?\( *?FleetSide\.(.+?) *?, *?"(.+?)" *?, *?FleetMemberType\.(.+?) *?,( *?"(.+?) *?,)? *? ?(.+?) *?\) *?;'
                    line = re.match(matchPattern, line)
                    if line != None:
                        groups = line.groups()
                        self.ships.append({
                            'side':      groups[0],
                            'variant':   groups[1],
                            'type':      groups[2],
                            'name':      groups[4],
                            'important': groups[5]
                        })
        
#        listModel = QtGui.QStandardItemModel()
#        icon = QtGui.QIcon(r'C:\Program Files (x86)\Fractal Softworks\Starfarer\starfarer-all\graphics\ships\astral_cv.png')
#        listModel.setItem(0, 0, QtGui.QStandardItem(icon, ""))
        
#        self.ui.playerShips.setModel(listModel)
#        self.ui.playerShips.resizeRowsToContents()
#        self.ui.playerShips.resizeColumnsToContents()
        
        
        listModel = QtGui.QStandardItemModel()
        col = 0
        for ship in self.ships:
            if ship['side'] == 'PLAYER':
                variantLocation = STARFARER_DATA + '\\variants\\' + ship['variant'] + '.variant'
                if os.path.exists(variantLocation):
                    with open(variantLocation, 'r') as f:
                        variantData = ast.literal_eval(f.read())
                    hullLocation = STARFARER_DATA + '\\hulls\\' + variantData['hullId'] + '.ship'
                    if os.path.exists(hullLocation):
                        with open(hullLocation, 'r') as f:
                            hullData = ast.literal_eval(f.read())
                        spriteLocation = STARFARER_ROOT + os.sep + hullData['spriteName']
                        if os.path.exists(spriteLocation):
                            icon = QtGui.QIcon(spriteLocation)
                            listModel.setItem(0, col, QtGui.QStandardItem(icon, ""))
                            listModel.setItem(1, col, QtGui.QStandardItem(ship['variant']))
                            col += 1
        self.ui.playerShips.setModel(listModel)
        self.ui.playerShips.resizeRowsToContents()
        self.ui.playerShips.resizeColumnsToContents()
        
        with open(missionPath + '\descriptor.json', 'r') as file:
            self.missionDescriptor = ast.literal_eval(file.read())
        
        with open(STARFARER_MISSIONS_LIST, 'r') as file:
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