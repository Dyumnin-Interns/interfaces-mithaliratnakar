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

  // FIFO submodule signals (renamed)
  wire a_ff_clr, a_ff_enq, a_ff_deq;
  wire a_ff_din, a_ff_dout;
  wire a_ff_full_n, a_ff_empty_n;

  wire b_ff_clr, b_ff_enq, b_ff_deq;
  wire b_ff_din, b_ff_dout;
  wire b_ff_full_n, b_ff_empty_n;

  wire y_ff_clr, y_ff_enq, y_ff_deq;
  wire y_ff_din, y_ff_dout;
  wire y_ff_full_n, y_ff_empty_n;

  // Assign constants
  assign write_rdy = 1'b1;  // always ready to accept writes
  assign read_rdy = 1'b1;   // always ready to read

  // Write address decoding
  wire write_to_a = write_en && (write_address == 3'd4);
  wire write_to_b = write_en && (write_address == 3'd5);

  // Read address decoding for dequeue pulse
  wire read_y_fifo = read_en && (read_address == 3'd3);

  // Enqueue data inputs
  assign a_ff_din = write_data;
  assign b_ff_din = write_data;

  // y_ff data input is OR of outputs of a_ff and b_ff FIFOs
  assign y_ff_din = a_ff_dout | b_ff_dout;

  // Reset is active low, so invert for FIFO reset input if needed
  // Assuming FIFO expects active high reset:
  wire fifo_reset = ~RST_N;

  assign a_ff_clr = 1'b0;
  assign b_ff_clr = 1'b0;
  assign y_ff_clr = 1'b0;

  // Synchronous control for ENQ and DEQ signals (pulse generation)
  reg a_ff_enq_reg, b_ff_enq_reg, y_ff_enq_reg;
  reg a_ff_deq_reg, b_ff_deq_reg, y_ff_deq_reg;

  always @(posedge CLK or negedge RST_N) begin
    if (!RST_N) begin
      a_ff_enq_reg <= 1'b0;
      b_ff_enq_reg <= 1'b0;
      y_ff_enq_reg <= 1'b0;
      a_ff_deq_reg <= 1'b0;
      b_ff_deq_reg <= 1'b0;
      y_ff_deq_reg <= 1'b0;
    end else begin
      // Enqueue logic: pulse on write enable & fifo not full
      a_ff_enq_reg <= write_to_a && a_ff_full_n;
      b_ff_enq_reg <= write_to_b && b_ff_full_n;

      // Enqueue y_ff when a_ff and b_ff are NOT empty and y_ff not full
      y_ff_enq_reg <= (a_ff_empty_n && b_ff_empty_n && y_ff_full_n);

      // Dequeue a_ff and b_ff when y_ff is not full and both are not empty
      a_ff_deq_reg <= (y_ff_full_n && a_ff_empty_n && b_ff_empty_n);
      b_ff_deq_reg <= (y_ff_full_n && a_ff_empty_n && b_ff_empty_n);

      // Dequeue y_ff on read request at address 3
      y_ff_deq_reg <= read_y_fifo && y_ff_empty_n;
    end
  end

  assign a_ff_enq = a_ff_enq_reg;
  assign b_ff_enq = b_ff_enq_reg;
  assign y_ff_enq = y_ff_enq_reg;

  assign a_ff_deq = a_ff_deq_reg;
  assign b_ff_deq = b_ff_deq_reg;
  assign y_ff_deq = y_ff_deq_reg;

  // Read data logic
  always @(*) begin
    case (read_address)
      3'd0: read_data = a_ff_full_n;
      3'd1: read_data = b_ff_full_n;
      3'd2: read_data = y_ff_empty_n;
      3'd3: read_data = y_ff_empty_n && y_ff_dout;
      default: read_data = 1'b0;
    endcase
  end

  // Instantiate FIFOs with corrected parameters
  FIFO2 #(.width(1)) a_ff(  // Removed guarded parameter
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

  FIFO1 #(.width(1)) b_ff(  // Removed guarded parameter
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

  FIFO2 #(.width(1)) y_ff(  // Removed guarded parameter
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
