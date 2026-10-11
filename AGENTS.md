Project:
Jane Street Tiny Tapeout protocol-emulator ASIC competition.

Goal:
Build a protocol-agnostic programmable event processor that:
1. captures pin transitions as delta-time events,
2. stores events,
3. allows events to be modified,
4. replays them deterministically,
5. demonstrates UART/SPI/I2C behavior.

Event representation:
event_t = {
    delta_time,
    pin_mask,
    pin_value
}

Initial architecture:
pins
→ pin_frontend
→ capture_engine
→ event_buffer
→ event_processor
→ replay_engine
→ pins

RTL:
- SystemVerilog
- synthesizable RTL only unless explicitly in verification/
- avoid vendor-specific constructs
- use ready/valid interfaces between streaming blocks
- synchronous active-low reset unless documented otherwise
- parameterize widths where useful, but avoid premature abstraction

Verification:
- cocotb + Python reference model
- each RTL module should have standalone unit tests
- cycle-accurate replay timing must be checked
- capture and replay should be independently testable

Physical-design constraints:
- Tiny Tapeout IHP CMOS5L
- area is constrained
- prioritize simple datapaths and small storage
- do not add large structures without discussing area implications

Workflow:
- do not modify multiple architectural blocks at once unless asked
- explain proposed interface changes before applying them
- preserve existing passing tests
- add tests for new functionality
  