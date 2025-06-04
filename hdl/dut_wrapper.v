module dut_wrapper (
    input wire CLK,
    input wire RST,
    input wire [0:0] DATA_IN,     
    input wire WR_EN,
    input wire RD_EN,
    input wire CLR,
    output wire [0:0] DATA_OUT,
    output wire EMPTY,
    output wire FULL
);

    FIFO1 #(.width(1)) fifo_inst (
        .CLK(CLK),
        .RST(RST),
        .D_IN(DATA_IN),
        .ENQ(WR_EN),
        .DEQ(RD_EN),
        .CLR(CLR),
        .D_OUT(DATA_OUT),
        .EMPTY_N(EMPTY),
        .FULL_N(FULL)
    );

    initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, dut_wrapper);
    end

endmodule
