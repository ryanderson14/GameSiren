import time
from environment import Home
from audio import Audio
from schedule import Schedule
from constants import *
from utils import sleep_until_6am
from events import pregame_event, goal_scored


def main():

    my_home = Home()
    audio = Audio()
    my_home.trigger_lights_startup()
    audio.play_startup_sound()

    # Continuous loop
    while True:

        # Check if your team plays today
        schedule = Schedule()
        game = schedule.team_game_today(TEAM)

        if not game:
            print(f"No game found today for team {TEAM}.")
            sleep_until_6am()
            continue
        print(f"Found game for team {TEAM} (Game ID: {game.game_id}) scheduled to start at {game.start_time_dt}.")

        # Wait until 5 minutes before the game starts
        game.sleep_until_pregame()

        # Game starting in 5 minutes
        pregame_event(my_home, audio)
        game.sleep_until_start()

        # Game starting, start tracking score
        prev_team_score = 0
        home_team = True if TEAM == game.home_team else False

        while game.game_state not in ['OFF', 'FINAL']:
            game.update_score()
            current_team_score = game.score.get("home", 0) if home_team else game.score.get("away", 0)
            if current_team_score > prev_team_score:
                if LIVE_DELAY > 0:
                    time.sleep(LIVE_DELAY)
                goal_scored(my_home, audio)
                prev_team_score = current_team_score
            print(f"{game.away_team} {game.score.get('away')} - {game.home_team} {game.score.get('home')} | Status: {game.game_state}")
            time.sleep(1)

        print("Game is over. Waiting until next day at 6am.")
        sleep_until_6am()


if __name__ == "__main__":
    main()




