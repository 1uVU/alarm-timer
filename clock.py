#!/usr/bin/env python3
# alarm: an interactive terminal timer / alarm clock.
# Asks whether you want a countdown timer or an alarm at a clock time,
# waits with a live countdown, then rings until you press Ctrl-C.

# Selective imports: only the names actually used.
from time import sleep
from re import fullmatch
from subprocess import run
from os.path import exists
from datetime import datetime, timedelta

# Alarm sound. If this file doesn't exist, ring() falls back to synthesized beeps.
ALARM_FILE = "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"

# ffplay plays the sound.
# -nodisp: no video window; -autoexit: quit when the sound ends;
# -loglevel quiet: suppress ffplay's console output.
FFPLAY = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]

def from_duration(text):
 """Turn '30', '1h15m' or '90s' into the datetime that far from now."""
 # A bare number means minutes, like the prompt in your old script.
 if text.isdigit():
  text += "m"
 # Optional hours, minutes and seconds groups, in that order (e.g. 1h15m30s).
 m = fullmatch(r"(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", text)
 # The pattern also matches the empty string, so reject "no group matched".
 if not m or not any(m.groups()):
  raise ValueError(text)
 # Groups that didn't match are None; "or 0" turns them into zero.
 h, mi, s = (int(x or 0) for x in m.groups())
 return datetime.now() + timedelta(hours=h, minutes=mi, seconds=s)

def from_clock(text):
 """Turn 'HH:MM' (24-hour) into the next datetime with that time."""
 # strptime raises ValueError on bad input, which ask_target() catches.
 t = datetime.strptime(text, "%H:%M").time()
 target = datetime.combine(datetime.now().date(), t)
 # If that time already passed today, aim for the same time tomorrow.
 return target if target > datetime.now() else target + timedelta(days=1)

def ask_target():
 """Ask the user which mode they want, then return the target datetime."""
 mode = ""
 # Keep asking until the first letter of the answer is 't' or 'a'.
 while mode not in ("t", "a"):
  mode = input("[T]imer or [a]larm at a set time? ").strip().lower()[:1]
 # Keep asking until the time or duration can be parsed.
 while True:
  try:
   if mode == "t":
    return from_duration(input("How long? (30, 1h15m, 90s). A bare number means minutes: ").strip())
   return from_clock(input("At what time? (HH:MM, 24h): ").strip())
  except ValueError:
   print("Couldn't read that, try again.")

def ring():
 """Play the alarm sound once (or a beep pattern if the file is missing)."""
 if exists(ALARM_FILE):
  run(FFPLAY + [ALARM_FILE])
 else:
  # Fallback: three short 880 Hz beeps from ffmpeg's built-in sine generator.
  for _ in range(3):
   run(FFPLAY + ["-f", "lavfi", "sine=frequency=880:duration=0.25"])
   sleep(0.15)

# Main flow. Ctrl-C (or Ctrl-D at a prompt) jumps to the handler at the bottom.
try:
 target = ask_target()
 print(f"Alarm set for {target:%a %H:%M:%S}")

 # Countdown loop. We compare against the wall clock each time rather than
 # sleeping once for the whole duration, so the display stays accurate.
 # The walrus operator (:=) stores the seconds left and tests it in one step.
 while (left := (target - datetime.now()).total_seconds()) > 0:
  # \r returns to the start of the line so the countdown overwrites itself.
  print(f"\r{int(left//3600):02d}:{int(left%3600//60):02d}:{int(left%60):02d}  ",
        end="", flush=True)
  sleep(0.5)

 # Time is up: ring repeatedly until the user interrupts.
 print("\nTime's up! Press Ctrl-C to stop.")
 while True:
  ring()
  sleep(1)  # short pause between repetitions
except (KeyboardInterrupt, EOFError):
 # Clean exit instead of a traceback.
 print("\nStopped.")
