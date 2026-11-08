import rp2
import time
import ujson
import wifi_setup
from alarm import AlarmManager, AlarmState
from alarm_indicator import AlarmIndicator
from button import ButtonHandler, ButtonState, factory_reset
from clock import Clock, ClockState
from controls import Controls
from display import DisplayController
from machine import Pin
from mqtt_topics import MQTT_TOPICS
from network_managers import WifiManager, MqttManager, WifiState, MqttState
from speaker import Speaker
from state_machine import StateMachine, WakeState
from weather import WeatherManager

# ---------------------------------------------------------
# Load configuration
# ---------------------------------------------------------
led = Pin("LED", Pin.OUT)
led.on()

config = wifi_setup.load_config()
if config is None:
    print("Main: No config -> Setup mode")
    wifi_setup.start_access_point()
    wifi_setup.start_webserver()
    raise SystemExit()


# ---------------------------------------------------------
# Generate topics
# ---------------------------------------------------------
topic_debug_in = (config["topic_prefix"] + MQTT_TOPICS["debug_in"]).encode()
topic_debug_out = (config["topic_prefix"] + MQTT_TOPICS["debug_out"]).encode()
topic_available = (config["topic_prefix"] + MQTT_TOPICS["available"]).encode()
topic_active_alarms = (config["topic_prefix"] + MQTT_TOPICS["alarms"]).encode()
topic_alarm_add = (config["topic_prefix"] + MQTT_TOPICS["alarm_add"]).encode()
topic_alarm_remove = (config["topic_prefix"] + MQTT_TOPICS["alarm_remove"]).encode()
topic_event = (config["topic_prefix"] + MQTT_TOPICS["event"]).encode()
topic_state = (config["topic_prefix"] + MQTT_TOPICS["state"]).encode()
topic_control = (config["topic_prefix"] + MQTT_TOPICS["control"]).encode()
topic_weather = (config["topic_prefix"] + MQTT_TOPICS["weather"]).encode()

# ---------------------------------------------------------
# Init variables and helpers
# ---------------------------------------------------------
last_minute = -1
bootsel_start = None
last_alarm_publish = 0
last_alarm_state = None
BUTTON_PIN = 10
SPEAKER_PIN = 14
IGNORE_ALARM_MINUTE_WINDOW = 45
DEFAULT_LOOP_SLEEP_TIME = 0.05
SLOW_LOOP_SLEEP_TIME = 10


def is_valid_alarm(alarm):
    # Must be dict
    if not isinstance(alarm, dict):
        return False

    # Time check
    try:
        hour = int(alarm["hour"])
        minute = int(alarm["minute"])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return False
    except (KeyError, ValueError):
        return False

    # Sound check
    # not necessary

    # Date check
    try:
        year = int(alarm["year"])
        month = int(alarm["month"])
        day = int(alarm["day"])
        return 1 <= month <= 12 and 1 <= day <= 31 and year >= 2026
    except (KeyError, ValueError):
        return False


def safe_publish(topic, message):
    if mqtt_mgr.state == MqttState.CONNECTED and mqtt_mgr.client:
        try:
            mqtt_mgr.client.publish(topic, message.encode("utf-8"))
            return True
        except Exception as e:
            print(f"Main: Publish failed: {e}")
    else:
        print("Main: Cannot publish, MQTT not connected")
    return False


def handle_button_event_debug(event):
    ### ONLY FOR DEBUG
    if event == ButtonState.DOUBLE:
        print("Main: Double click")
        clean_reset()

    elif event == ButtonState.TRIPLE:
        print("Main: Triple click")
        speaker.start_alarm("HappyWake")


def on_button_event(button_event):
    print("Main: Event:", button_event)
    # handle_button_event_debug(button_event)
    safe_publish(topic_event, button_event)
    safe_publish(topic_event, ButtonState.RELEASE)

    # ---------------------------------------------------------
    # SINGLE CLICK
    # ---------------------------------------------------------
    if button_event == ButtonState.SINGLE:

        # Standby -> Info
        if sm.state == WakeState.STANDBY:
            sm.set(WakeState.INFO)
            return

        # Info -> back to Standby
        if sm.state == WakeState.INFO:
            sm.set(WakeState.STANDBY)
            return

        # Night -> Night Temp On
        if sm.state == WakeState.NIGHT:
            sm.set(WakeState.NIGHT_INFO)
            return

        # Night Temp On -> back to Night
        if sm.state == WakeState.NIGHT_INFO:
            sm.set(WakeState.NIGHT)
            return

        # Alarm active -> Snooze
        if sm.state == WakeState.ALARM_RINGING:
            sm.set(WakeState.ALARM_SNOOZE)
            return

        return

    # ---------------------------------------------------------
    # TRIPLE
    # ---------------------------------------------------------
    # if button_event == ButtonState.TRIPLE:

    #     # Next alarm, ignored or not
    #     next_alarm = alarm_mgr.get_next_alarm(include_ignored=True)

    #     if not next_alarm:
    #         print("Main: No upcoming alarm found")
    #         return

    #     if alarm_mgr.is_ignored(next_alarm):
    #         alarm_mgr.enable_alarm(next_alarm)
    #         print("Main: Next alarm ENABLED:", next_alarm)
    #     else:
    #         alarm_mgr.ignore_alarm(next_alarm)
    #         print("Main: Next alarm DISABLED:", next_alarm)

    #     return

    # ---------------------------------------------------------
    # LONG PRESS
    # ---------------------------------------------------------
    if button_event == ButtonState.LONG:

        # Alarm active -> Alarm off
        if sm.state == WakeState.ALARM_RINGING:
            sm.set(WakeState.INFO)
            return

        if sm.state == WakeState.ALARM_SNOOZE:
            sm.set(WakeState.INFO)
            return

        # Standby/Info -> Night
        if sm.state == WakeState.STANDBY:
            sm.set(WakeState.NIGHT_INFO)
            return

        if sm.state == WakeState.INFO:
            sm.set(WakeState.NIGHT_INFO)
            return

        # Night/Night temp on -> Info
        if sm.state == WakeState.NIGHT:
            sm.set(WakeState.INFO)
            return

        if sm.state == WakeState.NIGHT_INFO:
            sm.set(WakeState.INFO)
            return

        return


def on_alarm_event(event):
    if event == AlarmState.TRIGGERED:
        sm.set(WakeState.ALARM_RINGING)

    elif event == AlarmState.TIMEOUT:
        sm.set(WakeState.INFO)

    elif event == AlarmState.SNOOZE:
        sm.set(WakeState.ALARM_SNOOZE)


def on_state_change(old_state, new_state):
    print(f"Main: State changed from {old_state} to {new_state}")
    # Generic, move to states:

    if new_state == WakeState.ALARM_RINGING:
        display.set(WakeState.ALARM_RINGING)
        return

    if new_state == WakeState.ALARM_SNOOZE:
        alarm_mgr.snooze_alarm()
        display.set(WakeState.ALARM_SNOOZE)
        return

    if new_state == WakeState.STANDBY:
        alarm_mgr.stop_alarm()
        display.set(WakeState.STANDBY)
        return

    # Turn off display and disable alarms

    if new_state == WakeState.CALM:
        alarm_mgr.allow_alarms(False)
        display.set(WakeState.CALM)
        return

    if new_state not in (WakeState.CALM, WakeState.BOOT, WakeState.INIT):
        alarm_mgr.allow_alarms(True)

    # Switching to day from night

    if old_state in (
        WakeState.NIGHT,
        WakeState.NIGHT_INFO,
    ) and new_state in (
        WakeState.INFO,
        WakeState.STANDBY,
    ):
        print("Main: User woke up -> checking if next alarm should be ignored")

        next_alarm = alarm_mgr.get_next_alarm(include_ignored=True)

        if next_alarm:
            # MicroPython mktime() expects a tuple of 8 elements
            alarm_struct = (
                next_alarm["year"],
                next_alarm["month"],
                next_alarm["day"],
                next_alarm["hour"],
                next_alarm["minute"],
                0,  # seconds
                0,  # weekday (ignored)
                0,  # yearday (ignored)
            )

            # Get time zone
            offset = clock.offset_for_walltime(alarm_struct)

            # mktime gives UTC, clock.walltime works with UTC+offset
            # -> alarm time needs to be put to the same basis like time.time()
            alarm_ts = (
                time.mktime(alarm_struct) - offset  # pyright: ignore[reportCallIssue]
            )
            now_ts = time.time()
            diff_seconds = alarm_ts - now_ts

            # Ignore alarm in time window
            if 0 <= diff_seconds <= IGNORE_ALARM_MINUTE_WINDOW * 60:
                print(
                    f"Main: Next alarm is within {IGNORE_ALARM_MINUTE_WINDOW} minutes -> ignoring it"
                )
                alarm_mgr.ignore_alarm(next_alarm)
            else:
                print(
                    f"Main: Next alarm is NOT within {IGNORE_ALARM_MINUTE_WINDOW} minutes -> keeping it active"
                )

    # Switching to night from day
    if old_state in (WakeState.INFO, WakeState.STANDBY) and new_state in (
        WakeState.NIGHT,
        WakeState.NIGHT_INFO,
    ):
        print("Main: User starts sleeping -> enable next alarm")
        next_alarm = alarm_mgr.get_next_alarm(include_ignored=True)
        if next_alarm:
            alarm_mgr.enable_alarm(next_alarm)

    if new_state == WakeState.INFO:
        alarm_mgr.stop_alarm()
        display.set(WakeState.INFO)
        return

    if new_state == WakeState.NIGHT:
        display.set(WakeState.NIGHT)
        return

    if new_state == WakeState.NIGHT_INFO:
        display.set(WakeState.NIGHT_INFO)
        return


def clean_reset():
    alarm_mgr.stop_alarm()
    speaker.stop_alarm()
    sm.set(WakeState.INFO)


# ---------------------------------------------------------
# Network setup
# ---------------------------------------------------------
def on_incoming_message(topic, msg):
    text = msg.decode("utf-8")
    print("Main: Received:", topic, text)

    # Add alarm
    if topic == topic_alarm_add:
        try:
            alarm = ujson.loads(text)
            if is_valid_alarm(alarm):
                alarm_mgr.add_alarm(alarm)
            else:
                print("Main: Invalid alarm structure:", alarm)
        except Exception as e:
            print("Main: Invalid JSON for add:", e)
        return

    # Remove alarm
    elif topic == topic_alarm_remove:
        try:
            alarm = ujson.loads(text)
            if is_valid_alarm(alarm):
                alarm_mgr.remove_alarm(alarm)
            else:
                print("Main: Invalid alarm structure:", alarm)
        except Exception as e:
            print("Main: Invalid JSON for remove:", e)
        return

    elif topic == topic_control:
        try:
            print("Main: Control received", text)

            # 1) Button events
            if text in ButtonState.__dict__.values():
                on_button_event(text)

            # 2) Stop alarm # Probably obsolete, use enter_state_info instead
            if text == Controls.STOP_ALARM:
                sm.set(WakeState.INFO)

            # 3) ENTER_STATE_<state> commands
            if text.startswith(Controls.ENTER_STATE):
                state = text[len(Controls.ENTER_STATE) :]

                # Only accept allowed states
                if state in WakeState.__dict__.values():
                    print("Main: Entering state", state)
                    sm.set(state)
                else:
                    print("Main: Unknown state:", state)
                return

        except Exception as e:
            print("Main: Error", e)
        return

    elif topic == topic_weather:
        weather_mgr.update_from_json(text)
        return

    # Default handling
    try:
        safe_publish(topic_debug_out, text)
    except:
        print("Main: Error while responding")


wifi_mgr = WifiManager(config["wifi_ssid"], config["wifi_password"])
mqtt_mgr = MqttManager(
    wifi_mgr,
    config,
    on_incoming_message,
    subscribe_topics=[
        topic_debug_in,
        topic_alarm_add,
        topic_alarm_remove,
        topic_control,
        topic_weather,
    ],
    available_topic=topic_available,
)

# ---------------------------------------------------------
# Clock init + NTP sync
# ---------------------------------------------------------
clock = Clock(
    wifi_mgr,
    tz_offset_winter=config.get("tz_offset_winter", 1),
    ntp_server=config.get("ntp_server", "pool.ntp.org"),
)

# ---------------------------------------------------------
# Button + speaker setup
# ---------------------------------------------------------
button = ButtonHandler(pin_number=BUTTON_PIN)
speaker = Speaker(pin_number=SPEAKER_PIN)

# ---------------------------------------------------------
# Init Alarm Manager
# ---------------------------------------------------------
indicator = AlarmIndicator(Pin("LED", Pin.OUT))
speaker = Speaker(Pin(SPEAKER_PIN, Pin.OUT))
alarm_mgr = AlarmManager(clock, button, indicator, speaker, config)

# ---------------------------------------------------------
# Display setup
# ---------------------------------------------------------
weather_mgr = WeatherManager()
display = DisplayController(weather_mgr, alarm_mgr)


# ---------------------------------------------------------
# State setup
# ---------------------------------------------------------
def publish_state(state=None):
    if state is None:
        state = sm.state
    safe_publish(topic_state, state)


sm = StateMachine(
    publish_state_callback=publish_state, state_change_callback=on_state_change
)

loop_sleep_time = DEFAULT_LOOP_SLEEP_TIME

# ---------------------------------------------------------
# Main loop
# ---------------------------------------------------------
while True:

    # -------------
    # Check button events
    # -------------
    button_event = button.check()

    if button_event:
        on_button_event(button_event)

    # BOOTSEL with LED feedback
    if rp2.bootsel_button() == 1:
        if bootsel_start is None:
            bootsel_start = time.time()
            led.on()
            print("Main: BOOTSEL pressed...")
            clean_reset()
        # 10 seconds passed?
        if time.time() - bootsel_start >= 10:
            print("Main: BOOTSEL held 10s -> Factory reset")
            led.off()
            factory_reset()
    else:
        if bootsel_start is not None:
            print("Main: BOOTSEL released")
            led.off()
            bootsel_start = None

    # -------------
    # Do regular updates
    # -------------
    sm.update()
    wifi_state = wifi_mgr.check()
    mqtt_state = mqtt_mgr.check()
    clock_state = clock.check()

    if (
        wifi_state == WifiState.CONNECTED
        and mqtt_state == MqttState.CONNECTED
        and sm.state != WakeState.INIT
    ):
        led.off()
    else:
        led.on()

    # -------------
    # Switch from INIT to INFO after boot and everything was connected
    # -------------
    if (
        wifi_state == WifiState.CONNECTED
        and mqtt_state == MqttState.CONNECTED
        and clock_state == ClockState.SYNCED
        and sm.state == WakeState.INIT
    ):
        led.off()
        sm.set(WakeState.INFO)

    # -------------
    # Wait until everyting is connected and synced
    # -------------
    if sm.state == WakeState.INIT:
        continue

    # -------------
    # Go on with workflow
    # -------------
    speaker.update()

    # -------------
    # Check if alarm list needs to be published
    # -------------

    now = time.time()

    current_alarms = []

    # Check if 'ignored' key needs to be added to list of alarms
    for alarm in alarm_mgr.get_active_alarms():
        a = dict(alarm)
        # Add the 'ignored' key to the list if necessary
        # Ignored alarms are handled internally in a separate list
        if alarm_mgr.is_ignored(alarm):
            a["ignored"] = True
        current_alarms.append(a)

    current_state = ujson.dumps(current_alarms)

    # Publish if something changed
    if current_state != last_alarm_state:
        print("Main: Current alarms: ", current_state)
        print("Main: Trying to publish active alarms because state changed")
        safe_publish(topic_active_alarms, current_state)
        last_alarm_state = current_state
        last_alarm_publish = now

    # -------------
    # Check if loop sleep time can be changed
    # -------------
    if sm.state == WakeState.CALM and loop_sleep_time != SLOW_LOOP_SLEEP_TIME:
        print("Main: Slow down loop")
        loop_sleep_time = SLOW_LOOP_SLEEP_TIME
    elif loop_sleep_time != DEFAULT_LOOP_SLEEP_TIME:
        print("Main: Speed up loop")
        loop_sleep_time = DEFAULT_LOOP_SLEEP_TIME

    # -------------
    # Tasks for every minute
    # -------------
    t = clock.walltime()
    current_minute = t[4]

    if current_minute != last_minute:
        # Print time every minute
        last_minute = current_minute
        time_str = clock.time_string()
        date_str = clock.date_string()
        print("Main: TIME:", time_str)
        # safe_publish(topic_debug_out, time_str)
        publish_state()
        display.update(time_str=time_str, date_str=date_str)

        # Check if alarm needs to be activated
        alarm_event = alarm_mgr.check()

        if alarm_event:
            on_alarm_event(alarm_event)

        # Publish alarms every 10 minutes
        if now - last_alarm_publish >= 600:
            print("Main: Current alarms: ", current_state)
            print("Main: Trying to publish active alarms")
            safe_publish(topic_active_alarms, current_state)
            last_alarm_publish = now

    time.sleep(loop_sleep_time)
