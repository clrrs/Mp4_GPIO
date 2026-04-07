# Pi mp4 museum -- Installation Cheat Sheet

Interactive video kiosk: 5 hall-effect sensors trigger 5 videos via VLC on a Raspberry Pi. An attract-loop video plays when idle.

**Prerequisites**: Raspberry Pi (3/4/5) running Raspberry Pi OS, user `pi`, password `mp4museum`, HDMI display + keyboard/mouse for first boot, Ethernet cable or Wi-Fi network available.

---

## Commands

| Category | Command | What it does | When to use |
|---|---|---|---|
| **System** | `sudo raspi-config` | Interactive config tool | Enable SSH, set Wi-Fi, disable overlay FS |
| | `sudo reboot` | Restart the Pi | After config changes |
| | `sudo poweroff` | Shut down safely | Before unplugging power |
| | `whoami` | Show current user | Confirm you're `pi` |
| | `uname -a` | Show OS / kernel info | Identify Pi model and OS version |
| | `df -h` | Disk usage | Check if SD card is full |
| | `free -h` | RAM usage | Check available memory |
| | `vcgencmd measure_temp` | CPU temperature | If Pi feels hot or is throttling |
| | `uptime` | Time since last boot | Confirm a reboot actually happened |
| | `sudo mount -o remount,rw /` | Remount root filesystem as read-write | If overlay FS is on or FS is read-only |
| | `sudo mount -o remount,rw /boot` | Remount boot partition as read-write | If you need to edit `/boot/config.txt` while overlay FS is on |
| **Networking** | `hostname -I` | Show Pi's IP address(es) | Find IP for SSH |
| | `ip a` | Detailed network interfaces | See Ethernet (eth0) and Wi-Fi (wlan0) status |
| | `iwconfig` | Wi-Fi connection details | Check signal strength, SSID |
| | `ping -c 3 google.com` | Test internet connectivity | Verify the Pi is online |
| | `ping -c 3 <IP>` | Ping another device | Test link between laptop and Pi |
| | `sudo systemctl restart dhcpcd` | Restart DHCP client | If Pi didn't get an IP after plugging in |
| | `rfkill list` | Show wireless block status | Check if Wi-Fi/Bluetooth is soft-blocked |
| | `sudo rfkill unblock wifi` | Remove Wi-Fi soft block | If Wi-Fi is disabled and won't connect |
| | `cat /etc/wpa_supplicant/wpa_supplicant.conf` | Show saved Wi-Fi config | Verify SSID / password are correct |
| **SSH** | `sudo systemctl enable ssh` | Enable SSH on boot | One-time setup on the Pi |
| | `sudo systemctl start ssh` | Start SSH right now | If SSH isn't running yet |
| | `sudo systemctl status ssh` | Check SSH service status | Verify SSH is active |
| | `ssh pi@raspberrypi.local` | Connect from laptop (mDNS) | Easiest way -- works on Mac / most Linux |
| | `ssh pi@<IP>` | Connect from laptop (by IP) | If `.local` doesn't resolve |
| | `scp file.mp4 pi@<IP>:/home/pi/` | Copy file to Pi | Transfer videos from laptop |
| | `scp pi@<IP>:/tmp/mp4museum.log .` | Copy log from Pi | Pull log to laptop for review |
| **Files & Logs** | `cd /home/pi` | Go to project folder | All project files live here |
| | `ls -la *.mp4` | List video files | Verify all 6 videos are present |
| | `ls -la mp4m-gpio.py` | Check script exists | Confirm script is deployed |
| | `tail -f /tmp/mp4museum.log` | Follow log in real time | Watch script output live |
| | `tail -n 50 /tmp/mp4museum.log` | Last 50 lines of log | Quick check for recent errors |
| | `cat /tmp/mp4museum.log` | Full log | Deep-dive into errors |
| | `rm /tmp/mp4museum.log` | Delete log | Clear old log before a fresh run |
| | `nano /home/pi/.bashrc` | Edit autostart config | Add or remove the auto-run line |
| | `cat /home/pi/.bashrc` | View autostart config | Check if auto-run line is present |
| **Python & Process** | `python3 /home/pi/mp4m-gpio.py` | Run script manually | Test interactively (see errors in terminal) |
| | `python3 mp4m-gpio.py > /tmp/mp4museum.log 2>&1 &` | Run script in background | Manual background start |
| | `ps aux \| grep mp4m-gpio` | Find running script | Check if the script is alive |
| | `pkill -f mp4m-gpio.py` | Kill the script | Stop it before re-running |
| | `kill <PID>` | Kill a specific process | Use PID from `ps aux` output |
| | `pip3 install python-vlc` | Install VLC Python bindings | If `import vlc` fails |
| | `pip3 install RPi.GPIO` | Install GPIO library | If `import RPi.GPIO` fails |
| | `python3 -c "import vlc; print(vlc.__version__)"` | Test VLC import | Quick sanity check |
| **GPIO & Sensors** | `pinout` | Show Pi pinout diagram | Identify physical pin locations |
| | `gpio readall` | Show all pin states (if wiringPi installed) | Visual pin map |
| **VLC & Audio** | `cvlc --play-and-exit AttractLoop.mp4` | Play a video from CLI | Test video output without the script |
| | `echo 0 | sudo tee /boot/alsa.txt` | Set script audio target to HDMI | Use when testing/using HDMI audio |
| | `echo 1 | sudo tee /boot/alsa.txt` | Set script audio target to aux/headphone jack | Switch back to analog output |
| | `amixer -c 1 cset name='Headphone' 100%` | Set headphone volume to max | Script does this, but useful manually |
| | `amixer` | Show mixer controls | See available audio devices |
| | `aplay -l` | List audio playback devices | Identify card numbers (0=HDMI, 1=headphone) |
| | `cat /proc/asound/cards` | Short names for each card | Match `CARD=…` in ALSA device strings |
| | `speaker-test -D plughw:N,0 -c 2 -t wav` | Test **USB DAC** (replace **N** with card #) | After `aplay -l` shows the DAC |
| | `cvlc -q -A alsa --alsa-audio-device plughw:N /home/pi/video1.mp4` | VLC test: video + **USB** audio | Same **N** as above |
| | `speaker-test -c 2 -t wav` | Play test sound | Default ALSA device (onboard) |
| | `alsamixer` | Interactive volume control (TUI) | Adjust levels visually |
| | `sudo alsactl store` | Save current mixer levels permanently | Persist volume changes across reboots |
| | `tvservice -s` | Show current HDMI display mode | Check resolution and refresh rate |
| **Boot & Config** | `sudo nano /boot/config.txt` | Edit boot config | Change HDMI/audio/GPU settings |
| | `cat /boot/config.txt` | View boot config | Check current settings |
| | `dmesg \| tail -30` | Recent kernel messages | Hardware errors after boot |
| | `journalctl -b --no-pager \| tail -50` | Boot log | Diagnose boot-time failures |

---

## SSH Connection

### Step 1: Enable SSH on the Pi (one-time, on-screen)

1. Open a terminal on the Pi (or use the desktop menu)
2. Run `sudo raspi-config`
3. Navigate: **Interface Options** -> **SSH** -> **Yes**
4. Back out and finish
5. Optionally change the password: **System Options** -> **Password**

### Step 2a: Connect via Ethernet

1. Plug an Ethernet cable between the Pi and your router/switch
2. On the Pi, run `hostname -I` -- note the IP (e.g. `192.168.1.42`)
3. From your laptop:

```bash
ssh pi@raspberrypi.local
# or, if .local doesn't work:
ssh pi@192.168.1.42
```

Password: `mp4museum` (default)

### Step 2b: Connect via Wi-Fi

1. On the Pi, run `sudo raspi-config`
2. Navigate: **System Options** -> **Wireless LAN**
3. Enter your Wi-Fi SSID and password
4. Back out and finish, then run `hostname -I` to get the IP
5. From your laptop:

```bash
ssh pi@raspberrypi.local
# or by IP:
ssh pi@<WIFI_IP>
```

### Finding the Pi's IP (multiple methods)

| Method | Where to run | Command / action |
|---|---|---|
| On the Pi itself | Pi terminal | `hostname -I` |
| mDNS / Bonjour | Laptop (Mac/Linux) | `ping raspberrypi.local` |
| Router admin page | Laptop browser | Check connected devices list for `raspberrypi` |
| Network scan | Laptop terminal | `nmap -sn 192.168.1.0/24` (adjust subnet) |
| ARP table | Laptop terminal | `arp -a \| grep raspberry` |

> **Security**: Change the default password (`passwd`) once everything works.

---

## Project Setup (First-Time Only)

Use these steps **once per new SD card / Pi image** to get the mp4museum GPIO build running.  
For **day-to-day use**, you should normally just plug in the Pi and let it boot.

1. **SSH in** or use the Pi's keyboard/display.
2. **Disable overlay filesystem** (so the SD card is writable):

```bash
sudo raspi-config
# Advanced Options -> Overlay FS -> No -> Reboot
```

3. **Copy files** to `/home/pi` (one time):
   - `mp4m-gpio.py`
   - `AttractLoop.mp4`
   - `video1.mp4` through `video5.mp4`

4. **Edit `/boot/config.txt`** if needed (display/audio settings). Don't replace the whole file -- merge settings from this project's `config.txt` into the existing one on the Pi.

5. **Edit `/home/pi/.bashrc`** -- comment out the stock player and add our script:

```bash
# comment out the stock mp4museum player:
# python3 /boot/mp4museum.py > /tmp/mp4museum.log 2>&1

# add our GPIO script instead:
python3 /home/pi/mp4m-gpio.py > /tmp/mp4museum.log 2>&1
```

6. **Reboot**: `sudo reboot`

> **Power-cut warning**: With overlay FS disabled, the SD card is writable and vulnerable to corruption on hard power loss. Always `sudo poweroff` before pulling the plug. Re-enable overlay FS via `raspi-config` once everything is tested and stable.

### How it works

- On boot, the `pi` user auto-logs in -> `.bashrc` runs -> script starts
- **Attract loop**: `AttractLoop.mp4` plays on repeat when no sensor is triggered
- **Sensor trigger**: A magnet near a hall sensor pulls GPIO LOW -> the matching video plays once -> attract loop resumes
- **Audio**: Select output in `/boot/alsa.txt` (`0` = HDMI, `1` = headphone jack). If missing/invalid, script defaults to `1` (headphone) for safety.
- **Headphone gain tweak**: `amixer -c 1 cset name='Headphone' ...` is only applied when `/boot/alsa.txt` is set to `1`.

### Pin -> Video mapping

| Sensor | BOARD pin | BCM GPIO | Video |
|---|---|---|---|
| 1 | 11 | GPIO17 | `video1.mp4` |
| 2 | 13 | GPIO27 | `video2.mp4` |
| 3 | 15 | GPIO22 | `video3.mp4` |
| 4 | 16 | GPIO23 | `video4.mp4` |
| 5 | 18 | GPIO24 | `video5.mp4` |

All sensors share 3.3V (e.g. pin 1) and GND (e.g. pin 6). No external resistors needed -- internal pull-ups are enabled by the script.

---

## USB DAC (KT USB Audio / Ugreen-class)

Use this section when making the **USB DAC the default** output for VLC / `mp4m-gpio.py`.

### Hardware identity

| Topic | Detail |
|--------|--------|
| **Physical** | Cheap class-compliant USB DAC (e.g. Ugreen); often rebadged silicon. |
| **`lsusb`** | May show **`12d1:0010` Huawei Technologies** — misleading **USB vendor ID reuse** by the OEM. |
| **`dmesg` (on plug-in)** | Look for **`Product: KT USB Audio`**, **`Manufacturer: KTMicro`**, and `snd-usb-audio`. |
| **ALSA** | `aplay -l` / `cat /proc/asound/cards` — e.g. **card `2`**, short name **`Audio`**, long name **`KT USB Audio`**. |
| **Card number** | Not fixed forever: if you add/remove USB devices, **re-check** `aplay -l`. |

### VLC / script ALSA strings

- Prefer **`plughw:N`** (or `plughw:N,0`) — **not** `hw:` — so sample format/rate conversion works.
- Example when the DAC is **card 2**: `--alsa-audio-device plughw:2`
- Alternative by name: `sysdefault:CARD=Audio` (if short name stays `Audio`).

### Quick test (Pi)

```bash
aplay -l
speaker-test -D plughw:2,0 -c 2 -t wav
cvlc -q -A alsa --alsa-audio-device plughw:2 /home/pi/video1.mp4
```

Replace **`2`** with whatever **`aplay -l`** reports for the USB device.

### Notes

- **Power**: Prefer a **direct Pi USB port**; if the dongle resets or drops, try a **powered** hub.
- **VLC may log** `device cannot be paused` on some USB DACs — usually **harmless**.
- **Incorporating into `mp4m-gpio.py`**: `/boot/alsa.txt` currently only supports **`0`** (HDMI) and **`1`** (headphone). For USB you will need to **extend** that file (e.g. **`2`**) and pass **`plughw:<n>`** to VLC, **or** set a default PCM device in **`~/.asoundrc`** / **`/etc/asound.conf`** for the USB card (watch for **card order** if multiple USB gadgets appear).

---

## Debugging

### Script not running / no video on boot

- **Check if it's running**: `ps aux | grep mp4m-gpio`
- **Check the log**: `tail -n 50 /tmp/mp4museum.log`
- **Check .bashrc has the line**: `grep mp4m /home/pi/.bashrc`
- **Run manually to see errors**:

```bash
pkill -f mp4m-gpio.py          # kill any existing instance
python3 /home/pi/mp4m-gpio.py  # run in foreground, errors print to terminal
```

- **Temporarily disable autostart**: comment out the line in `.bashrc` with `#`, reboot, then run manually

### Sensors not triggering

- **Run the test script** (from `gpio-wiring.md`):

```bash
python3 -c "
import time, RPi.GPIO as GPIO
PINS = [11, 13, 15, 16, 18]
GPIO.setmode(GPIO.BOARD)
for p in PINS: GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try:
    while True:
        states = [GPIO.input(p) for p in PINS]
        print('States (LOW=magnet):', states)
        time.sleep(0.2)
except KeyboardInterrupt: pass
finally: GPIO.cleanup()
"
```

- **Expected output**: All `1`s at rest. A pin reads `0` when its magnet is near.
- **All zeros?** Sensor VCC/GND may be swapped, or OUT is shorted to GND.
- **Always 1 even with magnet?** Magnet is too far, wrong polarity, or wire is disconnected.
- **Quick hardware test**: Touch a jumper wire from a sensor GPIO pin directly to GND -- this simulates a sensor trigger without needing magnets.
- **Sensor plays video at boot (stuck active)?** The sensor polarity may be inverted. In `poll_sensors()`, swap `GPIO.LOW` to `GPIO.HIGH` (or vice versa). Use the test script above to confirm idle vs active states first.
- **Double-check wiring** against the pin table above. Remember: the script uses **BOARD** (physical header) numbering, not BCM.

### Video / VLC issues

- **Test a video manually**:

```bash
cvlc --play-and-exit /home/pi/AttractLoop.mp4
```

- **No video on screen?** Check HDMI cable, try `hdmi_force_hotplug=1` in `/boot/config.txt`
- **Wrong video plays**: Verify filenames match `SENSOR_PINS` in the script (`ls -la /home/pi/*.mp4`)
- **Video stutters**: Check `gpu_mem=128` is set in `/boot/config.txt`, check CPU temp with `vcgencmd measure_temp`

### Audio issues

- **Current recommendation**: HDMI audio is working well on this build. Set `/boot/alsa.txt` to `0` for HDMI.
- **No sound from selected output**:
  - Confirm current mode: `cat /boot/alsa.txt` (`0` = HDMI, `1` = headphone)
  - Switch mode if needed:
    - HDMI: `echo 0 | sudo tee /boot/alsa.txt`
    - Headphone: `echo 1 | sudo tee /boot/alsa.txt`
  - Restart script (or reboot) after changing mode
- **No sound from headphone jack (mode `1`)**:
  - Run `amixer -c 1 cset name='Headphone' 100%` manually
  - Test with `speaker-test -c 2 -t wav`
  - Check `aplay -l` -- card 1 should be `bcm2835 Headphones`
  - Note: `amixer cset numid=3 1` does NOT work on Pi 4. Always use `-c 1 cset name='Headphone'`.
- **No sound from HDMI (mode `0`)**:
  - Ensure display is on HDMI-1 (kiosk path)
  - If needed, uncomment `hdmi_drive=2` in `/boot/config.txt`, then reboot
- **Crackly / popping audio?** Try these in order:
  1. Lower volume slightly: `amixer -c 1 cset name='Headphone' 90%`
  2. Create `/etc/asound.conf` with buffer tuning:

```
defaults.ctl.card 1
defaults.pcm.card 1
defaults.pcm.period_time 500
defaults.pcm.buffer_time 4000
```

  3. Check physical connections -- bad ground or cheap cable can cause noise
- **Want to switch outputs quickly?** Edit only `/boot/alsa.txt` (`0` HDMI / `1` headphone), then restart the script
- **No audio at all**: Check `dtparam=audio=on` is in `/boot/config.txt`
- **Save volume changes permanently**: `sudo alsactl store`

#### Field notes: confirmed on current Pi

- HDMI audio path is currently stable and is the preferred output mode for testing.
- `alsamixer -c 1` **does** change volume while video is running.
- `vcgencmd get_throttled` is consistently `0x0` (no thermal/undervoltage throttling).
- On the analog headphone path, audio-only playback is clean but artifacts can appear when video+audio run together.
- This pattern usually indicates buffering/scheduling pressure in VLC/ALSA under decode load (not a dead headphone port).

#### Continue diagnosis (no `rg` required)

1. Pick a file that definitely has audio (for example `video1.mp4`) and run VLC in background with verbose logging:

```bash
: > /tmp/vlc-audio-debug.log
cvlc -vvv -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
```

2. While video is running, search log for ALSA/buffer errors (using `grep`):

```bash
grep -Ei "alsa|underrun|buffer|drop|xrun|error" /tmp/vlc-audio-debug.log
```

Optional: watch matches update live during playback:

```bash
watch -n 1 "grep -Ei 'alsa|underrun|buffer|drop|xrun|error' /tmp/vlc-audio-debug.log | tail -n 20"
```

3. Interpret the grep output:

- If you see `underrun`, `xrun`, or repeated ALSA write errors, tune buffering first.
- If you do **not** see underruns (current Pi result), but see MMAL/X output probe errors like `mmal_xsplitter ... Failed to open ...`, continue with backend A/B tests below.

4. A/B test audio device mode (same video, same volume, one-at-a-time):

```bash
# stop previous test first
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null

# A: current path
cvlc -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid

# B: ALSA default conversion path for headphones
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null
cvlc -A alsa --alsa-audio-device sysdefault:CARD=Headphones /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid

# C: dmix path
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null
cvlc -A alsa --alsa-audio-device dmix:CARD=Headphones,DEV=0 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
```

5. A/B test cache buffering:

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null
cvlc --file-caching=2000 --network-caching=2000 -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
```

6. Reduce VLC video-output probing noise (can reduce startup module churn):

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null
cvlc --no-xlib -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
```

When done testing:

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null
rm -f /tmp/vlc-audio.pid
```

7. If improved, apply persistent ALSA buffering:

```bash
sudo tee /etc/asound.conf >/dev/null <<'EOF'
defaults.ctl.card 1
defaults.pcm.card 1
defaults.pcm.period_time 500
defaults.pcm.buffer_time 4000
EOF
```

8. Re-test with your Python script after reboot:

```bash
sudo reboot
```

If one of the A/B paths is clearly cleaner, mirror that exact `--alsa-audio-device` choice in `mp4m-gpio.py`. Keep `HEADPHONE_LEVEL` + `VLC_AUDIO_VOLUME` with some headroom (avoid both near max).

#### Latest A/B outcome snapshot

- `B (sysdefault:CARD=Headphones)`: audio present but same artifact as `A`.
- `C (dmix:CARD=Headphones,DEV=0)`: no audio.
- `D (--no-xlib + plughw:1)`: same artifact as `A/B`.
- No `underrun`/`xrun` seen in filtered logs.

#### Next tests (backend/decode path), background style

Use this same pattern each run:

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; : > /tmp/vlc-audio-debug.log
```

1. Force `mmal_vout` directly (skip xsplitter selection noise):

```bash
cvlc -vvv --vout=mmal_vout -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
sleep 10
grep -Ei "using vout display module|mmal_xsplitter|underrun|xrun|error" /tmp/vlc-audio-debug.log
```

2. Disable hardware decode (checks MMAL decode interaction):

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; : > /tmp/vlc-audio-debug.log
cvlc -vvv --avcodec-hw=none -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
sleep 10
grep -Ei "avcodec|mmal|using vout display module|underrun|xrun|error" /tmp/vlc-audio-debug.log
```

3. Force resampler + output rate:

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; : > /tmp/vlc-audio-debug.log
cvlc -vvv --audio-resampler=soxr --aout-rate=48000 -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
sleep 10
grep -Ei "resampler|rate|alsa|underrun|xrun|error" /tmp/vlc-audio-debug.log
```

4. PulseAudio output test (if pulse is installed/running):

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; : > /tmp/vlc-audio-debug.log
cvlc -vvv -A pulse /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
sleep 10
grep -Ei "pulse|alsa|underrun|xrun|error" /tmp/vlc-audio-debug.log
```

Stop test playback when done:

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; rm -f /tmp/vlc-audio.pid
```

If `grep` says `Binary file ... matches`, use one of these:

```bash
grep -aEi "underrun|xrun|error|mmal|alsa|resampler|rate" /tmp/vlc-audio-debug.log
```

```bash
strings /tmp/vlc-audio-debug.log | grep -Ei "underrun|xrun|error|mmal|alsa|resampler|rate"
```

#### Phase 2: isolate analog-under-video-load behavior

1. Same file, VLC audio-only (control check):

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; : > /tmp/vlc-audio-debug.log
cvlc -vvv --no-video -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
```

2. Same file, normal video+audio (comparison):

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; : > /tmp/vlc-audio-debug.log
cvlc -vvv -A alsa --alsa-audio-device plughw:1 /home/pi/video1.mp4 > /tmp/vlc-audio-debug.log 2>&1 &
echo $! > /tmp/vlc-audio.pid
```

3. If audio-only is clean but video+audio is still bad after all VLC flag tests, treat onboard 3.5mm output as the bottleneck under GPU load and move to one of these production paths:

- USB audio adapter/DAC (recommended for kiosk stability).
- HDMI audio extractor (keep video on HDMI, route clean analog line-out externally).

4. Final cleanup:

```bash
kill $(cat /tmp/vlc-audio.pid) 2>/dev/null; rm -f /tmp/vlc-audio.pid
```

#### Phase 2 result (current Pi)

- `H` (`--no-video`) sounds clean.
- `I` (video+audio) sounds bad again.
- Conclusion: onboard headphone output is the limiting path under video/GPU load on this setup, not file corruption and not simple VLC flag choice.

#### Decision paths from here

Path A: keep using onboard headphone output (best-effort mitigation)

1. Lower gain/headroom in script first (example start point):
   - `HEADPHONE_LEVEL = 38`
   - `VLC_AUDIO_VOLUME = 45`
2. Re-export problem videos with controlled peaks (normalization + limiter), 48kHz stereo.
3. Optional firmware trade-off test in `/boot/config.txt`:

```ini
audio_pwm_mode=1
```

`audio_pwm_mode=1` can reduce some contention scenarios, but it is documented as lower-quality analogue mode.

Current project test result:

- `audio_pwm_mode=1` improved the harsh distortion, but introduced intermittent audio dropouts/cut-outs.
- Treat this as a temporary troubleshooting knob, not the final museum/kiosk production setting.

Path B: move off onboard 3.5mm for production reliability

1. USB audio adapter/DAC (preferred practical fix for kiosks).
2. HDMI audio extractor (keep HDMI video, split clean analog line-out externally).
3. If using USB DAC, identify card:

```bash
aplay -l
```

Then test:

```bash
cvlc -A alsa --alsa-audio-device sysdefault:CARD=<USB_CARD_NAME> /home/pi/video1.mp4
```

#### External references supporting these findings

- Raspberry Pi official config docs (`audio_pwm_mode`):
  - `audio_pwm_mode=1` is legacy low quality.
  - `audio_pwm_mode=2` is higher quality but "uses more GPU compute resources and can interfere with some use cases on some models."
  - https://raw.githubusercontent.com/raspberrypi/documentation/master/documentation/asciidoc/computers/config_txt/audio.adoc
- Raspberry Pi Linux issue showing headphone crackle with MMAL/video load while HDMI audio is fine (Pi4):
  - https://github.com/raspberrypi/linux/issues/4146
- Raspberry Pi firmware issue discussing analog output interactions with PWM on Pi4:
  - https://github.com/raspberrypi/firmware/issues/1293

### Display / HDMI issues

These options live in `/boot/config.txt` (edit with `sudo nano /boot/config.txt`, reboot to apply):

| Problem | Fix (uncomment in config.txt) |
|---|---|
| No picture at all | `hdmi_safe=1` (safe mode, guaranteed output) |
| No picture, composite showing | `hdmi_force_hotplug=1` |
| Projector not auto-detecting | `hdmi_group=1`, `hdmi_mode=16`, `hdmi_force_hotplug=1` (forces 1080p60) |
| Black border around image | `disable_overscan=1` |
| Need 4K 60Hz (Pi 4 only) | `hdmi_enable_4kp60=1` |
| HDMI audio not working | `hdmi_drive=2` |
| Weak/flickering HDMI signal | `config_hdmi_boost=4` |
| Portrait / vertical screen | `display_rotate=1` (90 CW) or `display_rotate=3` (90 CCW) |

- **Check current display mode**: `tvservice -s`
- If nano warns "file is being edited by another process" -- press **Y**, it's harmless.

### Video encoding

- **Use H.264 codec** for all video files (Handbrake is recommended for conversion).
- **4K on Pi 4**: Must use H.265 instead.
- **Stuttering video?** The file may be software-decoded. Re-encode with H.264 in Handbrake. Also check `gpu_mem=128` in `/boot/config.txt`.
- Export from your editor in ProRes/DNxHD first, then compress with Handbrake.

### Network / SSH issues

- **Can't SSH in?**
  1. Is SSH enabled? On the Pi: `sudo systemctl status ssh`
  2. Does the Pi have an IP? On the Pi: `hostname -I`
  3. Are you on the same network? From laptop: `ping <PI_IP>`
  4. Try Ethernet first (simpler, no Wi-Fi config to debug)
  5. `raspberrypi.local` not resolving? Use the IP directly. On Windows, install Bonjour or use IP.
  6. Still failing? Check if port 22 is open: `ssh -v pi@<IP>`

- **Wi-Fi won't connect?**
  1. Check for soft block first: `rfkill list` -- if Wi-Fi shows `Soft blocked: yes`, run `sudo rfkill unblock wifi`
  2. Verify SSID/password: `sudo raspi-config` -> System Options -> Wireless LAN
  3. Check interface status: `ip a` (look for `wlan0` with an `inet` address)
  4. Restart networking: `sudo systemctl restart dhcpcd`
  5. Check for 5GHz-only networks -- some Pis only support 2.4GHz

- **Connection drops?**
  - Add to your laptop's SSH config (`~/.ssh/config`):

```
Host pi
    HostName raspberrypi.local
    User pi
    ServerAliveInterval 30
```

  - Then just `ssh pi` to connect with keep-alive.
