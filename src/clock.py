import ntptime
import time
from network_managers import WifiState


class ClockState:
    IDLE = "idle"
    SYNCED = "synced"
    UNSYNCED = "unsynced"


class Clock:
    def __init__(self, wifi_manager, tz_offset_winter=1, ntp_server="pool.ntp.org"):
        self.wifi = wifi_manager

        try:
            tz_offset_winter = int(tz_offset_winter)
        except:
            tz_offset_winter = 0

        self.tz_winter = tz_offset_winter * 3600
        self.tz_summer = (tz_offset_winter + 1) * 3600
        self.ntp_server = ntp_server

        self.last_sync = 0
        self.next_attempt = 0
        self.sync_interval = 3600 * 6  # every 6h
        self.state = ClockState.IDLE

    def _dst_rule(self, year, month, mday, hour, spring_hour, autumn_hour):
        """EU summertime rule.

        spring_hour / autumn_hour are the hours at which the clocks change.
        They depend on whether `hour` is a UTC hour or a local wall-clock
        hour; the rest of the rule is identical either way:

            local wall clock : spring 02:00, autumn 03:00
            UTC             : spring 01:00, autumn 01:00
        """
        # Winter time: January, February, November, December
        if month < 3 or month > 10:
            return False

        # Sommer time: April to September
        if 4 <= month <= 9:
            return True

        # Last Sunday in March
        if month == 3:
            # Calculate weekday of last day in month and subtract from 31.
            # The day offset of 31.3. needs to be added,
            # because (5 * year // 4) % 7 only calculates the weekday offset of the current year.
            # The formula is from the Zeller‑Kongruenz and starts with March as month 1.
            # A year offset by 1 is already included.
            # That's why the also needed "day of year offset" needs to be calculated
            # with 31 % 7 (1.3. is day 1) instead of 90 % 7 (1.1. is day 1).
            # Additionally to 31 % 7 = 3 we need to add 1, because Zeller moves the year offset by 1:
            last_sunday = 31 - (5 * year // 4 + 4) % 7
            if mday < last_sunday:
                return False  # before last sunday -> winter time
            if mday > last_sunday:
                return True  # after last sunday -> summer time
            return hour >= spring_hour

        # Last Sunday in October
        if month == 10:
            # Same as above, but the "day of year offset" for 31.10. is +1.
            last_sunday = 31 - (5 * year // 4 + 1) % 7
            if mday < last_sunday:
                return True  # before last sunday -> summer time
            if mday > last_sunday:
                return False  # after last sunday -> winter time
            return hour < autumn_hour

        return False

    # EU summertime rule, for a UTC time.
    #
    # `t` is a UTC tuple, as returned by MicroPython's time.localtime():
    # ntptime.settime() stores UTC and time.setlocaltime() is never called, so
    # time.localtime() is UTC on this device. The clocks change at 01:00 UTC.
    #
    # For a wall-clock time (an alarm time) use offset_for_walltime().
    def is_dst_localtime(self, t):
        year, month, mday, hour, *_ = t
        return self._dst_rule(year, month, mday, hour, 1, 1)

    def offset_for_walltime(self, t):
        """UTC offset in seconds applying to a wall-clock time `t`."""
        year, month, mday, hour, *_ = t
        if self._dst_rule(year, month, mday, hour, 2, 3):
            return self.tz_summer
        return self.tz_winter

    def check(self):
        now = time.time()

        # Not yet time for sync?
        if now < self.next_attempt:
            pass

        # Only sync if connected
        elif self.wifi.state != WifiState.CONNECTED:
            pass

        # Time for sync?
        elif now - self.last_sync >= self.sync_interval:
            try:
                print("Clock: syncing NTP...")
                ntptime.host = self.ntp_server
                ntptime.settime()

                self.last_sync = now
                self.next_attempt = now + self.sync_interval
                self.state = ClockState.SYNCED

                print("Clock: synced:", self.walltime())

            except Exception as e:
                print("Clock: NTP error:", e)
                # Retry in 10 seconds
                self.next_attempt = now + 10
                self.state = ClockState.UNSYNCED

        return self.state

    def walltime(self):
        """Current time as a local wall-clock tuple.

        The three time bases in play:
            time.time()      epoch seconds
            time.localtime() UTC
            walltime()       local wall clock
        """
        t = time.localtime()
        offset = self.tz_summer if self.is_dst_localtime(t) else self.tz_winter
        return time.localtime(time.time() + offset)

    def time_string(self, show_seconds=False):
        y, m, d, hh, mm, ss, *_ = self.walltime()
        if show_seconds:
            return f"{hh:02d}:{mm:02d}:{ss:02d}"
        else:
            return f"{hh:02d}:{mm:02d}"

    def date_string(self):
        y, m, d, *_ = self.walltime()
        return f"{d:02d}.{m:02d}.{y}"
