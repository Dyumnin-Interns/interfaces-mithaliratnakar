module dut_wrapper(
    input  wire        clk,
    input  wire        reset_n,
    input  wire [2:0]  write_address,
    input  wire [7:0]  write_data, 
    input  wire        write_en,
    output wire        write_rdy,
    input  wire [2:0]  read_address,
    input  wire        read_en,
    output wire [7:0]  read_data,  
    output wire        read_rdy
);
    dut dut_inst (
        .CLK(clk),
        .RST_N(reset_n),
        .write_address(write_address),
        .write_data(write_data), 
        .write_en(write_en),
        .write_rdy(write_rdy),
        .read_address(read_address),
        .read_en(read_en),
        .read_data(read_data),   
        .read_rdy(read_rdy)
    );
    
    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, dut_wrapper);
    end
endmodule
