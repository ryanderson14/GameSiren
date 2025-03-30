import datetime
import requests
from constants import BASE_URL
from game import Game

class Schedule:
    def __init__(self):

        today = datetime.date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/schedule/{formatted_date}")
        self.games = [Game(game) for game in response.json().get("gameWeek")[0]["games"]]

    def team_game_today(self, team):
        """
        Check if a team is on the schedule for today. If it is listed as any home or away team, return that
        Game object. If it is not, return None.
        :param team: Three letter indicator of team (e.g. WSH)
        :return: Game or None
        """
        for game in self.games:
            if game.away_team == team or game.home_team == team:
                return game
        return None
