`timescale 100fs/100fs
module twogates (input a, input b, output out);
  assign out = a | ~b;
endmodule

