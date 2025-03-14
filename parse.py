import dataclasses
import datetime
import json
import re
import typing

RECORDING_PATH: str = "recordings/2025-03-14T09-45-42.081713Z.jsonl"


@dataclasses.dataclass
class Position:
    latitude_deg: float
    longitude_deg: float
    height_m: float


@dataclasses.dataclass
class Sample:
    t: datetime.datetime
    position: typing.Optional[Position]


LATITUDE_OR_LONGITUDE: re.Pattern = re.compile(r"^(\d+)\.(\d+)$")
NORTH_SOUTH: set[str] = {"N", "S"}
EAST_WEST: set[str] = {"E", "W"}

with open(RECORDING_PATH) as recording:
    for line in recording:
        stripped_line = line.strip()
        if (
            len(stripped_line) > 0
            and stripped_line.startswith("{")
            and stripped_line.endswith("}")
        ):
            entry = json.loads(stripped_line)
            unix_datetime = datetime.datetime.fromisoformat(entry["t"])
            if entry["data"].startswith("$GNGGA,"):
                gps_words = entry["data"].split(",")
                time_string = gps_words[1]
                if len(time_string) > 0:
                    hour_string = time_string[0:2].lstrip("0")
                    hour = int(hour_string) if len(hour_string) > 0 else 0
                    minute_string = time_string[2:4].lstrip("0")
                    minute = int(minute_string) if len(minute_string) > 0 else 0
                    second_string = time_string[4:6].lstrip("0")
                    second = int(second_string) if len(second_string) > 0 else 0
                    microsecond = int(
                        round(float(f"0.{time_string.split('.')[1]}") * 1e6)
                    )
                    unix_date = unix_datetime.date()
                    candidates = [
                        datetime.datetime(
                            year=date.year,
                            month=date.month,
                            day=date.day,
                            hour=hour,
                            minute=minute,
                            second=second,
                            microsecond=microsecond,
                            tzinfo=datetime.timezone.utc,
                        )
                        for date in (
                            unix_date - datetime.timedelta(days=1),
                            unix_date,
                            unix_date + datetime.timedelta(days=1),
                        )
                    ]
                    deltas = [
                        abs((candidate - unix_datetime).total_seconds())
                        for candidate in candidates
                    ]
                    best_index = min(range(len(deltas)), key=deltas.__getitem__)
                    t = candidates[best_index]
                    latitude_match = LATITUDE_OR_LONGITUDE.match(gps_words[2])
                    longitude_match = LATITUDE_OR_LONGITUDE.match(gps_words[4])
                    if (
                        latitude_match is not None
                        and longitude_match is not None
                        and gps_words[3] in NORTH_SOUTH
                        and gps_words[5] in EAST_WEST
                    ):
                        latitude_deg = (
                            int(latitude_match[1][:-2])
                            + float(f"{latitude_match[1][-2:]}.{latitude_match[2]}")
                            / 60.0
                        )
                        if gps_words[3] == "S":
                            latitude_deg = -latitude_deg
                        longitude_deg = (
                            int(longitude_match[1][:-2])
                            + float(f"{longitude_match[1][-2:]}.{longitude_match[2]}")
                            / 60.0
                        )
                        if gps_words[5] == "W":
                            longitude_deg = -longitude_deg
                        sample = Sample(
                            t=t,
                            position=Position(
                                latitude_deg=latitude_deg,
                                longitude_deg=longitude_deg,
                                height_m=float(gps_words[9]),
                            ),
                        )
                    else:

                        sample = Sample(
                            t=t,
                            position=None,
                        )
                    print(sample)
