`ifdef BSV_ASSIGNMENT_DELAY
`else
  `define BSV_ASSIGNMENT_DELAY
`endif

`ifdef BSV_POSITIVE_RESET
  `define BSV_RESET_VALUE 1'b1
  `define BSV_RESET_EDGE posedge
`else
  `define BSV_RESET_VALUE 1'b0
  `define BSV_RESET_EDGE negedge
`endif

module dut (
    input  wire        CLK,
    input  wire        RST_N,
    input  wire [2:0]  write_address,
    input  wire [7:0]  write_data,
    input  wire        write_en,
    output wire        write_rdy,
    input  wire [2:0]  read_address,
    input  wire        read_en,
    output reg  [7:0]  read_data,
    output wire        read_rdy,
    output wire [7:0]  counter_out
);

  // FIFO reset
  wire fifo_reset = ~RST_N;

  // FIFO1 and FIFO2 wires
  wire a_ff_enq, a_ff_deq, a_ff_clr, a_ff_full_n, a_ff_empty_n;
  wire [7:0] a_ff_din, a_ff_dout;

  wire b_ff_enq, b_ff_deq, b_ff_clr, b_ff_full_n, b_ff_empty_n;
  wire [7:0] b_ff_din, b_ff_dout;

  wire y_ff_enq, y_ff_deq, y_ff_clr, y_ff_full_n, y_ff_empty_n;
  wire [7:0] y_ff_din, y_ff_dout;

  // Internal signals
  wire a_data$whas = write_en && write_address == 3'd0;
  wire b_data$whas = write_en && write_address == 3'd5;
  wire pwyff_deq$whas = read_en && read_address == 3'd3;

  // Counter
  reg [7:0] counter;
  wire [7:0] counter$D_IN = counter + 8'd1;
  wire counter$EN = 1'b1;
  assign counter_out = counter;

  // FIFOs
  FIFO2 #(.width(8)) a_ff (
    .RST(fifo_reset), .CLK(CLK),
    .D_IN(a_ff_din), .ENQ(a_ff_enq), .DEQ(a_ff_deq), .CLR(a_ff_clr),
    .D_OUT(a_ff_dout), .FULL_N(a_ff_full_n), .EMPTY_N(a_ff_empty_n)
  );

  FIFO1 #(.width(8)) b_ff (
    .RST(fifo_reset), .CLK(CLK),
    .D_IN(b_ff_din), .ENQ(b_ff_enq), .DEQ(b_ff_deq), .CLR(b_ff_clr),
    .D_OUT(b_ff_dout), .FULL_N(b_ff_full_n), .EMPTY_N(b_ff_empty_n)
  );

  FIFO2 #(.width(8)) y_ff (
    .RST(fifo_reset), .CLK(CLK),
    .D_IN(y_ff_din), .ENQ(y_ff_enq), .DEQ(y_ff_deq), .CLR(y_ff_clr),
    .D_OUT(y_ff_dout), .FULL_N(y_ff_full_n), .EMPTY_N(y_ff_empty_n)
  );

  // Ready signals
  assign write_rdy = 1'b1;
  assign read_rdy  = 1'b1;

  // Write logic
  assign a_ff_din = write_data;
  assign a_ff_enq = a_ff_full_n && a_data$whas;
  assign a_ff_deq = read_en && read_address == 3'd0 && a_ff_empty_n;
  assign a_ff_clr = 1'b0;

  assign b_ff_din = write_data;
  assign b_ff_enq = b_ff_full_n && b_data$whas;
  assign b_ff_deq = y_ff_full_n && a_ff_empty_n && b_ff_empty_n && counter == 8'd50;
  assign b_ff_clr = 1'b0;

  assign y_ff_din = a_ff_dout | b_ff_dout;
  assign y_ff_enq = y_ff_full_n && a_ff_empty_n && b_ff_empty_n && counter == 8'd50;
  assign y_ff_deq = y_ff_empty_n && pwyff_deq$whas;
  assign y_ff_clr = 1'b0;

  // Read logic
  always @(*) begin
    case (read_address)
      3'd0:    read_data = a_ff_dout;
      3'd1:    read_data = b_ff_dout;
      3'd2:    read_data = {7'b0, y_ff_empty_n};
      3'd3:    read_data = y_ff_dout;
      default: read_data = 8'd0;
    endcase
  end

  // Counter logic
  always @(posedge CLK or `BSV_RESET_EDGE RST_N) begin
    if (RST_N == `BSV_RESET_VALUE)
      counter <= `BSV_ASSIGNMENT_DELAY 8'd0;
    else if (counter$EN)
      counter <= `BSV_ASSIGNMENT_DELAY counter$D_IN;
  end

  `ifndef BSV_NO_INITIAL_BLOCKS
  initial begin
    counter = 8'hAA;
  end
  `endif

endmodule
