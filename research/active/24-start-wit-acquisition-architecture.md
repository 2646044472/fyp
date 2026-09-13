# START-WIT Acquisition Architecture

> **Superseded (KILL, 2026-09-03):** retained only for a bounded control/
> replication; do not build it as the active FYP gate.

## Decision

Use the Raspberry Pi for command orchestration, local storage and the actual
edge policy. Use a small 3.3 V microcontroller as a deterministic acquisition
front end for the policy sensors, and keep the optical truth logger outside the
policy data path.

This is a measurement decision, not a research contribution. Direct Pi-only
polling may be used as a bring-up comparison, but it is not the default source
for final timing claims until its timestamp jitter is measured.

## Why the split is needed

The first seconds after a start command are the central observation window.
Linux scheduling, I2C polling and USB/serial buffering can produce timestamp
jitter and dropped samples. If current, acceleration and optical truth are
timestamped by unrelated processes, an apparent early-stopping benefit may be
an acquisition artifact.

The acquisition layer therefore has to expose the same command-relative timing
for policy samples while preventing the policy from reading the truth stream.

## Recommended topology

```text
Pi GPIO command pulse
        |
        +---- low-voltage switch ---- guarded 5 V motor/fan
        |
        +---- trigger input to policy-sensor MCU
        |
        +---- trigger input to independent truth logger

policy-sensor MCU:
  INA219/current stream + ADXL345 acceleration stream
  -> timestamped raw packet file/USB stream -> Pi policy process

truth logger:
  optical tachometer/photointerrupter
  -> local file or separate storage, unavailable to policy process
```

The command pulse is a common event marker. Each logger records its local tick
at the edge; a manual calibration trial estimates relative offset and jitter.
The truth logger must not share the policy process's filesystem, queue or
runtime API during a decision episode.

## Component choice

### Policy acquisition MCU

Use an inexpensive 3.3 V MCU development board with hardware timers and I2C/SPI
support, such as an RP2040-class board. It should stream raw current and
acceleration samples with sequence numbers and local monotonic ticks over USB
serial. A different board is acceptable if it can provide the same timing
fields and a reproducible firmware build.

### Current channel

Start with the INA219 module from the BOM because it is simple to wire and
provides current/voltage telemetry for the low-voltage fixture. Measure its
effective conversion/polling rate on the selected module. If it cannot resolve
the command-relative event at the preregistered rate, replace it with an
analog shunt-amplifier plus MCU ADC; do not silently interpolate a slow stream.

### Acceleration channel

Use an ADXL345-class breakout over SPI when possible, because SPI avoids some
I2C bus contention and allows a fixed sample schedule. Record range, output
data rate, axis orientation and mount identifier in the episode manifest.

### Truth channel

Use a reflective optical sensor or photointerrupter connected to a separate
timer/input-capture logger. The logger stores pulse timestamps and derives the
binary truth after the episode. A relay state can be recorded for debugging,
but it is never a substitute for mechanical truth.

## Required firmware behavior

- accept a trigger edge and reset an episode-local sample counter;
- sample current and acceleration at fixed declared rates;
- attach sequence number and MCU tick to every sample packet;
- report dropped packets and buffer overflow explicitly;
- stop after the common maximum window or an explicit abort;
- never expose optical truth packets to the Pi policy process;
- store firmware version and sensor configuration hash per run.

## Bring-up tests

1. **Trigger test:** issue 100 command pulses and verify that Pi, policy MCU
   and truth logger each record one event with bounded relative jitter.
2. **Stream test:** run the motor without policy inference and measure current,
   acceleration and optical packet rates, drops and buffer overflows.
3. **Stop test:** manually stop the rotor and confirm the optical pulse stream
   changes independently of the relay state.
4. **Isolation test:** run the policy process with the truth storage removed;
   it must still produce an action from current/acceleration alone.
5. **Offline test:** disconnect the network and verify local command, policy
   and truth files are still written to their separate locations.

## Acceptance thresholds

Before collecting research episodes, record measured values and freeze them:

- trigger count agreement: 100/100 in the trigger test;
- no unexplained sample drops in the held-out comparison;
- relative command/tick jitter reported as a measurement, not assumed zero;
- policy input rates within the declared protocol tolerance;
- truth pulse/rpm rule stable across manual start/stop trials;
- policy process has no read permission or API path to truth data.

If these thresholds cannot be met, simplify the research claim or rebuild the
instrumentation. Do not claim a short-deadline action result from unsynchronised
streams.

## Purchase impact

Add one low-cost 3.3 V MCU board to the minimum BOM. A second MCU or separate
storage for the truth logger is recommended when the first board cannot make
the truth isolation auditable. Do not buy a second motor or high-end ADC until
the bring-up tests show a real sampling limitation.

## Status

**HOLD (Amber).** Architecture is ready for hardware bring-up; no empirical
START-WIT result exists.
