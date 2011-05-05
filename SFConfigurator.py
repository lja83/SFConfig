import re
import sys
import ast
from PyQt4 import QtCore, QtGui, uic

STARFARER_ROOT = r'C:\Program Files (x86)\Fractal Softworks\Starfarer'
STARFARER_DATA = STARFARER_ROOT + r'\starfarer-all\data'
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
        
        self.playerShipModel = QtGui.QStringListModel()
        playerShipList = QtCore.QStringList()
        
        self.enemyShipModel = QtGui.QStringListModel()
        enemyShipList = QtCore.QStringList()
        
        
        for ship in self.ships:
            if ship['side'] == 'PLAYER':
                playerShipList << ship['variant']
            else:
                enemyShipList << ship['variant']
        
        self.playerShipModel.setStringList(playerShipList)
        self.ui.playerShips.setModel(self.playerShipModel)
        
        self.enemyShipModel.setStringList(enemyShipList)
        self.ui.enemyShips.setModel(self.enemyShipModel)
        
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