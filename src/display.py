from machine import Pin, SPI
import random
from ssd1351.ssd1351 import Display, color565
from ssd1351.xglcd_font import XglcdFont
from state_machine import WakeState


class ColorStyle:
    WHITE = color565(255, 255, 255)
    WHITE_WARM = color565(255, 190, 240)
    GRAY = color565(100, 70, 90)
    GRAY_DARK = color565(60, 30, 40)
    GREEN = color565(0, 255, 0)
    GREEN_ACID = color565(0, 255, 100)
    RED = color565(255, 0, 0)
    DARK_RED = color565(100, 10, 10)
    BLUE = color565(0, 0, 255)
    BLUE_SKY = color565(0, 100, 200)
    BLACK = color565(0, 0, 0)
    YELLOW = color565(220, 190, 10)
    ORANGE_DARK = color565(160, 100, 10)


class TextStyle:
    TIME = XglcdFont("fonts/E123421x34.c", 21, 34)
    TIME_SMALL = XglcdFont("fonts/E123414x24.c", 14, 24)
    TEMPERATURE = XglcdFont("fonts/Modified_Degree_Mono5x9.c", 5, 9)


DISPLAY_BORDER = 10
DISPLAY_W_H = 128

DISPLAY_PADDING_TOP = 4
DISPLAY_PADDING_LEFT = 3
DISPLAY_PADDING_RIGHT = 3
DISPLAY_PADDING_BOTTOM = 0


class DisplayController:
    def __init__(self, weather_mgr=None, alarm_mgr=None):
        # SPI setup
        self.spi = SPI(0, baudrate=14500000, sck=Pin(18), mosi=Pin(19), miso=Pin(16))

        # Display
        self.display = Display(self.spi, dc=Pin(20), cs=Pin(17), rst=Pin(21))

        # State
        self.state = WakeState.INIT
        # self.last_state = WakeState.BOOT
        self.last_update_ms = 0
        self.is_off = False

        self.time_str = None
        self.date_str = None
        self.next_alarm = None

        # Anti burn-in
        self.last_minute = -1
        self.x = 10
        self.y = 10
        self.display.clear(ColorStyle.ORANGE_DARK)

        # Weather data
        self.weather_mgr = weather_mgr
        self.alarm_mgr = alarm_mgr

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def set(self, state, next_alarm_str=None):
        """Controlled externally by main.py"""
        print("DisplayController: Set display state to", state)
        self.state = state
        if next_alarm_str is not None:
            self.next_alarm_str = next_alarm_str

        self.update(self.time_str, self.date_str)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------

    def update(self, time_str=None, date_str=None):
        print(
            f"DisplayController: Update called with time {time_str} and date {date_str}, current state {self.state}"
        )

        if time_str is None:
            return

        self.time_str = time_str
        self.date_str = date_str

        # --- NIGHT/CALM MODE ---
        if self.state in (WakeState.NIGHT, WakeState.CALM):
            if not self.is_off:
                self.display.display_off()
                self.is_off = True
            return
        else:
            if self.is_off:
                self.display.display_on()
                self.is_off = False

        # --- RENDERING ---
        if self.state == WakeState.STANDBY:
            self.draw_standby(self.time_str)

        elif self.state == WakeState.NIGHT_INFO:
            self.draw_night(self.time_str, self.date_str)

        elif self.state == WakeState.INFO:
            self.draw_info(self.time_str, self.date_str)

        elif self.state == WakeState.ALARM_RINGING:
            self.draw_alarm(self.time_str)

        elif self.state == WakeState.ALARM_SNOOZE:
            self.draw_snooze(self.time_str)

    # ---------------------------------------------------------
    # Rendering
    # ---------------------------------------------------------

    def draw_standby(self, time_str):

        font = TextStyle.TIME_SMALL

        text_width = font.measure_text(time_str)
        text_height = font.height

        self.x = random.randint(
            DISPLAY_BORDER + DISPLAY_PADDING_LEFT,
            DISPLAY_W_H - DISPLAY_BORDER - text_width - DISPLAY_PADDING_LEFT,
        )
        self.y = random.randint(
            DISPLAY_BORDER + DISPLAY_PADDING_TOP,
            DISPLAY_W_H - DISPLAY_BORDER - text_height - DISPLAY_PADDING_TOP,
        )

        hour = int(time_str.split(":")[0])
        if 7 <= hour <= 20:
            color = ColorStyle.GRAY
        else:
            color = ColorStyle.GRAY_DARK

        self.display.clear()
        self.display.draw_text(self.x, self.y, time_str, font, color)

    def draw_info(self, time_str, date_str=None, next_alarm_str=None):
        self.display.clear()

        font = TextStyle.TIME
        fontText = TextStyle.TEMPERATURE
        color = ColorStyle.WHITE_WARM

        # Center time
        text_width = font.measure_text(time_str)
        x = (
            DISPLAY_W_H - DISPLAY_PADDING_LEFT - text_width
        ) // 2 + DISPLAY_PADDING_LEFT
        y = (DISPLAY_W_H - DISPLAY_PADDING_TOP - font.height) // 2 + DISPLAY_PADDING_TOP

        self.display.draw_text(x, y, time_str, font, color)

        # Date only if available
        if date_str:
            self.show_date(date_str, fontText, color)

        # Next alarm
        self.show_next_alarm(
            fontText,
            color,
            "icons/material-symbols-light_alarm-on-outline-rounded_25_255_190_240.raw",
        )

        # Weather
        self.show_weather(fontText, color)

    def draw_night(self, time_str, date_str=None):
        """Red clock."""
        self.display.clear()

        font = TextStyle.TIME
        fontText = TextStyle.TEMPERATURE
        color = ColorStyle.DARK_RED

        # Center time
        text_width = font.measure_text(time_str)
        x = (
            DISPLAY_W_H - DISPLAY_PADDING_LEFT - text_width
        ) // 2 + DISPLAY_PADDING_LEFT
        y = (DISPLAY_W_H - DISPLAY_PADDING_TOP - font.height) // 2 + DISPLAY_PADDING_TOP
        self.display.draw_text(x, y, time_str, font, color)

        # Date only if available
        if date_str:
            self.show_date(date_str, fontText, color)

        # Next  alarm
        self.show_next_alarm(
            fontText,
            color,
            "icons/material-symbols-light_alarm-on-outline-rounded_25_100_10_10.raw",
        )

        # Weather
        self.show_weather(fontText, color)

    def draw_alarm(self, time_str):
        """Large bright clock."""
        self.display.clear(ColorStyle.DARK_RED)

        font = TextStyle.TIME
        color = ColorStyle.GREEN_ACID
        colorBG = ColorStyle.DARK_RED

        # Center time
        text_width = font.measure_text(time_str)
        x = (DISPLAY_W_H - text_width) // 2
        y = (DISPLAY_W_H - font.height) // 2
        self.display.draw_text(x, y, time_str, font, color, colorBG)

    def draw_snooze(self, time_str):
        self.display.clear()

        font = TextStyle.TIME
        color = ColorStyle.ORANGE_DARK

        # Center time
        text_width = font.measure_text(time_str)
        x = (DISPLAY_W_H - text_width) // 2
        y = (DISPLAY_W_H - font.height) // 2
        self.display.draw_text(x, y, time_str, font, color)

    def normalize_text_for_font(self, text, font):
        # 1) Replace characters
        REPLACEMENTS = {
            "ä": "ae",
            "ö": "oe",
            "ü": "ue",
            "Ä": "Ae",
            "Ö": "Oe",
            "Ü": "Ue",
            "ß": "ss",
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "á": "a",
            "à": "a",
            "â": "a",
            "ã": "a",
            "å": "a",
            "ó": "o",
            "ò": "o",
            "ô": "o",
            "õ": "o",
            "í": "i",
            "ì": "i",
            "î": "i",
            "ï": "i",
            "ú": "u",
            "ù": "u",
            "û": "u",
            "ç": "c",
        }

        for src, dst in REPLACEMENTS.items():
            text = text.replace(src, dst)

        # 2) Get ASCII range of font
        start = font.start_letter
        end = font.start_letter + font.letter_count  # exclusive

        # 3) Keep only characters that can be displayed by font
        cleaned = "".join(ch if start <= ord(ch) < end else "?" for ch in text)

        return cleaned

    def shorten_text(self, text, font, max_width):
        # If text is ok -> done
        if font.measure_text(text) <= max_width:
            return text

        # Reserve space for "..."
        ellipsis = "..."
        ellipsis_width = font.measure_text(ellipsis)

        # Shorten characters
        while text and font.measure_text(text) + ellipsis_width > max_width:
            text = text[:-1]

        return text + ellipsis

    def shorten_year(self, date_str):
        # Extract all number blocks (without regex)
        parts = []
        current = ""

        for ch in date_str:
            if ch.isdigit():
                current += ch
            else:
                if current:
                    parts.append(current)
                    current = ""
        if current:
            parts.append(current)

        # Find four digit year
        year4 = None
        for p in parts:
            if len(p) == 4:
                year4 = p
                break

        # If no four digit year -> return
        if not year4:
            return date_str

        # Make two digit year
        year2 = year4[-2:]

        # Replace year
        return date_str.replace(year4, year2)

    def show_date(self, date_str, font, color):
        short_date = self.shorten_year(date_str)
        date_width = font.measure_text(short_date)
        x_date = DISPLAY_W_H - date_width - DISPLAY_PADDING_RIGHT
        self.display.draw_text(x_date, DISPLAY_PADDING_TOP, short_date, font, color)

    def show_weather(self, font, color):
        if self.weather_mgr:
            current = self.weather_mgr.get_current()
            forecast = self.weather_mgr.get_forecast()

            unit = self.weather_mgr.get_unit()

            # Current weather
            if current:
                temp = current.get("temp")
                condition = current.get("condition")

                if temp is not None:
                    self.display.draw_text(
                        DISPLAY_PADDING_LEFT,
                        DISPLAY_PADDING_TOP,
                        f"{temp} *{unit}",  # Use * instead of °, it's adapted manually in the font
                        font,
                        color,
                    )

                icon_path = self.weather_mgr.get_icon_path(condition, color)
                if icon_path:
                    try:
                        with open(icon_path, "rb") as f:
                            raw = f.read()
                        icon_size = 25
                        self.display.draw_sprite(
                            raw,
                            (
                                DISPLAY_W_H
                                - (icon_size // 2)
                                - DISPLAY_PADDING_LEFT
                                - DISPLAY_PADDING_RIGHT
                            )
                            // 2
                            + DISPLAY_PADDING_LEFT,
                            DISPLAY_PADDING_TOP,
                            icon_size,
                            icon_size,
                        )
                    except Exception as e:
                        print("DisplayController: Weather icon missing:", icon_path, e)

            # Forecast
            if forecast:
                tempLeft = forecast.get("temp1")
                tempRight = forecast.get("temp2")

                if tempLeft is not None and tempRight is not None:
                    y_space_between_texts = 2
                    self.display.draw_text(
                        DISPLAY_PADDING_LEFT,
                        DISPLAY_PADDING_TOP + font.height + y_space_between_texts,
                        f"{tempLeft}/{tempRight} *{unit}",
                        font,
                        color,
                    )

    def show_next_alarm(self, font, color, icon):
        if self.alarm_mgr:
            next_alarm = self.alarm_mgr.get_next_alarm()
            print("DisplayController: Next alarm ", next_alarm)
            if next_alarm is not None:
                next_alarm_date_str = (
                    f"{next_alarm['day']:02d}.{next_alarm['month']:02d}."
                )
                next_alarm_time_str = (
                    f"{next_alarm['hour']:02d}:{next_alarm['minute']:02d}"
                )
                no_name = ""
                next_alarm_name_str = next_alarm.get("name", no_name)

                # Remove non-displayable characters
                next_alarm_name_str = self.normalize_text_for_font(
                    next_alarm_name_str, font
                )
                next_alarm_datetime_str = f"{next_alarm_date_str} {next_alarm_time_str}"

                alarm_datetime_width = font.measure_text(next_alarm_datetime_str)
                x_alarm = (DISPLAY_W_H - alarm_datetime_width) // 2
                height_alarm = font.height

                alarm_name_width = font.measure_text(next_alarm_name_str)

                y_space_between_texts = 2
                y_text = (
                    DISPLAY_W_H
                    - DISPLAY_PADDING_BOTTOM
                    - (height_alarm * 2 + y_space_between_texts)
                )

                rawIcon = None
                try:
                    with open(
                        icon,
                        "rb",
                    ) as f:
                        rawIcon = f.read()
                except Exception as e:
                    print("DisplayController: Alarm icon missing", e)

                # Icon available
                if rawIcon is not None:
                    icon_size = 25
                    icon_width = icon_size
                    x_space_icon_text = 5

                    text_block_width = max(alarm_datetime_width, alarm_name_width)
                    total_width = icon_width + x_space_icon_text + text_block_width

                    x_block = (
                        DISPLAY_W_H
                        - total_width
                        - DISPLAY_PADDING_LEFT
                        - DISPLAY_PADDING_RIGHT
                    ) // 2 + DISPLAY_PADDING_LEFT
                    # If text is too wide, reset x to 0
                    if x_block < DISPLAY_PADDING_LEFT:
                        x_block = DISPLAY_PADDING_LEFT

                    x_icon = x_block
                    y_icon = DISPLAY_W_H - DISPLAY_PADDING_BOTTOM - icon_size

                    x_text = x_icon + icon_width + x_space_icon_text

                    if next_alarm_name_str == no_name:
                        y_text = y_text + ((height_alarm + y_space_between_texts) // 2)

                    # Align icon and text in y direction
                    y_diff_between_icon_and_text = y_icon - y_text
                    if y_diff_between_icon_and_text > 0:
                        # Icon is lower than text, move icon halfway up
                        y_icon = y_icon - y_diff_between_icon_and_text // 2
                    elif y_diff_between_icon_and_text < 0:
                        # Icon is higher than text, move text halfway up
                        y_text = y_text + y_diff_between_icon_and_text // 2

                    self.display.draw_sprite(
                        rawIcon,
                        x_icon,
                        y_icon,
                        icon_size,
                        icon_size,
                    )

                    self.display.draw_text(
                        x_text, y_text, next_alarm_datetime_str, font, color
                    )
                    if next_alarm_name_str != no_name:
                        # Shorten dynamic text
                        next_alarm_name_str = self.shorten_text(
                            next_alarm_name_str,
                            font,
                            DISPLAY_W_H
                            - DISPLAY_PADDING_LEFT
                            - DISPLAY_PADDING_RIGHT
                            - x_text,
                        )
                        self.display.draw_text(
                            x_text,
                            y_text + height_alarm + y_space_between_texts,
                            next_alarm_name_str,
                            font,
                            color,
                        )
                # No icon available
                else:
                    self.display.draw_text(
                        x_alarm, y_text, next_alarm_datetime_str, font, color
                    )
                    x_alarm_name = (
                        DISPLAY_W_H
                        - DISPLAY_PADDING_LEFT
                        - DISPLAY_PADDING_RIGHT
                        - alarm_name_width
                    ) // 2 + DISPLAY_PADDING_LEFT
                    if x_alarm_name < 0:
                        x_alarm_name = 1
                    # Shorten dynamic text
                    next_alarm_name_str = self.shorten_text(
                        next_alarm_name_str,
                        font,
                        DISPLAY_W_H
                        - DISPLAY_PADDING_LEFT
                        - DISPLAY_PADDING_RIGHT
                        - x_alarm_name,
                    )
                    self.display.draw_text(
                        x_alarm_name,
                        y_text + height_alarm + y_space_between_texts,
                        next_alarm_name_str,
                        font,
                        color,
                    )
