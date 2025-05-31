module FIFO2 #(parameter width = 1) (
  input  wire         CLK,
  input  wire         RST,
  input  wire [width-1:0] D_IN,
  input  wire         ENQ,
  input  wire         DEQ,
  input  wire         CLR,
  output reg  [width-1:0] D_OUT,
  output wire         FULL_N,  
  output wire         EMPTY_N  
);

  // Small 2-entry FIFO for simplicity
  reg [width-1:0] mem [1:0];
  reg [1:0] head, tail;
  reg [1:0] count;

  // FULL_N and EMPTY_N logic
  assign FULL_N = (count < 2);
  assign EMPTY_N = (count > 0);

  always @(posedge CLK or posedge RST) begin
    if (RST) begin
      head <= 0;
      tail <= 0;
      count <= 0;
      D_OUT <= 0;
    end else if (CLR) begin
      head <= 0;
      tail <= 0;
      count <= 0;
      D_OUT <= 0;
    end else begin

      if (ENQ && FULL_N) begin
        mem[head] <= D_IN;
        head <= head + 1;
        count <= count + 1;
      end
      if (DEQ && EMPTY_N) begin
        D_OUT <= mem[tail];
        tail <= tail + 1;
        count <= count - 1;
      end else if (EMPTY_N) begin
        // hold D_OUT stable if not dequeued
        D_OUT <= mem[tail];
      end
    end
  end

endmodule
