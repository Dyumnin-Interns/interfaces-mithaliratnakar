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

module dut(
  input  CLK,
  input  RST_N,
  input  [2:0] write_address,
  input  [7:0] write_data,
  input  write_en,
  output write_rdy,
  input  [2:0] read_address,
  input  read_en,
  output reg [7:0] read_data,
  output read_rdy,
  output [7:0] counter_out,
  output wire a_ff_EMPTY_N
);

  // Declare internal wires and regs
  reg [7:0] counter;
  wire [7:0] counter_D_IN;
  wire counter_EN;

  // Signals for FIFO 'a'
  wire a_ff_CLR;
  wire a_ff_DEQ;
  wire [7:0] a_ff_D_IN;
  wire [7:0] a_ff_D_OUT;
  wire a_ff_EMPTY_N;
  wire a_ff_ENQ;
  wire a_ff_FULL_N;

  // Signals for FIFO 'b'
  wire b_ff_CLR;
  wire b_ff_DEQ;
  wire [7:0] b_ff_D_IN;
  wire [7:0] b_ff_D_OUT;
  wire b_ff_EMPTY_N;
  wire b_ff_ENQ;
  wire b_ff_FULL_N;

  // Signals for FIFO 'y'
  wire y_ff_CLR;
  wire y_ff_DEQ;
  wire [7:0] y_ff_D_IN;
  wire [7:0] y_ff_D_OUT;
  wire y_ff_EMPTY_N;
  wire y_ff_ENQ;
  wire y_ff_FULL_N;

  // Assign output counter value
  assign counter_out = counter;

  // Write ready always high (ready to accept data)
  assign write_rdy = 1'b1;

  // Helper signals for write/read address matching
  wire a_data_whas = write_en && (write_address == 3'd4);
  wire b_data_whas = write_en && (write_address == 3'd5);
  wire pwyff_deq_whas = read_en && (read_address == 3'd3);

  // Counter increment logic
  assign counter_D_IN = counter + 8'd1;
  assign counter_EN = 1'b1; // always enabled

  // FIFO inputs for enqueue
  assign a_ff_D_IN = write_data;
  assign b_ff_D_IN = write_data;

  // Enqueue conditions for a_ff and b_ff FIFOs
  assign a_ff_ENQ = a_ff_FULL_N && a_data_whas;
  assign b_ff_ENQ = b_ff_FULL_N && b_data_whas;

  // Dequeue conditions for a_ff and b_ff FIFOs:
  // Dequeue only when y_ff not full, both a_ff and b_ff are NOT empty,
  // and counter reached 50
  assign a_ff_DEQ = y_ff_FULL_N && a_ff_EMPTY_N && b_ff_EMPTY_N && (counter == 8'd50);
  assign b_ff_DEQ = y_ff_FULL_N && a_ff_EMPTY_N && b_ff_EMPTY_N && (counter == 8'd50);

  assign a_ff_CLR = 1'b0;
  assign b_ff_CLR = 1'b0;

  assign y_ff_D_IN = a_ff_D_OUT | b_ff_D_OUT;

  assign y_ff_ENQ = y_ff_FULL_N && a_ff_EMPTY_N && b_ff_EMPTY_N && (counter == 8'd50);


  assign y_ff_DEQ = y_ff_EMPTY_N && pwyff_deq_whas;

  assign y_ff_CLR = 1'b0;

  always @(*) begin
    case (read_address)
      3'd0: read_data = {7'd0, a_ff_FULL_N};
      3'd1: read_data = {7'd0, b_ff_FULL_N};
      3'd2: read_data = {7'd0, y_ff_EMPTY_N};
      3'd3: read_data = y_ff_EMPTY_N ? y_ff_D_OUT : 8'd0;
      default: read_data = 8'd0;
    endcase
  end

  assign read_rdy = 1'b1;

  FIFO2 #(.width(8)) a_ff(
    .RST(RST_N),
    .CLK(CLK),
    .D_IN(a_ff_D_IN),
    .ENQ(a_ff_ENQ),
    .DEQ(a_ff_DEQ),
    .CLR(a_ff_CLR),
    .D_OUT(a_ff_D_OUT),
    .FULL_N(a_ff_FULL_N),
    .EMPTY_N(a_ff_EMPTY_N)
  );

  FIFO1 #(.width(8)) b_ff(
    .RST(RST_N),
    .CLK(CLK),
    .D_IN(b_ff_D_IN),
    .ENQ(b_ff_ENQ),
    .DEQ(b_ff_DEQ),
    .CLR(b_ff_CLR),
    .D_OUT(b_ff_D_OUT),
    .FULL_N(b_ff_FULL_N),
    .EMPTY_N(b_ff_EMPTY_N)
  );

  FIFO2 #(.width(8)) y_ff(
    .RST(RST_N),
    .CLK(CLK),
    .D_IN(y_ff_D_IN),
    .ENQ(y_ff_ENQ),
    .DEQ(y_ff_DEQ),
    .CLR(y_ff_CLR),
    .D_OUT(y_ff_D_OUT),
    .FULL_N(y_ff_FULL_N),
    .EMPTY_N(y_ff_EMPTY_N)
  );

 
  always @(posedge CLK or `BSV_RESET_EDGE RST_N) begin
    if (RST_N == `BSV_RESET_VALUE) begin
      counter <= `BSV_ASSIGNMENT_DELAY 8'd0;
    end else if (counter_EN) begin
      counter <= `BSV_ASSIGNMENT_DELAY counter_D_IN;
    end
  end

  `ifndef BSV_NO_INITIAL_BLOCKS
  initial begin
    counter = 8'hAA;
  end
  `endif

endmodule
