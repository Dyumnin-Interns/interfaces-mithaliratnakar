module dut_wrapper (
    input wire CLK,
    input wire RST_N,
    input wire [2:0] write_address,
    input wire write_data,
    input wire write_en,
    output wire write_rdy,
    input wire [2:0] read_address,
    input wire read_en,
    output wire read_data,
    output wire read_rdy,
    output wire a_ff_dout,
    output wire b_ff_dout,
    output wire y_ff_dout
);
  dut dut_inst (
      .CLK(CLK),
      .RST_N(RST_N),
      .write_address(write_address),
      .write_data(write_data),
      .write_en(write_en),
      .write_rdy(write_rdy),
      .read_address(read_address),
      .read_en(read_en),
      .read_data(read_data),
      .read_rdy(read_rdy)
  );
  assign a_ff_dout = dut_inst.a_ff$D_OUT;
  assign b_ff_dout = dut_inst.b_ff$D_OUT;
  assign y_ff_dout = dut_inst.y_ff$D_OUT;
initial begin
  $dumpfile("waveform.vcd");
  $dumpvars(0, dut_wrapper);
end
endmodule
