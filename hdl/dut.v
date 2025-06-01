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
    input  wire [2:0]  write_address,
    input  wire [7:0]  write_data,    // **FIXED: Now 8 bits wide**
    input  wire        write_en,
    output wire        write_rdy,
    input  wire [2:0]  read_address,
    input  wire        read_en,
    output reg  [7:0]  read_data,     // **FIXED: Now 8 bits wide**
    output wire        read_rdy
);

  // Internal wires and regs for FIFO connections
  wire fifo_reset; 

  wire a_ff_enq, a_ff_deq, a_ff_clr, a_ff_full_n, a_ff_empty_n;
  wire [7:0] a_ff_din;   // **FIXED: Now 8 bits wide**
  wire [7:0] a_ff_dout;  // **FIXED: Now 8 bits wide**

  wire b_ff_enq, b_ff_deq, b_ff_clr, b_ff_full_n, b_ff_empty_n;
  wire [7:0] b_ff_din;   // **FIXED: Now 8 bits wide**
  wire [7:0] b_ff_dout;  // **FIXED: Now 8 bits wide**

  wire y_ff_enq, y_ff_deq, y_ff_clr, y_ff_full_n, y_ff_empty_n;
  wire [7:0] y_ff_din;   // **FIXED: Now 8 bits wide**
  wire [7:0] y_ff_dout;  // **FIXED: Now 8 bits wide**

  // Register counter
  reg [7 : 0] counter;
  wire [7 : 0] counter$D_IN;
  wire counter$EN;

  // Inlined wires for write/read enables based on address
  wire a_data$whas, b_data$whas, pwyff_deq$whas;


  // Submodule instantiations (FIFOs)
  FIFO2 #(
    .width(8) // **FIXED: FIFO width is 8 bits**
  ) a_ff (
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
    .width(8) // **FIXED: FIFO width is 8 bits**
  ) b_ff (
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
    .width(8) // **FIXED: FIFO width is 8 bits**
  ) y_ff (
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

  // Reset logic for FIFOs (active-low reset for RST_N)
  assign fifo_reset = ~RST_N;

  // action method write
  assign write_rdy = 1'd1 ; // Example: always ready to write

  // actionvalue method read
  always@(read_address or
          y_ff_empty_n or y_ff_dout or a_ff_full_n or b_ff_full_n or a_ff_dout or b_ff_dout) // Added a_ff_dout, b_ff_dout to sensitivity list
  begin
    case (read_address)
      3'd0: read_data = a_ff_dout; // **FIXED: Now reads the actual data from FIFO 'a'**
      3'd1: read_data = b_ff_dout; // **FIXED: Now reads the actual data from FIFO 'b'**
      3'd2: read_data = {7'b0, y_ff_empty_n};
      3'd3: read_data = y_ff_dout;
      default: read_data = 8'd0;
    endcase
  end
  assign read_rdy = 1'd1 ; // Example: read is always ready

  // Inlined wires for write/read enables based on address
  assign a_data$whas = write_en && write_address == 3'd0 ; // **FIXED: Enqueue to a_ff when write_address is 0**
  assign b_data$whas = write_en && write_address == 3'd5 ; // (Remains as is, not part of current test focus)
  assign pwyff_deq$whas = read_en && read_address == 3'd3 ;

  // register counter logic
  assign counter$D_IN = counter + 8'd1 ;
  assign counter$EN = 1'd1 ;

  // submodule a_ff logic connections
  assign a_ff_din = write_data ; 
  assign a_ff_enq = a_ff_full_n && a_data$whas ;
  assign a_ff_deq = read_en && read_address == 3'd0 && a_ff_empty_n; // **FIXED: Dequeue a_ff when reading from address 0**
  assign a_ff_clr = 1'b0 ;

  // submodule b_ff logic connections
  assign b_ff_din = write_data ; 
  assign b_ff_enq = b_ff_full_n && b_data$whas ;
  // Original b_ff_deq logic (remains as is for other processing)
  assign b_ff_deq = y_ff_full_n && a_ff_empty_n && b_ff_empty_n && counter == 8'd50 ;
  assign b_ff_clr = 1'b0 ;

  // submodule y_ff logic connections
  // IMPORTANT: This '|' performs a BITWISE OR on 8-bit values from a_ff_dout and b_ff_dout.
  // Ensure this is the desired combination logic.
  assign y_ff_din = a_ff_dout | b_ff_dout ; 
  // Original y_ff_enq logic (remains as is for other processing)
  assign y_ff_enq = y_ff_full_n && a_ff_empty_n && b_ff_empty_n && counter == 8'd50 ;
  assign y_ff_deq = y_ff_empty_n && pwyff_deq$whas ;
  assign y_ff_clr = 1'b0 ;

  // handling of inlined registers (for the counter)
  always@(posedge CLK or `BSV_RESET_EDGE RST_N)
  if (RST_N == `BSV_RESET_VALUE)
    begin
      counter <= `BSV_ASSIGNMENT_DELAY 8'd0;
    end
  else
    begin
      if (counter$EN) counter <= `BSV_ASSIGNMENT_DELAY counter$D_IN;
    end

  // synopsys translate_off
  `ifdef BSV_NO_INITIAL_BLOCKS
  `else // not BSV_NO_INITIAL_BLOCKS
  initial
  begin
    counter = 8'hAA; // Initial value for simulation (may be overridden by reset)
  end
  `endif

endmodule 
