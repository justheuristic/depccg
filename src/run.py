
import argparse
import fileinput
from depccg import PyAStarParser, PyJaAStarParser

parser = argparse.ArgumentParser("A* CCG parser")
parser.add_argument("model", help="model directory")
parser.add_argument("--input", default="-",
        help="a file with tokenized sentences in each line")
parser.add_argument("--format", default="auto",
        choices=["auto", "deriv", "xml", "ja", "conll"],
        help="output format")
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()
doc = [l.strip() for l in fileinput.input(args.input)]

parser = PyAStarParser(args.model, loglevel=1 if args.verbose else 3)

res = parser.parse_doc(doc)
for i, r in enumerate(res):
    print "ID={}".format(i)
    print getattr(r, args.format)
