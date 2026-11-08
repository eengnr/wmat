import time
import ujson

DEFAULT_DURATION = 300  # seconds (300 = 5 minutes)
DEFAULT_SNOOZE = 300


class AlarmState:
    TRIGGERED = "alarm_triggered"
    TIMEOUT = "alarm_timeout"
    SNOOZE = "alarm_snooze"


class AlarmManager:
    def __init__(
        self,
        clock,
        button_pin,
        indicator,
        speaker,
        config=None,
        alarm_duration=DEFAULT_DURATION,
        snooze_duration=DEFAULT_SNOOZE,
    ):
        self.clock = clock
        self.button_pin = button_pin
        self.indicator = indicator
        self.speaker = speaker
        self.alarm_duration = alarm_duration
        self.snooze_duration = snooze_duration
        self.snooze_until = None

        self.ignored_alarms = set()

        if config:
            self.load_config(config)
        else:
            self.alarms = []

        self.active_alarm = None
        self.alarm_start = 0
        self.alarms_allowed = False

    def load_config(self, config):
        self.clear_alarms()
        # Save alarms as list
        for alarm in config.get("alarms", []):
            self.add_alarm(alarm)
        # Save ignored alarms as hashable set
        self.ignored_alarms = set()
        for key in config.get("ignored_alarms", []):
            self.ignored_alarms.add(tuple(key))

    def allow_alarms(self, switch):
        print("AlarmManager: Allow alarms:", switch)
        self.alarms_allowed = switch

    def clear_alarms(self):
        self.alarms = []

    def _alarms_equal(self, a, b):
        a2 = dict(a)
        b2 = dict(b)

        # Remove properties which don't belong to identity
        a2.pop("sound", None)
        b2.pop("sound", None)
        a2.pop("name", None)
        b2.pop("name", None)

        return a2 == b2

    def add_alarm(self, alarm):
        for i, a in enumerate(self.alarms):
            if self._alarms_equal(a, alarm):
                print("AlarmManager: Alarm exists, overwriting:", alarm)
                self.alarms[i] = alarm
                self.save_alarms()
                return

        self.alarms.append(alarm)
        self.save_alarms()
        print("AlarmManager: Alarm added:", alarm)

    def remove_alarm(self, alarm):
        # Check if alarm exists
        if alarm in self.alarms:
            self.alarms.remove(alarm)
            print("AlarmManager: Alarm removed:", alarm)
            self.save_alarms()  # Persist
        else:
            print("AlarmManager: Alarm not found:", alarm)

    def get_active_alarms(self):
        return self.alarms

    def trigger_alarm(self, alarm):
        print("AlarmManager: Alarm activated:", alarm)
        self.active_alarm = alarm
        self.alarm_start = time.time()
        self.indicator.start()
        sound = alarm.get("sound")
        self.speaker.start_alarm(sound)

    def _alarm_key(self, alarm):
        return (
            alarm["year"],
            alarm["month"],
            alarm["day"],
            alarm["hour"],
            alarm["minute"],
        )

    def is_ignored(self, alarm):
        return self._alarm_key(alarm) in self.ignored_alarms

    def ignore_alarm(self, alarm):
        key = self._alarm_key(alarm)
        print("AlarmManager: Ignoring upcoming alarm:", alarm)
        self.ignored_alarms.add(key)
        self.save_alarms()

    def enable_alarm(self, alarm):
        key = self._alarm_key(alarm)
        if key in self.ignored_alarms:
            print("AlarmManager: Re-enabling alarm:", alarm)
            self.ignored_alarms.remove(key)
            self.save_alarms()

    def snooze_alarm(self):
        if self.active_alarm:
            print("AlarmManager: Alarm snoozed")
            self.speaker.stop_alarm()
            self.indicator.stop()
            self.snooze_until = time.time() + self.snooze_duration

    def stop_alarm(self):
        if self.active_alarm:
            print("AlarmManager: Alarm stopped")
            self.active_alarm = None
            self.snooze_until = None
            self.indicator.stop()
            self.speaker.stop_alarm()

    def check(self):
        now = self.clock.walltime()
        y, m, d, hh, mm = now[:5]

        if self.snooze_until and self.active_alarm:
            if time.time() >= self.snooze_until:
                # Snooze over -> restart alarm
                self.trigger_alarm(self.active_alarm)
                self.snooze_until = None
                return AlarmState.TRIGGERED
            else:
                return None

        if self.snooze_until and not self.active_alarm:
            self.snooze_until = None

        # If alarm is active -> LED blinks and check stop

        if self.active_alarm:
            # Blink each second
            now_ts = time.time()
            self.indicator.update(now_ts)

            # Alarm stop by timeout
            if now_ts - self.alarm_start > self.alarm_duration:
                self.stop_alarm()
                return AlarmState.TIMEOUT

            # Alarm continues
            return None

        # Check if alarm is necessary
        for alarm in list(self.alarms):

            # ---------------------------------------------------------
            # 1) Ignored alarms
            # ---------------------------------------------------------
            if self.is_ignored(alarm):

                # Ignored + in past -> delete
                if (
                    alarm["year"],
                    alarm["month"],
                    alarm["day"],
                    alarm["hour"],
                    alarm["minute"],
                ) < (y, m, d, hh, mm):
                    print("AlarmManager: Removing ignored expired once alarm:", alarm)
                    self.ignored_alarms.discard(self._alarm_key(alarm))
                    self.remove_alarm(alarm)

                # Ignored alarms are never triggered
                continue

            # ---------------------------------------------------------
            # 2) Active alarms
            # ---------------------------------------------------------

            # Expired -> delete it
            if (
                alarm["year"],
                alarm["month"],
                alarm["day"],
                alarm["hour"],
                alarm["minute"],
            ) < (y, m, d, hh, mm):
                print("AlarmManager: Cleaning up expired once alarm:", alarm)
                self.remove_alarm(alarm)
                continue

            # Now necessary -> trigger it
            if (
                alarm["year"] == y
                and alarm["month"] == m
                and alarm["day"] == d
                and alarm["hour"] == hh
                and alarm["minute"] == mm
            ):
                if self.alarms_allowed:
                    self.trigger_alarm(alarm)
                    self.remove_alarm(alarm)
                    return AlarmState.TRIGGERED
                else:
                    self.remove_alarm(alarm)
                    print("AlarmManager: Alarm currently not allowed")
                    return None

    def save_alarms(self):
        try:
            with open("config.json") as f:
                cfg = ujson.load(f)
        except:
            cfg = {}

        cfg["alarms"] = self.alarms

        cfg["ignored_alarms"] = list(self.ignored_alarms)

        with open("config.json", "w") as f:
            ujson.dump(cfg, f)

    def get_next_alarm(self, include_ignored=False):
        y, m, d, hh, mm = self.clock.walltime()[:5]

        next_alarm = None
        next_time = None

        for alarm in self.alarms:

            if not include_ignored and self.is_ignored(alarm):
                continue

            t = (
                alarm["year"],
                alarm["month"],
                alarm["day"],
                alarm["hour"],
                alarm["minute"],
            )

            # Skip past alarms
            if t <= (y, m, d, hh, mm):
                continue

            # Set next alarm
            if next_time is None or t < next_time:
                next_time = t
                next_alarm = alarm

        return next_alarm
