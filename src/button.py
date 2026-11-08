import time
import machine
import os

DOUBLE_CLICK_TIME = 0.8
TRIPLE_CLICK_TIME = 1.2
LONG_PRESS_TIME = 1.8
DEBOUNCE_MS = 50


class ButtonState:
    SINGLE = "single_click"
    DOUBLE = "double_click"
    TRIPLE = "triple_click"
    LONG = "long_press"
    RELEASE = "release"


class ButtonHandler:
    def __init__(self, pin_number):
        self.btn = machine.Pin(pin_number, machine.Pin.IN, machine.Pin.PULL_UP)

        self.click_times = []
        self.hold_start = None
        self.long_press_sent = False

        self.last_irq = time.ticks_ms()

        self.btn.irq(
            trigger=machine.Pin.IRQ_FALLING | machine.Pin.IRQ_RISING,
            handler=self._irq_handler,
        )

    def _irq_handler(self, pin):
        now = time.ticks_ms()

        # Debounce
        if time.ticks_diff(now, self.last_irq) < DEBOUNCE_MS:
            return
        self.last_irq = now

        t = time.time()

        if pin.value() == 0:
            # pressed
            self.hold_start = t
            self.long_press_sent = False

        else:
            # released
            hs = self.hold_start
            if hs is None:
                return

            self.hold_start = None

            # Was LONG PRESS already fired during press?
            if self.long_press_sent:
                return

            # normal CLICK
            self.click_times.append(t)

    def check(self):
        now = time.time()

        # LONG PRESS during press
        hs = self.hold_start
        if hs is not None and not self.long_press_sent:
            if now - hs >= LONG_PRESS_TIME:
                self.long_press_sent = True
                self.click_times.clear()
                return ButtonState.LONG

        if not self.click_times:
            return None

        first = self.click_times[0]
        if first is None:
            self.click_times.clear()
            return None

        dt_first = now - first
        count = len(self.click_times)

        # TRIPLE check first
        if count >= 3 and dt_first > TRIPLE_CLICK_TIME:
            self.click_times.clear()
            return ButtonState.TRIPLE

        # DOUBLE check
        if count == 2 and dt_first > TRIPLE_CLICK_TIME:
            self.click_times.clear()
            return ButtonState.DOUBLE

        # SINGLE check
        if count == 1 and dt_first > DOUBLE_CLICK_TIME:
            # but only if it's clear that there's no further click
            # if dt_first > TRIPLE_CLICK_TIME:
            self.click_times.clear()
            return ButtonState.SINGLE

        return None


def factory_reset():
    # Delete config file and reboot
    try:
        os.remove("config.json")
    except:
        pass
    machine.reset()
