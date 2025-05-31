`ifdef BSV_POSITIVE_RESET
  `define BSV_RESET_VALUE 1'b1
  `define BSV_RESET_EDGE posedge
`else
  `define BSV_RESET_VALUE 1'b0
  `define BSV_RESET_EDGE negedge
`endif

module FIFO2 #(parameter width = 1) (
    input                 CLK,
    input                 RST,
    input  [width-1:0]    D_IN,
    input                 ENQ,
    input                 DEQ,
    input                 CLR,

    output                FULL_N,
    output                EMPTY_N,
    output [width-1:0]    D_OUT
);

  // Internal registers
  reg [1:0] count;               // number of elements in FIFO: 0,1,2
  reg [width-1:0] data0_reg;
  reg [width-1:0] data1_reg;

  // Outputs
  assign FULL_N  = (count != 2); // FULL_N = 1 means NOT full
  assign EMPTY_N = (count != 0); // EMPTY_N = 1 means NOT empty
  assign D_OUT   = data0_reg;

  // Sequential logic for count and data registers
  always @(posedge CLK `BSV_RESET_EDGE) begin
    if (RST == `BSV_RESET_VALUE || CLR) begin
      count    <= 0;
      data0_reg <= {width{1'b0}};
      data1_reg <= {width{1'b0}};
    end else begin
      // Enqueue and Dequeue combinations
      case ({ENQ, DEQ})
        2'b10: begin // Enqueue only
          if (count < 2) begin
            if (count == 0) begin
              data0_reg <= D_IN;
            end else if (count == 1) begin
              data1_reg <= D_IN;
            end
            count <= count + 1;
          end
        end

        2'b01: begin // Dequeue only
          if (count > 0) begin
            data0_reg <= data1_reg; // shift data1 to data0
            data1_reg <= {width{1'b0}};
            count <= count - 1;
          end
        end

        2'b11: begin // Enqueue and Dequeue simultaneously
          if (count == 0) begin
            // FIFO empty, enqueue data0
            data0_reg <= D_IN;
            count <= 1;
          end else if (count == 1) begin
            // shift data1 to data0, enqueue new data into data1
            data0_reg <= data1_reg;
            data1_reg <= D_IN;
            // count remains 1
          end else if (count == 2) begin
            // FIFO full, dequeue oldest (data0), shift data1 to data0, enqueue new data to data1
            data0_reg <= data1_reg;
            data1_reg <= D_IN;
            // count remains 2
          end
        end

        default: begin
          // No enqueue or dequeue, hold state
        end
      endcase
    end
  end

  // Error checking (simulation only)
  // synopsys translate_off
  always @(posedge CLK) begin
    if (RST != `BSV_RESET_VALUE) begin
      if (ENQ && (count == 2)) begin
        $display("Warning: FIFO2: %m -- Enqueuing to full FIFO");
      end
      if (DEQ && (count == 0)) begin
        $display("Warning: FIFO2: %m -- Dequeuing from empty FIFO");
      end
    end
  end
  // synopsys translate_on

endmodule
