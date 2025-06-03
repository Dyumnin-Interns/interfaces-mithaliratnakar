module dut_wrapper (
  input CLK,
  input RST_N,
  input [2:0] write_address,
  input [7:0] write_data,
  input write_en,
  output write_rdy,
  input [2:0] read_address,
  input read_en,
  output [7:0] read_data,
  output read_rdy,
  output [7:0] counter_out,
  output a_ff_EMPTY_N
);

  wire [7:0] internal_read_data;
  wire internal_read_rdy;
  wire internal_write_rdy;
  wire [7:0] internal_counter_out;
  wire a_ff_EMPTY_N_internal;

  dut u_dut (
    .CLK(CLK),
    .RST_N(RST_N),
    .write_address(write_address),
    .write_data(write_data),
    .write_en(write_en),
    .write_rdy(internal_write_rdy),
    .read_address(read_address),
    .read_en(read_en),
    .read_data(internal_read_data),
    .read_rdy(internal_read_rdy),
    .counter_out(internal_counter_out),
    .a_ff_EMPTY_N(a_ff_EMPTY_N_internal)
  );

  assign a_ff_EMPTY_N = a_ff_EMPTY_N_internal;

  assign read_data = internal_read_data;
  assign read_rdy = internal_read_rdy;
  assign write_rdy = internal_write_rdy;
  assign counter_out = internal_counter_out;

endmodule


initial begin
    $dumpfile("waveform.vcd");
    $dumpvars(0, dut_wrapper);
end

endmodule

