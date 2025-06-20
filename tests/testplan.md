Design Under Test:-The DUT includes 3 FIFOs `a_ff`, `b_ff`, `y_ff`. It accepts input data through write operations to `a_ff`, `b_ff`,
                   ORs the first elements of both, and writes the result into `y_ff`.

Testbench Components :- 

 Component     Description 
 ------------|-------------
 Driver      | Stimulates the DUT with write/read commands and input data. 
 Monitor     | Observes DUT outputs and sends them to the Scoreboard. 
 Checker     | Compares expected and actual output from `y_ff`. 
 Scoreboard  | Checks whether the DUT behaves correctly by comparing expected from the monitor results with actual results from the DUT. 
 Environment | Instantiates and connects all components. 
 Testcases   | Specific scenarios to validate correctness of DUT. 

 Testcases :-

 Test Description                  Inputs               
---------------------------|----------------------
  Simple OR Test           | `a = 0, b = 1, y = 1` 
  Both Inputs 0            | `a = 0, b = 0, y = 0` 
  Both Inputs 1            | `a = 1, b = 1, y = 1` 
  FIFO full                |                      
  FIFO empty               |                      
  Multiple write and read  |                      

cornercases :

1] basic write and read
2] read when Fifo is empty
3] overwrite before read
4] Write Same Value Repeatedly
5] Rapid Toggle of WR_EN and RD_EN

Functional Coverage :

1] write when empty
2] write when full
3] read when full
4] read when empty
5] simultaneous read write
6] full flag asserted
7] empty flag asserted

Cross Coverage :

 Cross Bin                        Description                                      
--------------------|--------------------------------------------------
 a_input × b_input  | Check all 2×2 input combinations: 00, 01, 10, 11 
 write_addr × data  | Check data combinations at write addr 4 and 5 

 Directory Structure :

bsv - mem_if.bsv
hdl - FIFO1.v
      FIFO2.v
      delayed_dut.v
      dut.v
      dut_wrapper.v
tests -  dut_test.py
         env.py
         driver.py
         monitor.py
         scoreboard.py
         coverage.py
         Makefile

