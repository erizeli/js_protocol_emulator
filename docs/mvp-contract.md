# MVP Contract

Status: capture interface implemented below; buffer and replay contracts pending.
See `decisions.md` for accepted requirements and open choices.

## Shared Events

An event carries elapsed time, a changed-pin mask, and pin values. Before defining
the packed type, specify widths, time units, initial state, and zero/overflow rules
(O01, O06).

## Block Boundaries

- Capture: sampled pins and control → ready/valid events; sampling and loss
  behavior require O02–O03.
- Buffer: event input → stored event output; capacity, read latency, sequence
  boundaries, and retention require O04 and O06.
- Replay: events and start control → timed pin values; scheduling, drive enables,
  completion, and underrun require O05–O06.

For each stream, document payload stability under stall and the exact transfer
edge. Document reset values and control-command priority before implementation.

## Verification Acceptance

Each block needs independent cocotb tests. Integration must compare captured
events and replayed pin transitions with the Python model at exact clock cycles.
Cover reset, masked updates, boundary deltas, full/empty storage, stalls, and
error paths once their expected behavior is agreed.

## Implemented Capture Interface

See decisions D05–D07. `clk` samples on rising edges; `rst_n` is synchronous.
`pins[1:0]` must already be synchronous. `start` establishes `initial_value`;
`stop` ends sampling without flushing output. `active` reports sampling state;
`overflow` is sticky until reset or an accepted start.

`event_valid`/`event_ready` transfer the separate `event_delta[7:0]`,
`event_mask[1:0]`, and `event_value[1:0]` fields on a rising edge. Payload stays
stable while stalled. A newly captured event becomes visible after its capture
edge and can transfer on the next edge. Its delta measures sample time, not
handshake time. The shared packed type defines the format; separate field ports
keep the initial simulation interface straightforward.

The baseline is retained separately. Zero-delta events are not emitted. A
255-cycle transition is legal; the following cycle without a prior transition
causes overflow. Stop takes priority over recording a transition on that edge.
