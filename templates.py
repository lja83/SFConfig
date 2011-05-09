missionDefinition = """\
package data.missions.%(package_name)s;

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