import os, sys, argparse
from shutil import copy
from dotenv import load_dotenv
load_dotenv()

def build_file(verilog_file, output_file, svg_file):
    os.environ["FILE_NAME"] = verilog_file.split(".")[0] # remove extension
    os.environ["JSON_FILE_NAME"] = output_file
    os.environ["DO_SHOW"] = str(svg_file != None)
    # os.getenv("HOME") + ""
    outpipe = os.popen("yosys -c yosys.tcl")

    line = outpipe.readline()
    while line:
        print(line, end='')
        line = outpipe.readline()


parser = argparse.ArgumentParser()
parser.add_argument("verilog", help="Verilog file to synthesize.")
parser.add_argument("output", help="Name of output JSON file.")
parser.add_argument("-s", "--svg", help="Render synthesized design to an SVG.",
                    action="store")
args = parser.parse_args()


build_file(args.verilog, args.output, args.svg)