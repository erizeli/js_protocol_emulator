`timescale 1ns/1ps
package event_pkg;
  // MVP sizes, not final physical-design requirements.
  localparam integer PIN_COUNT = 2;
  localparam integer DELTA_WIDTH = 8;
  typedef struct packed {
    logic [DELTA_WIDTH-1:0] delta_time;
    logic [PIN_COUNT-1:0] pin_mask;
    logic [PIN_COUNT-1:0] pin_value;
  } event_t;
endpackage
