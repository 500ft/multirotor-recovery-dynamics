"""QT Py RP2040 bench-acquisition firmware (CircuitPython).

Implements the wiring, addresses and settings registered in
`docs/bench-acquisition.md` R2.1-R2.4: NAU7802 on the STEMMA connector
(I2C1), INA260 and LIS3DH on the SDA/SCL pads (I2C0), one digital beam
input. Emits one newline-delimited JSON record per sample/event over USB
serial; a host script (`Instrumentation/bench_capture.py`) demuxes the
stream into one CSV per sensor plus a run manifest. This file writes
nothing to onboard flash and makes no acquisition decisions itself -- it
is a dumb, fail-loud sensor relay.

Not unit-testable off-device (needs CircuitPython + the physical bus).
Bring-up must follow docs/bench-acquisition.md #4 one step at a time;
this firmware does not sequence that for you.

Deploy: copy as CIRCUITPY:/code.py. Requires adafruit_nau7802,
adafruit_ina260 and adafruit_lis3dh installed in CIRCUITPY:/lib.
"""
import board
import busio
import digitalio
import json
import supervisor
import time

import adafruit_ina260
import adafruit_lis3dh
import adafruit_nau7802

FIRMWARE_VERSION = "bench-capture-0.1"

NAU7802_RATE_HZ = 80          # docs/bench-acquisition.md #3
LIS3DH_RANGE = adafruit_lis3dh.RANGE_2_G
LOOP_PERIOD_S = 1.0 / NAU7802_RATE_HZ

EPOCH = 0                      # increments once at boot; a reset starts a new process, so
                                # a new epoch is implicit per run -- see bench_capture.py's
                                # per-run manifest, which never spans a device reset.


def emit(sensor, **fields):
    record = {"sensor": sensor, "t_device_us": time.monotonic_ns() // 1000, "epoch": EPOCH}
    record.update(fields)
    print(json.dumps(record))


def init_or_die(name, factory):
    """Construct a sensor driver and read back an identity/config register.

    An I2C ACK is not device identity (docs/bench-acquisition.md #1): the
    driver constructors below read a chip ID or config register as part of
    init and raise if it doesn't match, which is what "or_die" relies on.
    """
    try:
        dev = factory()
    except Exception as exc:  # noqa: BLE001 - fail loud over USB serial, not silently
        emit("_meta", event="init_failed", component=name, error=str(exc))
        raise
    emit("_meta", event="init_ok", component=name)
    return dev


def main():
    emit("_meta", event="boot", firmware_version=FIRMWARE_VERSION,
         nau7802_rate_hz=NAU7802_RATE_HZ)

    i2c1 = board.STEMMA_I2C()          # NAU7802 only (docs/bench-acquisition.md #1)
    i2c0 = busio.I2C(board.SCL, board.SDA)  # INA260 + LIS3DH

    nau = init_or_die("nau7802", lambda: adafruit_nau7802.NAU7802(i2c1, address=0x2A))
    nau.enable(True)
    nau.gain = 128
    nau.rate = adafruit_nau7802.NAU7802.RATE_80SPS
    emit("_meta", event="nau7802_config", gain=nau.gain, rate=NAU7802_RATE_HZ)

    ina = init_or_die("ina260", lambda: adafruit_ina260.INA260(i2c0, address=0x40))

    lis = init_or_die("lis3dh", lambda: adafruit_lis3dh.LIS3DH_I2C(i2c0, address=0x18))
    lis.range = LIS3DH_RANGE

    beam = digitalio.DigitalInOut(board.A0)
    beam.direction = digitalio.Direction.INPUT
    beam.pull = digitalio.Pull.UP  # open-collector receiver, pulled up (docs/bench-acquisition.md #2)
    beam_last = beam.value

    seq = 0
    while True:
        loop_start = time.monotonic()

        if nau.available():
            emit("nau7802", seq=seq, raw_adc=nau.read())

        emit("ina260", seq=seq, bus_v=ina.voltage, current_ma=ina.current)

        x, y, z = lis.acceleration
        emit("lis3dh", seq=seq, x_m_s2=x, y_m_s2=y, z_m_s2=z, range_g=2,
             saturated=any(abs(v) >= 78.4 for v in (x, y, z)))  # ~8g raw-count ceiling at +/-2g range

        state = beam.value
        if state != beam_last:
            emit("beam", seq=seq, state=("clear" if state else "blocked"))
            beam_last = state

        seq += 1
        elapsed = time.monotonic() - loop_start
        remaining = LOOP_PERIOD_S - elapsed
        if remaining > 0:
            time.sleep(remaining)

        if supervisor.runtime.serial_bytes_available:
            # any host keystroke ends the run cleanly rather than mid-record
            break

    emit("_meta", event="stop")


if __name__ == "__main__":
    main()
