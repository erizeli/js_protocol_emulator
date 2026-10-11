# Decision Log

Maintain this file throughout development. Record each decision's status,
rationale, implications, and any superseding decision. Recommendations are
not accepted decisions. Resolve relevant open entries before implementing RTL.

## Accepted

### D01 — Protocol-agnostic events

Source: `AGENTS.md`. Events contain `delta_time`, `pin_mask`, and `pin_value`.
Protocol interpretation belongs outside the core event path. Field widths and
exact timing semantics remain open (O01).

### D02 — RTL and interface conventions

Source: `AGENTS.md`. Use synthesizable, vendor-independent SystemVerilog,
ready/valid streaming interfaces, and synchronous active-low reset.
Simulation-only constructs belong in `verification/`. Capture must explicitly
handle transitions arriving while its output is stalled (O03).

### D03 — Verification and area constraints

Source: `AGENTS.md`. Use cocotb and a Python reference model, standalone block
tests, and cycle-accurate replay checks. Target Tiny Tapeout IHP CMOS5L and
favor small storage and simple datapaths; discuss area implications before
adding large structures.

### D04 — Initial milestone and scaffold

Source: approved MVP setup plan. Begin with capture → store → replay and shared
event definitions. Defer event processing, protocol demonstrations, and physical
integration. This scaffold supplies documentation only, without RTL behavior
or runnable verification.

## Open Decisions

### O01 — Event representation and time

Choose pin count, delta width, clock-cycle units, first-event baseline,
simultaneous-transition encoding, and zero-delta legality. These choices affect
every block and the reference model; resolve before defining `event_t`.

### O02 — Input sampling

Choose the capture input contract and synchronization ownership. Recommended:
capture accepts synchronized samples; a later frontend handles external pins.
Document synchronization latency and minimum observable pulse duration.

### O03 — Capture stalls and long idle intervals

Choose buffering and overflow behavior when output is stalled, plus delta-counter
overflow behavior. Physical inputs cannot obey backpressure. Specify whether
capture stops or loses events and how software observes the error.

### O04 — Storage organization

Choose depth, consuming FIFO versus retained sequence, read latency, full/empty
behavior, and capture/replay concurrency. Recommended: small retained storage
with separate capture and replay phases. Estimate area before selecting depth.

### O05 — Replay schedule

Choose start-cycle semantics, initial output state, masked updates, prefetch,
completion, and underrun behavior. Stream stalls must not silently alter timing.
Resolve how output drive enables are represented for eventual pin integration.

### O06 — Control and sequence boundaries

Define clear, capture start/stop, replay start, busy, done, error reporting,
reset state, and recorded-length/end-of-sequence signaling. Decide how invalid
or overlapping commands behave and how initial pin state is retained.

### O07 — Verification toolchain

Select a compatible simulator and pin Python/cocotb versions. Establish block
and integration commands, compile order, and CI after runnable tests exist.

## Recording Future Decisions

For each resolved entry, add an accepted decision with rationale and implications,
mark the open entry resolved with its decision ID, and update `mvp-contract.md`.
Keep superseded decisions for context; do not silently erase prior agreements.

## First Executable Slice — 2026-10-11

### D05 — Capture-only simulation milestone

Implementation choice under the requested RTL/test work: first verify capture
with a Python-generated UART 8N1 frame (0xA5, eight core cycles per bit).
Buffer and replay remain placeholders; this milestone does not verify replay.
No physical UART baud rate or final chip clock is selected.

### D06 — Initial capture contract

Use two pins and an eight-bit delta for the simulation MVP, defined in
`event_pkg.sv`. Capture receives synchronous samples; external synchronization
is deferred. Start samples a baseline; the next edge is cycle 1. Each transition
records a positive cycle delta, XOR mask, and full new sample. Simultaneous
changes produce one event. These resolve O01/O02 for this slice only.

A single output slot holds payload stable until handshake. A handshake and new
transition may occur together. If a blocked slot receives another transition,
capture stops with sticky overflow while retaining the pending event. A gap of
256 cycles also stops capture, even without a transition; a transition at 255
cycles is legal. This resolves O03 for this slice without extra storage.

Reset clears all state. Start is accepted only while inactive with no pending
event, and clears overflow. Stop suppresses capture on its edge but does not
discard pending output. Reset has highest priority, then accepted start, stop,
and capture. Repeated start while active is ignored. These partially resolve
O06; full sequence metadata and buffer/replay control remain open.

### D07 — Initial simulation toolchain

Use Icarus Verilog 12.0 and cocotb 2.0.1 in a repository-local virtual environment.
Use Python 3.9–3.13; the default Python 3.14 is incompatible with this cocotb pin.
On this machine the environment is created with `/usr/bin/python3`.
The capture test runner follows cocotb's Makefile interface:
https://docs.cocotb.org/en/v2.0.0/quickstart.html
O07 is resolved for capture simulation; CI and other block targets are deferred.
