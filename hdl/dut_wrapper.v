module dut_wrapper (
    input wire CLK,
    input wire RST,
    input wire [7:0] DATA_IN,
    input wire WR_EN,
    input wire RD_EN,
    input wire CLR,
    output wire [7:0] DATA_OUT,
    output wire EMPTY,
    output wire FULL
);
    wire full_n, empty_n;

    FIFO1 #(.width(8)) fifo_inst (
        .CLK(CLK),
        .RST(RST_N),
        .D_IN(DATA_IN),
        .ENQ(WR_EN),
        .DEQ(RD_EN),
        .CLR(CLR),
        .D_OUT(DATA_OUT),
        .EMPTY_N(empty_n),
        .FULL_N(full_n)
    );

    assign EMPTY = ~empty_n;
    assign FULL  = ~full_n;

initial begin
        $dumpfile("waveform.vcd");
        $dumpvars(0, dut_wrapper);
    end

endmodule
