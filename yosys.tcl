yosys read_verilog $::env(FILE_NAME).v
yosys hierarchy -check
yosys proc
yosys flatten
yosys opt_expr
yosys opt_clean
yosys check
yosys opt -nodffe -nosdff
yosys fsm
yosys opt
yosys wreduce
yosys peepopt
yosys opt_clean
yosys opt
yosys memory -nomap
yosys opt_clean
yosys opt -fast -full
yosys memory_map
yosys opt -full
yosys techmap
yosys opt -fast
yosys abc -fast -g OR
yosys opt -fast
yosys hierarchy -check
yosys stat
yosys check
if {$::env(DO_SHOW) == "True"} {
    puts "hoi"
    yosys show -format svg -width
}
yosys write_json $::env(JSON_FILE_NAME)