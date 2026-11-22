import sys
sys.path.append(".")
sys.path.append("scripts")

from data_loading import wikitable
from argparse import Namespace

args = Namespace(dataset='open_wikitq', dataset_split="validation", dataset_sub=10)
print(args)
data = wikitable(args)

print("Loaded:", len(data))
print("First item keys:", list(data[0].keys()) if data else "EMPTY")
