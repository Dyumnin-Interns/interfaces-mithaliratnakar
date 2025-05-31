`timescale 1ns/1ps

module dut_wrapper(
    input wire clk,
    input wire reset_n,
    input wire [2:0] write_addr,
    input wire write_data,
    input wire write_en,
    output wire write_ready,
    
    input wire [2:0] read_addr,
    input wire read_en,
    output wire read_data,
    output wire read_ready
);
  
    dut dut_inst (
        .CLK(clk),
        .RST_N(reset_n),
        
        .write_address(write_addr),
        .write_data(write_data),
        .write_en(write_en),
        .write_rdy(write_ready),
        
        .read_address(read_addr),
        .read_en(read_en),
        .read_data(read_data),
        .read_rdy(read_ready)
    );

    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, dut_wrapper);
    end

endmodule
