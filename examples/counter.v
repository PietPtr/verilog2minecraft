/* AUTOMATICALLY GENERATED VERILOG-2001 SOURCE CODE.
** GENERATED BY CLASH 1.4.6. DO NOT MODIFY.
*/
`timescale 100fs/100fs
module counter
    ( // Inputs
      input  clk // clock
    , input  rst // reset
    , input  en // enable
    , input  enable

      // Outputs
    , output wire [0:0] sum_lsb
    );
  // Example.hs:(20,1)-(21,48)
  reg [2:0] c$ds_app_arg = 3'd0;
  wire [2:0] c$app_arg;
  wire [3:0] result;
  wire [2:0] c$bv;

  // register begin
  always @(posedge clk or  posedge  rst) begin : c$ds_app_arg_register
    if ( rst) begin
      c$ds_app_arg <= 3'd0;
    end else if (en) begin
      c$ds_app_arg <= result[3:1];
    end
  end
  // register end

  assign sum_lsb = result[0:0];

  assign c$app_arg = enable ? (c$ds_app_arg + 3'd1) : c$ds_app_arg;

  assign c$bv = (c$ds_app_arg >> (64'sd2));

  assign result = {c$app_arg,   c$bv[0+:1]};


endmodule

