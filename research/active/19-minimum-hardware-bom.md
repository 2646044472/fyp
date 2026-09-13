# START-WIT Minimum Hardware BOM

> **Superseded (KILL, 2026-09-03):** do not procure these parts as a thesis
> gate. This is retained only for a future bounded control/replication.

## Purpose

This is a feasibility-gate bill of materials, not a claim that the parts make
the direction novel. Buy only the items needed to establish independent truth,
repeatable episodes and simple baselines.

## Buy or obtain first

| Item | Minimum specification | Role | Required? |
|---|---|---|---|
| Raspberry Pi 5B | Existing 8 GB board | Edge decision, local log and offline/online timing | Existing |
| 3.3 V MCU development board | RP2040-class or equivalent with hardware timers and I2C/SPI | Deterministic policy-sensor acquisition and trigger timestamping | Recommended for final timing; Pi-only is bring-up only |
| 5 V DC fan or small DC motor | Low-voltage, guarded rotor, replaceable load | Benign actuator fixture | Yes |
| INA219 breakout | I2C current/voltage monitor; choose a shunt/module rated above the fixture current | Electrical policy observation for bring-up; final use depends on measured effective sample rate | Yes |
| ADXL345 or equivalent | Digital 3-axis accelerometer with I2C/SPI breakout | Mechanical policy observation | Yes |
| Optical tachometer or photointerrupter | Detects a marked rotating surface independently of motor current | Mechanical truth label | Yes |
| Low-voltage switch/relay | Rated for the selected 5 V load | Issues the start command | Yes |
| Emergency stop and guard | Physically disconnects the low-voltage actuator and covers moving parts | Safety | Yes |
| Rigid base and removable load/brake | Supports remount and held-out load cells | Experimental variation | Yes |
| Reflective tape or slotted wheel | Clear optical target | Tachometer signal | Yes |
| USB inline power meter | Measures Pi/system energy if available | Cost accounting | Optional but useful |

## Compatibility checks

- The INA219 supports an I2C/SMBus digital interface and a 0-26 V common-mode
  range according to TI's product documentation. Select the breakout's shunt
  and current rating from the actual fan/motor current; do not assume every
  inexpensive module is interchangeable.
- Freeze the INA219 conversion mode, averaging, shunt and effective sample
  rate during bring-up. It is not a current waveform recorder by default. If
  measured command-relative timing is inadequate, use an analog shunt-amplifier
  plus MCU ADC or remove current from the positive mechanism claim.
- The ADXL345 supports I2C or SPI, selectable ranges up to +/-16 g and output
  data rates up to 3200 Hz in the official datasheet. Use a 3.3 V-compatible
  breakout and start at a moderate rate; the experiment needs repeatable
  vibration prefixes, not maximum bandwidth.
- Raspberry Pi GPIO is 3.3 V logic. Use GPIO2/GPIO3 for the standard I2C bus,
  and never connect a 5 V sensor output directly to a GPIO input. Power the
  motor separately from the Pi logic rail, with a common ground only where the
  module wiring requires it.
- The tachometer signal must be physically independent: it measures rotation
  or a mechanical marker, not the relay command and not the current waveform.
  If a photointerrupter output is not 3.3 V-safe, add an appropriate level
  shifter or interface circuit.

## Wiring principle

Keep three paths separate in the experiment log:

1. **Command path:** Pi GPIO -> low-voltage switch/relay -> motor power.
2. **Policy path:** INA219 and accelerometer -> Pi acquisition process.
3. **Truth path:** optical sensor -> separate GPIO/input capture or a small
   microcontroller, with its result withheld from the policy process.

For final short-window timing, prefer the MCU acquisition architecture in
[24-start-wit-acquisition-architecture.md](24-start-wit-acquisition-architecture.md).
The Pi-only path is a bring-up comparison until trigger jitter, sample rate and
drop behavior are measured.

Record a common command timestamp, sensor timestamps and truth timestamps. A
relay state is not sufficient as mechanical truth because it only proves that
the electrical command was issued.

## Do not buy yet

- higher-resolution cameras or a larger neural model;
- mains-voltage equipment;
- multiple motor types before the first fixture works;
- a 3D enclosure as a proposed contribution;
- a lux sensor or cloud service, unless the experiment explicitly adds a
  measured network/optical condition that needs it.

## First acceptance test

Before collecting research data, pass these checks:

1. A manual start/stop trial produces a stable optical pulse truth signal.
2. The current and acceleration streams show command-relative timestamps.
3. The Pi can store an episode while disconnected from the network.
4. Removing or changing the load changes the physical condition without
   changing the truth sensor or its label-generation mechanism.
5. The policy process cannot read the tachometer/relay truth channel.

Failure of any item is a hardware/instrumentation blocker, not evidence for a
new algorithm. Fix the measurement setup before collecting episodes.

## Official references

- TI, INA219 product page and datasheet: https://www.ti.com/product/INA219
- Analog Devices, ADXL345 datasheet: https://www.analog.com/media/en/technical-documentation/data-sheets/adxl345.pdf
- Raspberry Pi documentation, GPIO and I2C voltage/interface guidance: https://www.raspberrypi.com/documentation/computers/raspberry-pi.html

## Status

**Procurement gate only.** This list supports the `START-WIT` preflight and
does not lock the thesis direction.
