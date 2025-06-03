module dut_wrapper (
    input  wire          CLK,
    input  wire          RST,
    input  wire          CLR,
    input  wire          FIFO1_ENQ,
    input  wire          FIFO1_DEQ,
    input  wire [7:0]    FIFO1_D_IN,
    output wire          FIFO1_FULL_N,
    output wire          FIFO1_EMPTY_N,
    output wire [7:0]    FIFO1_D_OUT,
    input  wire          FIFO2_ENQ,
    input  wire          FIFO2_DEQ,
    input  wire [7:0]    FIFO2_D_IN,
    output wire          FIFO2_FULL_N,
    output wire          FIFO2_EMPTY_N,
    output wire [7:0]    FIFO2_D_OUT
);
    FIFO1 #(
        .width(8)
    ) fifo1_inst (
        .CLK(CLK),
        .RST(RST),
        .CLR(CLR),
        .ENQ(FIFO1_ENQ),
        .DEQ(FIFO1_DEQ),
        .D_IN(FIFO1_D_IN),
        .FULL_N(FIFO1_FULL_N),
        .EMPTY_N(FIFO1_EMPTY_N),
        .D_OUT(FIFO1_D_OUT)
    );
    FIFO2 #(
        .width(8)
    ) fifo2_inst (
        .CLK(CLK),
        .RST(RST),
        .CLR(CLR),
        .ENQ(FIFO2_ENQ),
        .DEQ(FIFO2_DEQ),
        .D_IN(FIFO2_D_IN),
        .FULL_N(FIFO2_FULL_N),
        .EMPTY_N(FIFO2_EMPTY_N),
        .D_OUT(FIFO2_D_OUT)
    );

  initial begin
    $dumpfile("waveform.vcd");
    $dumpvars(0, dut_wrapper);
  end

endmodule
