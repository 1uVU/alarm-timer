# alarm-timer
An interactive terminal timer / alarm clock. Asks whether you want a countdown timer or an alarm at a clock time, waits with a live countdown, then rings until you press Ctrl-C.

One might find it convenient to launch it with such Bash funtion:
```
alarm () 
{ 
    local s=$(date +%H%M%S);
    kitty --detach --class "alarm-$s" "$HOME/CS/SoftwareDevelopment/MySoftware/Python/clock/clock.py"
}
```
