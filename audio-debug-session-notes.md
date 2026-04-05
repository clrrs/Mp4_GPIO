# Audio Debug Session Notes (Apr 2026)

## Scope
- Raspberry Pi 4 kiosk playback via VLC in Python.
- Video on HDMI 1, audio on onboard headphone output.
- Symptom: audio artifacts during video+audio playback; audio-only playback is clean.

## What was tested
- Mixer control:
  - `alsamixer -c 1` changed volume correctly during playback.
- Thermal/power:
  - `vcgencmd get_throttled` consistently `0x0`.
- VLC/ALSA device A/B:
  - `plughw:1` and `sysdefault:CARD=Headphones`: both had artifacts.
  - `dmix:CARD=Headphones,DEV=0`: no audio.
- VLC flags:
  - `--no-xlib`, `--vout=mmal_vout`, `--avcodec-hw=none`, `--audio-resampler=soxr`, `--aout-rate=48000` did not resolve the issue.
- Isolation:
  - `--no-video` playback was clean.
  - Same file with video+audio was bad.

## Interpretation
- Not a source file problem (same content plays clean in other contexts).
- Not thermal throttling.
- Not fixed by common VLC output/decode/resampler toggles.
- Most consistent with known onboard analog (PWM-based) output limitations/interaction under video/GPU load.

## Config test
- Tested `audio_pwm_mode=1` in Pi config.
- Result: harsh distortion improved, but intermittent audio cut-outs appeared.
- Conclusion: useful troubleshooting knob, not production-stable for this project.

## Production recommendation
- Preferred: move off onboard 3.5mm for final deployment:
  - USB audio adapter/DAC, or
  - HDMI audio extractor.

## Local mirror updates made in this workspace
- `pi-mp4museum-cheatsheet.md` updated with test procedure, results, and references.
- `config.txt` updated with commented session note and commented `audio_pwm_mode=1` test line.
