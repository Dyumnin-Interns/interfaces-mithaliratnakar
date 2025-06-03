module dut_wrapper (
    input clk,
    input reset_n,
    input write_en,
    input [2:0] write_address,
    input [7:0] write_data,
    input read_en,
    input [2:0] read_address,
    output [7:0] read_data,
    output [7:0] counter_out  
);

dut u_dut (
    .CLK(clk),
    .RST_N(reset_n),
    .write_en(write_en),
    .write_address(write_address),
    .write_data(write_data),
    .read_en(read_en),
    .read_address(read_address),
    .read_data(read_data),
    .counter_out(counter_out)
);

initial begin
    $dumpfile("waveform.vcd");
    $dumpvars(0, dut_wrapper);
end

endmodule

