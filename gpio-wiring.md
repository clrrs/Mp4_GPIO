### Hall sensor → Raspberry Pi GPIO wiring

- **Numbering mode**: The script uses `GPIO.BOARD` numbering (physical pin numbers on the 40‑pin header).
- **Logic**: Hall sensors are treated as **active‑low** inputs.
  - Internal **pull‑up** resistors keep the GPIO pin at logic HIGH when idle.
  - When the sensor detects the magnet, it pulls the GPIO pin to **GND** (logic LOW), which the script treats as a trigger.

#### Power and ground

- **3.3 V power**: Use any 3.3 V pin on the header (for example, physical pin **1** or **17**).
- **Ground**: Use any GND pin (for example, physical pins **6**, **9**, **14**, **20**, **25**, **30**, **34**, **39**).
- All five sensors can **share the same 3.3 V and GND rails**.

Each typical 3‑wire hall sensor module has:

- `VCC` → 3.3 V
- `GND` → GND
- `OUT` → one dedicated GPIO pin listed below

#### Pin mapping (BOARD vs BCM vs video)

| Sensor | Function        | Pi HEADER (BOARD) | BCM GPIO | Video file    |
|--------|-----------------|-------------------|----------|---------------|
| 1      | Hall sensor 1   | **11**            | GPIO17   | `video1.mp4`  |
| 2      | Hall sensor 2   | **13**            | GPIO27   | `video2.mp4`  |
| 3      | Hall sensor 3   | **15**            | GPIO22   | `video3.mp4`  |
| 4      | Hall sensor 4   | **16**            | GPIO23   | `video4.mp4`  |
| 5      | Hall sensor 5   | **18**            | GPIO24   | `video5.mp4`  |

In `mp4m-gpio.py` this corresponds to:

```text
SENSOR_PINS = {
    11: "video1.mp4",  # Sensor 1
    13: "video2.mp4",  # Sensor 2
    15: "video3.mp4",  # Sensor 3
    16: "video4.mp4",  # Sensor 4
    18: "video5.mp4",  # Sensor 5
}
```

#### How to wire each hall sensor

For **each** of the 5 sensors:

1. Connect sensor `VCC` to **3.3 V** on the Pi (e.g. pin 1).
2. Connect sensor `GND` to **GND** on the Pi (e.g. pin 6).
3. Connect sensor `OUT` to the assigned GPIO pin:
   - Sensor 1 → header pin **11**
   - Sensor 2 → header pin **13**
   - Sensor 3 → header pin **15**
   - Sensor 4 → header pin **16**
   - Sensor 5 → header pin **18**

No external resistors are required; the script enables **internal pull‑up resistors**:

```text
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
```

#### Quick sanity check script (optional)

If you want to confirm sensor behavior on the Pi:

```python
import time
import RPi.GPIO as GPIO

PINS = [11, 13, 15, 16, 18]  # BOARD numbering

GPIO.setmode(GPIO.BOARD)
for p in PINS:
    GPIO.setup(p, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        states = [GPIO.input(p) for p in PINS]
        print("States (LOW = magnet):", states)
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
```

With this script:

- **No magnet** near a sensor → its pin should read `1` (HIGH).
- **Magnet present** near a sensor → its pin should read `0` (LOW).

