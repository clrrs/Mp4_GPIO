import time
import vlc
import os
import RPi.GPIO as GPIO

# install notes:
# connect to mp4museum via ssh user pi password mp4museum
# "sudo raspi-config" -> disable overlay filesystem, reboot
# put this file and your videos in /home/pi folder
# edit in the last parts of /home/pi/.bashrc:
# python3 /home/pi/mp4m-gpio.py > /tmp/mp4museum.log 2>&1

# then reboot and enjoy the interactive!


# Read audio device config (0=HDMI, 1=Headphones on this Pi)
# audiodevice = "0"
# if os.path.isfile("/boot/alsa.txt"):
#     with open("/boot/alsa.txt", "r") as f:
#         audiodevice = f.read(1)
audiodevice = "1"
# Audio: plughw: (not hw:) + one shared VLC Instance — reopening hw: each clip often crackles.
# Speaker-test clean but script crackly => VLC/ALSA path, not the analog jack.
# The "video broke" episode was NOT plughw: cmdline video=HDMI-A-2 moves the console to HDMI-2 while VLC/MMAL
# still draws on HDMI-1, so you see a blank/wrong port. Use HDMI-1 for this kiosk; keep cmdline without that video= line.
ALSA_CARD = "1"
HEADPHONE_LEVEL = 55
VLC_AUDIO_VOLUME = 70

# Optional MMAL HDMI port hint; usually ignored. Leave "" unless you verify with vlc -H.
MMAL_DISPLAY = ""


# --- Configuration ----------------------------------------------------

# Video files (must be in /home/pi next to this script)
ATTRACT_VIDEO = "AttractLoop.mp4"

# Using GPIO.BOARD numbering
# Hall sensors are active-low (trigger pulls input to GND)
SENSOR_PINS = {
    11: "video1.mp4",  # Sensor 1
    13: "video2.mp4",  # Sensor 2
    15: "video3.mp4",  # Sensor 3
    16: "video4.mp4",  # Sensor 4
    18: "video5.mp4",  # Sensor 5
}

DEBOUNCE_SECONDS = 0.5


# --- Global state -----------------------------------------------------

vlc_core = None
player = None
current_video = None
current_is_attract = False
current_sensor_pin = None

last_state = {pin: GPIO.HIGH for pin in SENSOR_PINS.keys()}  # pull-ups, idle high
last_trigger_time = {pin: 0.0 for pin in SENSOR_PINS.keys()}


def get_vlc_core():
    """One VLC Instance for the whole run — avoids reopening ALSA on every clip."""
    global vlc_core
    if vlc_core is None:
        prefix = ("--mmal-display " + MMAL_DISPLAY + " ") if MMAL_DISPLAY.strip() else ""
        vlc_core = vlc.Instance(
            prefix + "-q -A alsa --alsa-audio-device plughw:" + audiodevice
        )
    return vlc_core


def force_headphone_output():
    """Set bcm2835 Headphone mixer (see ALSA_CARD / HEADPHONE_LEVEL)."""
    try:
        os.system(
            "amixer -q -c "
            + ALSA_CARD
            + " cset name='Headphone' "
            + str(HEADPHONE_LEVEL)
            + "% >/dev/null 2>&1"
        )
    except Exception:
        pass


def start_video(source: str, is_attract: bool, sensor_pin=None):
    global player, current_video, current_is_attract, current_sensor_pin
    instance = get_vlc_core()
    if player is None:
        player = instance.media_player_new()
    else:
        try:
            player.stop()
        except Exception:
            pass

    media = instance.media_new(source)
    if is_attract:
        media.add_option(":input-repeat=-1")
    player.set_media(media)

    current_video = source
    current_is_attract = is_attract
    current_sensor_pin = sensor_pin

    player.play()
    time.sleep(0.35)
    player.audio_set_volume(VLC_AUDIO_VOLUME)


def ensure_attract_loop():
    if ATTRACT_VIDEO is None:
        return

    global player, current_video, current_is_attract, current_sensor_pin

    state = player.get_state() if player is not None else vlc.State.NothingSpecial

    if (
        player is None
        or not current_is_attract
        or state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error)
    ):
        start_video(ATTRACT_VIDEO, is_attract=True, sensor_pin=None)


def handle_sensor_trigger(pin):
    global player, current_video, current_is_attract, current_sensor_pin

    video = SENSOR_PINS.get(pin)
    if video is None:
        return

    state = player.get_state() if player is not None else vlc.State.NothingSpecial

    if (
        current_video == video
        and player is not None
        and state in (vlc.State.Playing, vlc.State.Paused)
    ):
        return

    start_video(video, is_attract=False, sensor_pin=pin)


def poll_sensors():
    now = time.time()

    for pin in SENSOR_PINS.keys():
        raw = GPIO.input(pin)
        prev = last_state[pin]

        # Hall sensors are active-low: magnet present pulls input to GND (LOW).
        active = raw == GPIO.LOW
        prev_active = prev == GPIO.LOW

        if active and not prev_active:
            if now - last_trigger_time[pin] >= DEBOUNCE_SECONDS:
                last_trigger_time[pin] = now
                handle_sensor_trigger(pin)

        last_state[pin] = raw


def main():
    # Force audio to the headphone jack once at startup
    force_headphone_output()

    GPIO.setmode(GPIO.BOARD)

    try:
        for pin in SENSOR_PINS.keys():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        ensure_attract_loop()

        while True:
            poll_sensors()

            state = player.get_state() if player is not None else vlc.State.NothingSpecial

            # After a sensor clip we return to attract; if attract repeat fails, state hits Ended while still "attract".
            if player is not None and state in (
                vlc.State.Ended,
                vlc.State.Stopped,
                vlc.State.Error,
            ):
                ensure_attract_loop()

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        try:
            if player is not None:
                player.stop()
        except Exception:
            pass
        GPIO.cleanup()


if __name__ == "__main__":
    main()

