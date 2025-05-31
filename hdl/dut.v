module dut(
    input  wire        CLK,
    input  wire        RST_N,

    // Write interface
    input  wire [2:0]  write_address,
    input  wire        write_data,
    input  wire        write_en,
    output wire        write_rdy,

    // Read interface
    input  wire [2:0]  read_address,
    input  wire        read_en,
    output reg         read_data,
    output wire        read_rdy
);

  FIFO2 #(
    .width(1),
    .guarded(1'b1)  
  ) a_ff(
    .RST(fifo_reset),
    .CLK(CLK),
    .D_IN(a_ff_din),
    .ENQ(a_ff_enq),
    .DEQ(a_ff_deq),
    .CLR(a_ff_clr),
    .D_OUT(a_ff_dout),
    .FULL_N(a_ff_full_n),
    .EMPTY_N(a_ff_empty_n)
  );

  FIFO1 #(
    .width(1),
    .guarded(1'b1)  // Explicitly set guarded parameter
  ) b_ff(
    .RST(fifo_reset),
    .CLK(CLK),
    .D_IN(b_ff_din),
    .ENQ(b_ff_enq),
    .DEQ(b_ff_deq),
    .CLR(b_ff_clr),
    .D_OUT(b_ff_dout),
    .FULL_N(b_ff_full_n),
    .EMPTY_N(b_ff_empty_n)
  );

  FIFO2 #(
    .width(1),
    .guarded(1'b1)  
  ) y_ff(
    .RST(fifo_reset),
    .CLK(CLK),
    .D_IN(y_ff_din),
    .ENQ(y_ff_enq),
    .DEQ(y_ff_deq),
    .CLR(y_ff_clr),
    .D_OUT(y_ff_dout),
    .FULL_N(y_ff_full_n),
    .EMPTY_N(y_ff_empty_n)
  );

endmodule
