import pathlib
import datetime
import sys
import time

import serial

SERIAL_PATH: str = "/dev/tty.usbmodem101"

dirname = pathlib.Path(__file__).resolve().parent

recordings = dirname / "recordings"
recordings.mkdir(exist_ok=True)

with serial.Serial(SERIAL_PATH, baudrate=38400) as gps:
    name = (
        datetime.datetime.now(tz=datetime.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
        .replace(":", "-")
    )
    last_flush = time.monotonic_ns()
    with open(recordings / f"{name}.jsonl", "w") as jsonl_file:
        while True:
            line = gps.readline()
            system_timestamp = time.monotonic_ns()
            t = (
                datetime.datetime.now(tz=datetime.timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
            )
            decoded_line = line.decode(errors="ignore")
            jsonl_file.write(
                f'{{"t":"{t}","system_timestamp":{system_timestamp},"data":"{decoded_line.strip()}"}}\n'
            )
            if system_timestamp - last_flush > 100_000_000:  # 100 ms
                jsonl_file.flush()
                last_flush = system_timestamp
            sys.stdout.write(decoded_line)
