`timescale 1ns/1ps
module capture_engine (
  input logic clk,
  input logic rst_n, // Active-low synchronous reset: 0 resets on a rising edge.
  input logic start, // Active-high request: 1 requests a new capture session.
  input logic stop,  // Active-high request: 1 stops sampling.
  input logic [event_pkg::PIN_COUNT-1:0] pins,
  input logic event_ready,
  output logic event_valid,
  output logic [event_pkg::DELTA_WIDTH-1:0] event_delta,
  output logic [event_pkg::PIN_COUNT-1:0] event_mask,
  output logic [event_pkg::PIN_COUNT-1:0] event_value,
  output logic [event_pkg::PIN_COUNT-1:0] initial_value,
  output logic active,
  output logic overflow
);
  import event_pkg::*;
  logic [PIN_COUNT-1:0] previous;
  logic [DELTA_WIDTH-1:0] elapsed;

  // elapsed counts unchanged samples since the last transition/baseline.
  // A transition on the next edge therefore has delta=1.
  always_ff @(posedge clk) begin
    // Reset has highest priority. !rst_n is true when rst_n is 0.
    if (!rst_n) begin
      previous <= '0;
      elapsed <= '0;
      initial_value <= '0;
      active <= 1'b0;
      overflow <= 1'b0;
      event_valid <= 1'b0;
      event_delta <= '0;
      event_mask <= '0;
      event_value <= '0;
    end else begin
      // Normal operation when reset is released (rst_n=1).
      // Both high means the receiver accepts the pending event on this edge.
      // Clear valid unless a new transition below replaces that event.
      if (event_valid && event_ready) event_valid <= 1'b0;
      // Start=1 requests capture; !active means we are currently idle.
      // Accept only with an empty slot, so an earlier event is not discarded.
      // Conditions read pre-edge state: a slot consumed above is not yet empty.
      if (start && !active && !event_valid) begin
        previous <= pins;
        initial_value <= pins;
        elapsed <= '0;
        overflow <= 1'b0;
        active <= 1'b1;
      end else if (stop) begin
        // Stop=1 ends sampling, but preserves any pending output event.
        // An accepted start above takes priority if both requests are high.
        active <= 1'b0;
      end else if (active) begin
        // Sample pins only while a capture session is active.
        // &elapsed is a reduction AND: true when every counter bit is 1.
        // The next delta would exceed the maximum, so stop instead of wrapping.
        if (&elapsed) begin
          overflow <= 1'b1;
          active <= 1'b0;
        end else if (pins != previous) begin
          // At least one sampled pin changed: we need to emit one event.
          // A valid event with ready=0 still occupies the only output slot.
          if (event_valid && !event_ready) begin
            // We cannot retain this new transition. Flag loss and stop capture;
            // leave the older event and its valid flag intact for the receiver.
            overflow <= 1'b1;
            active <= 1'b0;
          end else begin
            // The slot is empty or its previous event transfers on this edge.
            // Store the new event; the later valid assignment wins if the
            // handshake above also scheduled valid to clear on this edge.
            event_delta <= elapsed + 1'b1;
            event_mask <= pins ^ previous;
            event_value <= pins;
            event_valid <= 1'b1;
            previous <= pins;
            elapsed <= '0;
          end
        end else begin
          // Pins are unchanged. Count another cycle toward the next delta.
          elapsed <= elapsed + 1'b1;
        end
      end
      // If idle with no accepted command, capture state holds its value.
      // The independent output handshake above may still drain a pending event.
    end
  end
endmodule
