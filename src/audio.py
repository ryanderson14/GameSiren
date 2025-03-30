from constants import GOAL_SOUND, STARTUP_SOUND, PREGAME_SOUND
import pygame

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