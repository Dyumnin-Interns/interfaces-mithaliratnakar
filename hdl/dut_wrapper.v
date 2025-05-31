module dut_wrapper(
    input  wire        clk,
    input  wire        reset_n,  // Active-low
    input  wire [2:0]  write_address,
    input  wire        write_data,
    input  wire        write_en,
    output wire        write_rdy,
    input  wire [2:0]  read_address,
    input  wire        read_en,
    output wire        read_data,
    output wire        read_rdy
);
    dut dut_inst (
        .CLK(clk),
        .RST_N(reset_n),  // Active-low
        .write_address(write_address),
        .write_data(write_data),
        .write_en(write_en),
        .write_rdy(write_rdy),
        .read_address(read_address),
        .read_en(read_en),
        .read_data(read_data),
        .read_rdy(read_rdy)
    );
endmodule

initial begin
    $dumpfile("waveform.vcd");  // Saves in sim_build/
    $dumpvars(0, dut_wrapper);  // Dump all signals
end
