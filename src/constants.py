import json

################ CONSTANTS #########################################
config =                json.load(open('../config.json'))
HUE_BRIDGE_IP =         config.get("HUE_BRIDGE_IP")
BASE_URL =              config.get("API_URL")
TEAM =                  config.get("TEAM")
BOXSCORE_ENDPOINT =     config.get("BOXSCORE_ENDPOINT")
LIVE_DELAY =            config.get("LIVE_DELAY")
GOAL_SOUND =            config.get("GOAL_SOUND")
STARTUP_SOUND =         config.get("STARTUP_SOUND")
PREGAME_SOUND =         config.get("PREGAME_SOUND")