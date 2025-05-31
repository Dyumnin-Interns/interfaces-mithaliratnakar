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

module delayed_dut (
  input  wire         CLK,
  input  wire         RST_N,

  input  wire [2:0]   write_address,
  input  wire         write_data,
  input  wire         write_en,
  output wire         write_rdy,

  input  wire [2:0]   read_address,
  input  wire         read_en,
  output reg          read_data,
  output wire         read_rdy
);

  wire a_ff_CLR, a_ff_ENQ, a_ff_DEQ;
  wire b_ff_CLR, b_ff_ENQ, b_ff_DEQ;
  wire y_ff_CLR, y_ff_ENQ, y_ff_DEQ;

  wire a_ff_FULL_N, a_ff_EMPTY_N;
  wire b_ff_FULL_N, b_ff_EMPTY_N;
  wire y_ff_FULL_N, y_ff_EMPTY_N;

  wire a_ff_D_IN, a_ff_D_OUT;
  wire b_ff_D_IN, b_ff_D_OUT;
  wire y_ff_D_IN, y_ff_D_OUT;

  reg [7:0] counter;
  wire [7:0] counter_D_IN;
  wire counter_EN;

  assign write_rdy = 1'b1;
  assign read_rdy = 1'b1;

  wire write_a = write_en && (write_address == 3'd4);
  wire write_b = write_en && (write_address == 3'd5);

  wire read_y = read_en && (read_address == 3'd3);

  assign counter_D_IN = counter + 8'd1;
  assign counter_EN = 1'b1;

  assign a_ff_D_IN = write_data;

  assign a_ff_ENQ = a_ff_FULL_N && write_a;
  assign a_ff_DEQ = y_ff_FULL_N && a_ff_EMPTY_N && b_ff_EMPTY_N && (counter == 8'd50);
  assign a_ff_CLR = 1'b0;

  assign b_ff_D_IN = write_data;
  assign b_ff_ENQ = b_ff_FULL_N && write_b;
  assign b_ff_DEQ = y_ff_FULL_N && a_ff_EMPTY_N && b_ff_EMPTY_N && (counter == 8'd50);
  assign b_ff_CLR = 1'b0;

  assign y_ff_D_IN = a_ff_D_OUT || b_ff_D_OUT;
  assign y_ff_ENQ = y_ff_FULL_N && a_ff_EMPTY_N && b_ff_EMPTY_N && (counter == 8'd50);
  // Dequeue when FIFO is not empty and read_y is asserted
  assign y_ff_DEQ = y_ff_EMPTY_N && read_y;
  assign y_ff_CLR = 1'b0;

  // Instantiate FIFO modules
  FIFO2 #(.width(1), .guarded(1'b1)) a_ff (
    .CLK(CLK),
    .RST(RST_N),
    .D_IN(a_ff_D_IN),
    .ENQ(a_ff_ENQ),
    .DEQ(a_ff_DEQ),
    .CLR(a_ff_CLR),
    .D_OUT(a_ff_D_OUT),
    .FULL_N(a_ff_FULL_N),
    .EMPTY_N(a_ff_EMPTY_N)
  );

  FIFO1 #(.width(1), .guarded(1'b1)) b_ff (
    .CLK(CLK),
    .RST(RST_N),
    .D_IN(b_ff_D_IN),
    .ENQ(b_ff_ENQ),
    .DEQ(b_ff_DEQ),
    .CLR(b_ff_CLR),
    .D_OUT(b_ff_D_OUT),
    .FULL_N(b_ff_FULL_N),
    .EMPTY_N(b_ff_EMPTY_N)
  );

  FIFO2 #(.width(1), .guarded(1'b1)) y_ff (
    .CLK(CLK),
    .RST(RST_N),
    .D_IN(y_ff_D_IN),
    .ENQ(y_ff_ENQ),
    .DEQ(y_ff_DEQ),
    .CLR(y_ff_CLR),
    .D_OUT(y_ff_D_OUT),
    .FULL_N(y_ff_FULL_N),
    .EMPTY_N(y_ff_EMPTY_N)
  );

  // Read data logic
  always @(*) begin
    case (read_address)
      3'd0: read_data = a_ff_FULL_N;
      3'd1: read_data = b_ff_FULL_N;
      3'd2: read_data = y_ff_EMPTY_N;
      3'd3: read_data = y_ff_EMPTY_N && y_ff_D_OUT;
      default: read_data = 1'b0;
    endcase
  end

  // Counter update
  always @(posedge CLK or `BSV_RESET_EDGE RST_N) begin
    if (RST_N == `BSV_RESET_VALUE) begin
      counter <= `BSV_ASSIGNMENT_DELAY 8'd0;
    end else if (counter_EN) begin
      counter <= `BSV_ASSIGNMENT_DELAY counter_D_IN;
    end
  end

endmodule
