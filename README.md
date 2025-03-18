# neom9n

Program to communicate with the NEO-M9N GPS board over USB

## Install

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Edit `SERIAL_PATH` in _record.py_.

On Linux, run `sudo usermod -a -G dialout [you user name]`.

## Run

```sh
python record.py
```

## Post-processing

Time and position are stored in `$GNGGA` messages.

See _parse.py_ for an example.
