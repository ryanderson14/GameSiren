import requests
import time
import datetime
from phue import Bridge
import json
import pygame
import threading


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


################ CONSTANTS #########################################

def seconds_until(target_time):
    """Return the number of seconds from now until the target_time. If the target time has already passed, return 0"""
    now = datetime.datetime.now().astimezone()
    delta = target_time - now
    return max(delta.total_seconds(), 0)


def sleep_until(target_time):
    """Sleep until the target_time is reached."""
    seconds = seconds_until(target_time)
    if seconds > 0:
        time.sleep(seconds)


def sleep_until_6am():
    current_dt = datetime.datetime.now().astimezone()
    # Determine next 6am. If current time is before 6am, use today; otherwise, tomorrow.
    if current_dt.hour < 6:
        next_6am = current_dt.replace(hour=6, minute=0, second=0, microsecond=0)
    else:
        next_6am = (current_dt + datetime.timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)

    sleep_time = (next_6am - current_dt).total_seconds()
    print(f"Sleeping until 6am (in {sleep_time:.0f} seconds).")
    time.sleep(sleep_time)


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


class Home:
    def __init__(self):
        self.bridge = Bridge(HUE_BRIDGE_IP)
        self.tv_light = 1
        self.stair_light = 2

    def trigger_lights_goal(self):
        light1 = self.tv_light
        light2 = self.stair_light
        self.bridge.connect()

        # Define settings for red and off states.
        # For a red color, hue=0, saturation=254, and brightness=254 is a common choice.
        red_settings = {"on": True, "hue": 0, "sat": 254, "bri": 254}
        off_settings = {"on": False}

        duration = 10  # Total duration in seconds for blinking
        blink_interval = 0.5  # Time in seconds between toggles

        start_time = time.time()
        toggle = True  # Used to alternate which light is red

        while time.time() - start_time < duration:
            if toggle:
                # Set LIGHT_ID1 to red, LIGHT_ID2 off.
                self.bridge.set_light(light1, red_settings)
                self.bridge.set_light(light2, off_settings)
            else:
                # Set LIGHT_ID1 off, LIGHT_ID2 to red.
                self.bridge.set_light(light1, off_settings)
                self.bridge.set_light(light2, red_settings)
            toggle = not toggle
            time.sleep(blink_interval)

        # Ensure both lights are turned off at the end.
        self.bridge.set_light(light1, off_settings)
        self.bridge.set_light(light2, off_settings)

    def trigger_lights_startup(self):
        light1 = self.tv_light
        light2 = self.stair_light
        self.bridge.connect()

        duration = 10  # Total duration in seconds for the pulsing effect
        num_cycles = 3  # Number of fade in/out cycles (pulse cycles)
        max_brightness = 254
        start_time = time.time()
        cycle_duration = duration / num_cycles  # Duration of one complete cycle (fade in + fade out)

        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            # Determine the position within the current cycle
            cycle_elapsed = elapsed % cycle_duration

            # For the first half of the cycle, fade in; for the second half, fade out.
            if cycle_elapsed < cycle_duration / 2:
                brightness = int(max_brightness * (cycle_elapsed / (cycle_duration / 2)))
            else:
                brightness = int(max_brightness * ((cycle_duration - cycle_elapsed) / (cycle_duration / 2)))

            blue_settings = {
                "on": True,
                "hue": 46920,  # Blue hue value
                "sat": 254,
                "bri": brightness
            }
            self.bridge.set_light(light1, blue_settings)
            self.bridge.set_light(light2, blue_settings)

            # Update at a short interval for smooth dimming.
            time.sleep(0.1)

        # Ensure both lights are turned off at the end.
        off_settings = {"on": False}
        self.bridge.set_light(light1, off_settings)
        self.bridge.set_light(light2, off_settings)

    def trigger_lights_pregame(self):
        light1 = self.tv_light
        light2 = self.stair_light
        self.bridge.connect()

        # Define the color settings for red, white, and blue.
        # Red: typical red color.
        red_settings = {"on": True, "hue": 0, "sat": 254, "bri": 254}
        # White: no saturation gives white; brightness at maximum.
        white_settings = {"on": True, "sat": 0, "bri": 254}
        # Blue: using a hue value that approximates a deep blue.
        blue_settings = {"on": True, "hue": 46920, "sat": 254, "bri": 254}
        # Off settings to ensure the light is turned off.
        off_settings = {"on": False}

        duration = 10  # Total duration of the sequence in seconds.
        flash_on_time = 0.3  # Duration (in seconds) that each color is displayed.
        flash_off_time = 0.1  # Brief pause between flashes.

        start_time = time.time()
        color_cycle = [red_settings, white_settings, blue_settings]

        # Loop through the color cycle until the total duration elapses.
        while time.time() - start_time < duration:
            for color in color_cycle:
                # Check if there's enough time left; if not, exit early.
                if time.time() - start_time + flash_on_time + flash_off_time > duration:
                    break
                # Set both lights to the current color.
                self.bridge.set_light(light1, color)
                self.bridge.set_light(light2, color)
                time.sleep(flash_on_time)

                # Turn the lights off briefly before the next flash.
                self.bridge.set_light(light1, off_settings)
                self.bridge.set_light(light2, off_settings)
                time.sleep(flash_off_time)

        # Ensure both lights are turned off at the end of the sequence.
        self.bridge.set_light(light1, off_settings)
        self.bridge.set_light(light2, off_settings)


class Audio:
    def __init__(self):
        self.goal_horn_mp3 = f"../sounds/{GOAL_SOUND}"
        self.startup_mp3 = f"../sounds/{STARTUP_SOUND}"
        self.pregame_mp3 = f"../sounds/{PREGAME_SOUND}"

    def play_goal_horn(self):
        self.play_mp3(self.goal_horn_mp3)

    def play_startup_sound(self):
        self.play_mp3(self.startup_mp3)

    def play_pregame_sound(self):
        self.play_mp3(self.pregame_mp3)

    def play_mp3(self, file_name):
        pygame.mixer.init()
        pygame.mixer.music.load(file_name)
        pygame.mixer.music.play()
        # Keep the program running until the music stops
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)


def goal_scored(home, audio):
    light_thread = threading.Thread(target=home.trigger_lights_goal)
    audio_thread = threading.Thread(target=audio.play_goal_horn)

    light_thread.start()
    audio_thread.start()

    light_thread.join()
    audio_thread.join()


def pregame_event(home, audio):
    light_thread = threading.Thread(target=home.trigger_lights_pregame)
    audio_thread = threading.Thread(target=audio.play_pregame_sound())

    light_thread.start()
    audio_thread.start()

    light_thread.join()
    audio_thread.join()




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
    # my_home = Home()
    # audio = Audio()
    # goal_scored(my_home, audio)



