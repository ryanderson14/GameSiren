import threading

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


