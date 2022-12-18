"""Implements the buckfs CLI."""
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--name', type=str, required=True)
add_subparser = parser.add_subparsers(dest='add')
add_subparser.add_

args = parser.parse_args()
