class AlarmIndicator:
    def __init__(self, led):
        self.led = led
        self.last_blink = 0

    def start(self):
        self.led.on()
        self.last_blink = 0

    def stop(self):
        self.led.off()

    def update(self, now_ts):
        if now_ts - self.last_blink >= 1:
            self.led.toggle()
            self.last_blink = now_ts
