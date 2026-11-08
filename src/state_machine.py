import time


class WakeState:
    STANDBY = "standby"
    INFO = "info"
    NIGHT = "night"
    NIGHT_INFO = "night_info"
    ALARM_RINGING = "alarm_ringing"
    ALARM_SNOOZE = "alarm_snooze"
    CALM = "calm"
    SETUP = "setup"
    INIT = "init"
    BOOT = "boot"


class StateMachine:
    def __init__(self, publish_state_callback=None, state_change_callback=None):
        self.publish_state_callback = publish_state_callback
        self.state_change_callback = state_change_callback

        self.info_until = 0
        self.night_temp_until = 0
        self.state = WakeState.BOOT

        self.set(WakeState.INIT)

    def set(self, new_state):
        now = time.time()

        old_state = self.state
        self.state = new_state
        print("StateMachine: Switch to state:", new_state)

        # Central state entry logic
        self._on_enter_state(new_state, now)

        # Publish
        if self.publish_state_callback:
            self.publish_state_callback(new_state)

        # Notify main.py
        if self.state_change_callback:
            self.state_change_callback(old_state, new_state)

    def _on_enter_state(self, state, now):
        if state == WakeState.INFO:
            self.info_until = now + 60

        elif state == WakeState.NIGHT_INFO:
            self.night_temp_until = now + 15

        # Other states don't have timers

    def update(self):
        now = time.time()

        if self.state == WakeState.INFO and now > self.info_until:
            self.set(WakeState.STANDBY)

        elif self.state == WakeState.NIGHT_INFO and now > self.night_temp_until:
            self.set(WakeState.NIGHT)
