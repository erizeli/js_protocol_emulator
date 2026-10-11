# Protocol Emulator ASIC

Protocol-agnostic event capture, storage, modification, and deterministic replay
for the Jane Street Tiny Tapeout competition.

The initial MVP milestone is capture → store → replay. Event modification,
protocol demonstrations, and physical integration follow later.

## Layout

- `src/`: synthesizable SystemVerilog; capture implemented; other blocks are placeholders.
- `verification/`: cocotb tests, Python model, and simulation-only harness.
- `docs/decisions.md`: active record of agreed decisions, implications, and open choices.
- `docs/mvp-contract.md`: interface and timing contracts to settle before RTL.
- `AGENTS.md`: repository working guidelines.

## Development

The first executable slice tests capture using Icarus Verilog and cocotb.
`make -C verification help` lists the simulation commands.

Before implementing a block, resolve its relevant open decisions and document
its interfaces. Implement and test one architectural block at a time. Update
`docs/decisions.md` whenever a decision is made, revised, or found to block work.

## Run the First RTL Test

The capture engine is implemented; buffer and replay remain placeholders.
The cocotb suite sends a synthetic UART frame and checks event timing against a
Python model, plus simultaneous transitions, stalls, overflow, and reset.

With Python 3.9–3.13 and Icarus Verilog 12.0 available
(this machine uses `/usr/bin/python3` for the virtual environment):

```sh
/usr/bin/python3 -m venv .venv
.venv/bin/python -m pip install -r verification/requirements.txt
make -C verification
make -C verification WAVES=1
```

Waveforms are generated under `verification/sim_build/`. Tests currently use two
pins and an eight-bit delta. This verifies sampled capture, not external pin
synchronization, event storage, or replay.
