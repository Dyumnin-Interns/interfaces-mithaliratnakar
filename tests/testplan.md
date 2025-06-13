Design Under Test (DUT): FIFO system with three FIFOs (a_ff, b_ff, y_ff).

Interfaces to drive:
Inputs: write_address, write_data, write_en, read_address, read_en
Clock & Reset: CLK, RST_N

Monitors:
Monitor FIFO statuses (FULL_N, EMPTY_N)
Observe read_data for correctness.

Drivers:
Drive different write_address values to target a_ff (4), b_ff (5), and read signals.

Corner cases / Testcases:
Enqueue to a full FIFO (check for error message).
Dequeue from an empty FIFO (check for error).
Normal enqueue-dequeue operation.
Simultaneous enqueue and dequeue.

Functional coverage goals:
Cover all combinations of write/read addresses.
Cover all FIFO states: full, empty, half-full.

Cross coverage:
Cross between write_address and read_address.

