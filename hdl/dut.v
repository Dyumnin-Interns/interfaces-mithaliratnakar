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
    output wire [7:0]  counter_out,
    output wire a_ff_EMPTY_N

);

  wire fifo_reset = ~RST_N;

  wire a_ff_enq, a_ff_deq, a_ff_clr, a_ff_full_n;
  wire [7:0] a_ff_din, a_ff_dout;

  wire b_ff_enq, b_ff_deq, b_ff_clr, b_ff_full_n, b_ff_EMPTY_N;
  wire [7:0] b_ff_din, b_ff_dout;

  wire y_ff_enq, y_ff_deq, y_ff_clr, y_ff_full_n, y_ff_EMPTY_N;
  wire [7:0] y_ff_din, y_ff_dout;

  wire a_data_whas = write_en && write_address == 3'd4;
  wire b_data_whas = write_en && write_address == 3'd5;
  wire pwyff_deq_whas = read_en && read_address == 3'd3;
 
  reg [7:0] counter;
  wire [7:0] counter_D_IN = counter + 8'd1;
  wire counter_EN = 1'b1;
  assign counter_out = counter;
  
  FIFO2 #(.width(8)) a_ff (
    .RST(fifo_reset), .CLK(CLK),
    .D_IN(a_ff_din), .ENQ(a_ff_enq), .DEQ(a_ff_deq), .CLR(a_ff_clr),
    .D_OUT(a_ff_dout), .FULL_N(a_ff_full_n), .EMPTY_N(a_ff_EMPTY_N)
  );

  FIFO1 #(.width(8)) b_ff (
    .RST(fifo_reset), .CLK(CLK),
    .D_IN(b_ff_din), .ENQ(b_ff_enq), .DEQ(b_ff_deq), .CLR(b_ff_clr),
    .D_OUT(b_ff_dout), .FULL_N(b_ff_full_n), .EMPTY_N(b_ff_EMPTY_N)
  );

  FIFO2 #(.width(8)) y_ff (
    .RST(fifo_reset), .CLK(CLK),
    .D_IN(y_ff_din), .ENQ(y_ff_enq), .DEQ(y_ff_deq), .CLR(y_ff_clr),
    .D_OUT(y_ff_dout), .FULL_N(y_ff_full_n), .EMPTY_N(y_ff_EMPTY_N)
  );

  assign write_rdy = 1'b1;
  assign read_rdy  = 1'b1;

  assign a_ff_din = write_data;
  assign a_ff_enq = a_ff_full_n && a_data_whas;
  assign a_ff_deq = read_en && read_address == 3'd0 && a_ff_EMPTY_N;
  assign a_ff_clr = 1'b0;

  assign b_ff_din = write_data;
  assign b_ff_enq = b_ff_full_n && b_data_whas;
  assign b_ff_deq = y_ff_full_n && a_ff_EMPTY_N && b_ff_EMPTY_N && counter == 8'd50;
  assign b_ff_clr = 1'b0;

  assign y_ff_din = a_ff_dout | b_ff_dout;
  assign y_ff_enq = y_ff_full_n && a_ff_EMPTY_N && b_ff_EMPTY_N && counter == 8'd50;
  assign y_ff_deq = y_ff_EMPTY_N && pwyff_deq_whas;
  assign y_ff_clr = 1'b0;

  always @(*) begin
  case (read_address)
    3'd0:    read_data = {7'b0, a_ff_full_n}; 
    3'd1:    read_data = {7'b0, b_ff_full_n};
    3'd2:    read_data = {7'b0, y_ff_EMPTY_N};
    3'd3:    read_data = y_ff_EMPTY_N ? y_ff_dout : 8'd0;  
    default: read_data = 8'd0;
  endcase
end

  always @(posedge CLK or `BSV_RESET_EDGE RST_N) begin
    if (RST_N == `BSV_RESET_VALUE)
      counter <= `BSV_ASSIGNMENT_DELAY 8'd0;
    else if (counter_EN)
      counter <= `BSV_ASSIGNMENT_DELAY counter_D_IN;
  end

  `ifndef BSV_NO_INITIAL_BLOCKS
  initial begin
    counter = 8'hAA;
  end
  `endif

endmodule
