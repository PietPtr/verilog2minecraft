`timescale 100fs/100fs
module fourgates (input a, input b, input c, output out);
  assign out = (~c | ~a) | (~a | ~b);
endmodule