from phue import Bridge
import time
import json

config =                json.load(open('../config.json'))
HUE_BRIDGE_IP =         config.get("HUE_BRIDGE_IP")

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


def trigger_lights():
    home = Home()
    home.trigger_lights_goal()
