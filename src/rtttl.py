import re

NOTE_ORDER = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def parse_rtttl(rtttl_string):
    parts = rtttl_string.split(":")
    if len(parts) != 3:
        raise ValueError("Invalid RTTTL string")

    defaults = get_defaults(parts[1])
    melody = get_data(parts[2], defaults)

    return melody  # <--- Important: return only melody list


def get_name(name):
    if not name:
        return "Unknown"
    return name


def get_defaults(defaults):
    values = defaults.split(",")

    result = {}
    for v in values:
        if not v:
            continue

        key, val = v.split("=")

        if key == "d":
            result["duration"] = int(val)
        elif key == "o":
            result["octave"] = int(val)
        elif key == "b":
            result["bpm"] = int(val)

    return {
        "duration": result.get("duration", 4),
        "octave": result.get("octave", 6),
        "bpm": result.get("bpm", 63),
    }


def get_data(melody, defaults):
    notes = melody.split(",")
    beat_every = 60000 / defaults["bpm"]

    parsed = []

    regex = re.compile(r"(1|2|4|8|16|32|64)?((?:[a-g]|h|p)#?)(\.?)(4|5|6|7)?")

    for note in notes:
        note = note.strip()
        match = regex.match(note)
        if not match:
            continue

        dur, nt, dotted, octv = match.groups()

        duration = int(dur) if dur else defaults["duration"]

        nt = nt.lower()
        if nt == "h":
            nt = "b"

        octave = int(octv) if octv else defaults["octave"]

        freq = calculate_frequency(nt, octave)
        ms = calculate_duration(beat_every, duration, dotted == ".")

        # Response with a tupel, not a dict
        parsed.append(("tone" if freq else "pause", freq, 4000, int(ms)))  # duty

    return parsed


def calculate_frequency(note, octave):
    if note == "p":
        return 0

    C4 = 261.63
    twelfth = 2 ** (1 / 12)

    semitones = calculate_semitones_from_c4(note, octave)
    freq = C4 * (twelfth**semitones)

    return round(freq, 1)


def calculate_semitones_from_c4(note, octave):
    base = NOTE_ORDER.index(note)
    jump = (octave - 4) * 12
    return base + jump


def calculate_duration(beat_every, note_duration, dotted):
    base = (beat_every * 4) / note_duration
    if dotted:
        base += base / 2
    return base
