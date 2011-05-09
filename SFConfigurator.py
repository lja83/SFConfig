import os
import re
import sys
import ast
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
        
        self.connect(self.ui.addEnemyShipButton, QtCore.SIGNAL('clicked()'), lambda: self.addShipCallback(False))
        self.connect(self.ui.removeEnemyShipButton, QtCore.SIGNAL('clicked()'), lambda: self.removeShipCallback(False))
        
        self.init_data(STARFARER_ROOT)
    
    def init_data(self, sfRoot):
        self.sfRoot = sfRoot
        self.sfData = self.sfRoot + r'\data'
        self.sfMissions = self.sfData + r'\missions'
        self.sfMissionList = self.sfMissions + r'\mission_list.json'
        self.sfHulls = self.sfData + r'\hulls'
        self.sfVariants = self.sfData + r'\variants'
        self.sfFighters = self.sfVariants + r'\fighters'
        
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
                            'important': groups[5]
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
        
        self.ui.playerShips.setModel(self.playerListModel)
        self.ui.enemyShips.setModel(self.enemyListModel)
        
        for listModel in (self.playerListModel, self.enemyListModel):
            listModel.setVerticalHeaderItem(0, QtGui.QStandardItem("Ship"))
            listModel.setVerticalHeaderItem(1, QtGui.QStandardItem("Variant"))
            listModel.setVerticalHeaderItem(2, QtGui.QStandardItem("Name"))
        
        playerCol = 0
        enemyCol = 0
        for ship in missionShips:
            if ship['type'] == 'SHIP':
                variant = self.allShips[ship['variant']]
                iconText = ''
            else:
                variantName = self.wingData[ship['variant']]['variant']
                variant = self.allWings[variantName]
                iconText = "x%s" % self.wingData[ship['variant']]['num']
            
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
        
        self.ui.playerShips.resizeRowsToContents()
        self.ui.playerShips.resizeColumnsToContents()
        self.ui.enemyShips.resizeRowsToContents()
        self.ui.enemyShips.resizeColumnsToContents()
    
    def makeShipLines(self, fleets, side='PLAYER', indent = '        '):
        lines = []
        lineWithoutName = indent + 'api.addToFleet(FleetSide.%(side)s, "%(variant)s", FleetMemberType.%(type)s, %(important)s);'
        lineWithName    = indent + 'api.addToFleet(FleetSide.%(side)s, "%(variant)s", FleetMemberType.%(type)s, "%(name)s", %(important)s);'
        for ship in fleets:
            if ship['side'] == side:
                lines.append((lineWithName if ship['name'] else lineWithoutName) % ship)
        return '\n'.join(lines)
    
    def makeBreifingLines(self, objectives, indent = '        '):
        return '\n'.join([indent + 'api.addBriefingItem("' + objective + '");' for objective in objectives])
    
    def saveMissionCallback(self):
        missionData = self.missionData
        
        indent = '        '
        packageName = str(self.ui.missionNameEdit.text())
        packageName = packageName.lower().replace(' ', '')
        replaceText = {
            'package_name': packageName,
            'briefing': self.makeBreifingLines(missionData['objectives'], indent),
            'player_fleet': self.makeShipLines(missionData['fleets'], 'PLAYER', indent),
            'enemy_fleet': self.makeShipLines(missionData['fleets'], 'ENEMY', indent),
        }
        newFile = template % replaceText
        
        print newFile
    
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

template = """
package data.missions.%(package_name)s

import com.fs.starfarer.api.combat.BattleObjectiveAPI;
import com.fs.starfarer.api.fleet.FleetGoal;
import com.fs.starfarer.api.fleet.FleetMemberType;
import com.fs.starfarer.api.mission.FleetSide;
import com.fs.starfarer.api.mission.MissionDefinitionAPI;
import com.fs.starfarer.api.mission.MissionDefinitionPlugin;

public class MissionDefinition implements MissionDefinitionPlugin {

    public void defineMission(MissionDefinitionAPI api) {

        // Set up the fleets so we can add ships and fighter wings to them.
        // In this scenario, the fleets are attacking each other, but
        // in other scenarios, a fleet may be defending or trying to escape
        api.initFleet(FleetSide.PLAYER, "ISS", FleetGoal.ATTACK, false);
        api.initFleet(FleetSide.ENEMY, "", FleetGoal.ATTACK, true);

        // Set a small blurb for each fleet that shows up on the mission detail and
        // mission results screens to identify each side.
        api.setFleetTagline(FleetSide.PLAYER, "ISS Hamatsu and ISS Black Star with drone escort");
        api.setFleetTagline(FleetSide.ENEMY, "Suspected Cult of Lud forces");
        
%(briefing)s
        
%(player_fleet)s
        
%(enemy_fleet)s
        
        // Set up the map.
        // 12000x8000 is actually somewhat small, making for a faster-paced mission.
        float width = 12000f;
        float height = 8000f;
        api.initMap((float)-width/2f, (float)width/2f, (float)-height/2f, (float)height/2f);
        
        float minX = -width/2;
        float minY = -height/2;
        
        // All the addXXX methods take a pair of coordinates followed by data for
        // whatever object is being added.
        
        // Add two big nebula clouds
        api.addNebula(minX + width * 0.75f, minY + height * 0.5f, 2000);
        api.addNebula(minX + width * 0.25f, minY + height * 0.5f, 1000);
        
        // And a few random ones to spice up the playing field.
        // A similar approach can be used to randomize everything
        // else, including fleet composition.
        for (int i = 0; i < 5; i++) {
            float x = (float) Math.random() * width - width/2;
            float y = (float) Math.random() * height - height/2;
            float radius = 100f + (float) Math.random() * 400f; 
            api.addNebula(x, y, radius);
        }
        
        // Add objectives. These can be captured by each side
        // and provide stat bonuses and extra command points to
        // bring in reinforcements.
        // Reinforcements only matter for large fleets - in this
        // case, assuming a 100 command point battle size,
        // both fleets will be able to deploy fully right away.
        api.addObjective(minX + width * 0.75f, minY + height * 0.5f, 
                         "sensor_array", BattleObjectiveAPI.Importance.NORMAL);
        api.addObjective(minX + width * 0.25f, minY + height * 0.5f, 
                         "nav_buoy", BattleObjectiveAPI.Importance.NORMAL);
        
        // Add an asteroid field going diagonally across the
        // battlefield, 2000 pixels wide, with a maximum of 
        // 100 asteroids in it.
        // 20-70 is the range of asteroid speeds.
        api.addAsteroidField(minY, minY, 45, 2000f,
                                20f, 70f, 100);
        
        // Add some planets.  These are defined in data/config/planets.json.
        api.addPlanet(minX + width * 0.2f, minY + height * 0.8f, 320f, "star_yellow", 300f);
        api.addPlanet(minX + width * 0.8f, minY + height * 0.8f, 256f, "desert", 250f);
        api.addPlanet(minX + width * 0.55f, minY + height * 0.25f, 200f, "cryovolcanic", 200f);
    }

}
"""

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myapp = MainWindow()
    sys.exit(app.exec_())
