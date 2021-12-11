`timescale 100fs/100fs
module twogates (input a, input b, input c, output out);
  assign out = a | ~b | (~a | ~c);
endmodule