# verilog2minecraft

Compiles Verilog to Minecraft (With the help of Yosys)

## Examples

Run the tool with one of the JSON files in the jsons folder, or build the JSONs yourself with `build.py` and Yosys. The examples are of following sizes:

- `twogates.v`: 1 NOT, 1 OR, 2 in total (4 gwires).

- `combi.v`: 3 NOT, 3 OR, 2 in total (9 wires).

- `counter.v`: 10 NOT, 8 OR, 3 DFFs, 21 in total (36 wires).

- `modulo.v`: 271 NOT, 300 OR, 8 DFFs, 579 in total (590 wires).

- `pipe.v`: 4314 NOT, 4836 OR, 48 DFFs, 9198 in total (9217 wires).

- `md5.v`: 5196 NOT, 5906 OR, 396 DFFs, 11498 in total (21129 wires).


## TODO

[ ] Add simulated annealing placer

[x] Allow users to constrain outputs to physical I/O with a location

[ ] Rotations