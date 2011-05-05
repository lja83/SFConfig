import re
import sys
import json
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
        
        playerShips = []
        enemyShips = []
        
        with open(missionPath + '\MissionDefinition.java', 'r') as file:
            for line in file.readlines():
                line = line.split('//')[0].strip()
                if 'api.addToFleet' in line:
                    if 'FleetSide.PLAYER' in line:
                        playerShips.append(line)
                    else:
                        enemyShips.append(line)
        
        with open(missionPath + '\descriptor.json') as file:
            descriptor = json.load(file)
        
        print 'Player Ships'
        for i in playerShips:
            print i
        print
        
        print 'Enemy Ships'
        for i in enemyShips:
            print i
        print
        
        print descriptor
    
    
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