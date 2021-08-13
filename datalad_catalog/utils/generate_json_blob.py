"""Utility module
"""

import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import os


# logger = logging.getLogger("extract_core_metadata")

argument_parser = ArgumentParser(
    description="some stuff")

argument_parser.add_argument(
    "-o", "--output",
    type=str,
    help="Output file to which result is written")

argument_parser.add_argument(
    "file_path",
    type=str,
    help="The file from which json object lines should be read")

arguments: Namespace = argument_parser.parse_args(sys.argv[1:])

print(arguments, file=sys.stderr)

with open(arguments.file_path) as f:
    lines = f.read().splitlines()

# if arguments.output is True:
#     out_file = arguments.output
# else:
#     out_file = arguments.file_path
out_file = arguments.output

with open(out_file, "w") as f:
    for line in lines:
        f.write(line + ",\n")
