import datetime
import requests
from constants import BASE_URL
from utils import seconds_until, sleep_until

class Game:
    def __init__(self, game_data):
        self.game_data = game_data
        self.game_id = game_data.get("id")
        self.start_time_dt = (
            datetime.datetime.strptime(game_data.get("startTimeUTC"), "%Y-%m-%dT%H:%M:%S%z"))
        self.start_time_local = self.start_time_dt.astimezone()
        self.away_team = game_data.get("awayTeam").get("abbrev")
        self.home_team = game_data.get("homeTeam").get("abbrev")
        self.game_state = game_data.get("gameState")
        self.score = {}

    def update_score(self):
        url = f"{BASE_URL}/gamecenter/{self.game_id}/boxscore"
        response = requests.get(url).json()
        self.score = {
            "home": response.get("homeTeam").get("score"),
            "away": response.get("awayTeam").get("score")
        }
        self.game_state = response.get("gameState")

    def sleep_until_pregame(self):
        pre_game_time = self.start_time_local - datetime.timedelta(minutes=5)
        if seconds_until(pre_game_time) > 0:
            print(
                f"Sleeping until 5 minutes before game start at {pre_game_time} (in {seconds_until(pre_game_time):.0f} seconds).")
            sleep_until(pre_game_time)
        else:
            print("Less than 5 minutes remain before game start or game has already started; proceeding immediately.")

    def sleep_until_start(self):
        # Sleep until the exact game start time
        print(f"Waiting until game start at {self.start_time_dt} (in {seconds_until(self.start_time_dt):.0f} seconds).")
        sleep_until(self.start_time_local)
        print("Game has started! Tracking score...")