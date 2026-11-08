import machine
import time
from melodies import MELODIES
from rtttl import parse_rtttl

initial_volume = 0.1


class Speaker:
    def __init__(self, pin_number):
        self.pwm = machine.PWM(machine.Pin(pin_number))
        self.pwm.duty_u16(0)

        self.alarming = False
        self.melody = MELODIES["Default"]
        self.step_index = 0

        self.timer = machine.Timer()  # Only hardware timer must change the PWM
        self.alarm_start = 0

        self.current_volume_factor = (
            initial_volume  # update() called from main loop must only change volume
        )

    def tone(self, freq, duty):
        if freq <= 0:
            self.pwm.duty_u16(0)
            return
        self.pwm.freq(int(freq))
        self.pwm.duty_u16(int(duty))

    def stop_alarm(self):
        self.alarming = False
        self.timer.deinit()
        self.pwm.duty_u16(0)
        time.sleep(0.1)

    def start_alarm(self, sound=None):
        self.stop_alarm()

        self.alarming = True
        self.step_index = 0
        self.alarm_start = time.ticks_ms()

        # RTTTL string
        if isinstance(sound, str) and sound.count(":") >= 2:
            try:
                self.melody = parse_rtttl(sound)
            except:
                self.melody = MELODIES["Default"]
        else:
            if isinstance(sound, str) and sound in MELODIES:
                entry = MELODIES[sound]
                if isinstance(entry, str) and entry.count(":") >= 2:
                    try:
                        self.melody = parse_rtttl(entry)
                    except:
                        self.melody = MELODIES["Default"]
                else:
                    self.melody = entry
            else:
                self.melody = MELODIES["Default"]

        self._play_step()

    # ---------------------------------------------------------
    # TIMER completely sets PWM
    # ---------------------------------------------------------

    def _play_step(self):
        if not self.alarming:
            return

        action, freq, duty, duration = self.melody[self.step_index]

        if action == "tone":
            adjusted = int(duty * self.current_volume_factor)  # type: ignore
            self.tone(freq, adjusted)
        else:
            self.pwm.duty_u16(0)

        self.timer.init(
            mode=machine.Timer.ONE_SHOT,
            period=duration,  # type: ignore
            callback=lambda t: self._next_step(),
        )

    def _next_step(self):
        if not self.alarming:
            return

        self.step_index += 1
        if self.step_index >= len(self.melody):
            self.step_index = 0

        self._play_step()

    # ---------------------------------------------------------
    # UPDATE only calculates volume
    # ---------------------------------------------------------

    def update(self):
        if not self.alarming:
            return

        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, self.alarm_start) // 1000

        jump_every = 30

        step = elapsed // jump_every
        duty_factor = initial_volume + step * 0.1
        if duty_factor > 1.0:
            duty_factor = 1.0

        # Only update volume, do NOT set PWM here
        self.current_volume_factor = duty_factor
