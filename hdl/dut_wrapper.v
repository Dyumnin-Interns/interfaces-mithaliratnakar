module dut_wrapper (
    input wire CLK,
    input wire RST,
    input wire [7:0] DATA_IN,
    input wire WR_EN,
    input wire RD_EN,
    output wire [7:0] DATA_OUT,
    output wire EMPTY,
    output wire FULL
);

    
    FIFO1 fifo_inst (
        .clk(CLK),
        .rst(RST),
        .data_in(DATA_IN),
        .wr_en(WR_EN),
        .rd_en(RD_EN),
        .data_out(DATA_OUT),
        .empty(EMPTY),
        .full(FULL)
    );

endmodule


  initial begin
    $dumpfile("waveform.vcd");
    $dumpvars(0, dut_wrapper);
  end

endmodule
