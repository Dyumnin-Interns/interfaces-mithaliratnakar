import FIFOF::*;

interface Ifc_dut;
    (* always_ready *)
    method Bool write_rdy();
    (* always_ready *)
    method Action write(Bit#(3) address, Bool data);
    (* always_ready *)
    method Bool read_rdy();
    (* always_ready *)
    method Bool read_data();
    method Action read(Bit#(3) address);
endinterface

(*synthesize*)
module mkDut(Ifc_dut);
    FIFOF#(Bool) a_ff <- mkFIFOF();
    FIFOF#(Bool) b_ff <- mkFIFOF1();
    FIFOF#(Bool) y_ff <- mkFIFOF();
    Reg#(Bool) a_data <- mkReg(False);
    Reg#(Bool) b_data <- mkReg(False);
    
    rule enq_a_ff;
        a_ff.enq(a_data);
    endrule
    
    rule enq_b_ff;
        b_ff.enq(b_data);
    endrule
    
    rule or_gate;
        let x = a_ff.first();
        let z = b_ff.first();
        y_ff.enq(x || z);
        a_ff.deq();
        b_ff.deq();
    endrule
    
    PulseWire read_pw <- mkPulseWire();
    
    rule handle_read (read_pw);
        y_ff.deq();
    endrule
    
    method Bool write_rdy() = True;
    
    method Action write(Bit#(3) address, Bool data);
        case (address)
            3'b100: a_data <= data;  // address 4
            3'b101: b_data <= data;  // address 5
        endcase
    endmethod
    
    method Bool read_rdy() = True;
    
    method Bool read_data();
        return y_ff.first();
    endmethod
    
    method Action read(Bit#(3) address);
        if (address == 3'b011) begin  // address 3
            read_pw.send();
        end
    endmethod
endmodule
