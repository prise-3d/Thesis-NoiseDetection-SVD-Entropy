# main imports
import os, sys
import argparse


def main():

    parser = argparse.ArgumentParser(description="Read and compute entropy data file (using `minus` approach)")

    parser.add_argument('--data', type=str, help='entropy file data to read and compute')

    args = parser.parse_args()

    p_data   = args.data

    with open(p_data, 'r') as f:
        lines = f.readlines()

        print(lines[0].split(';')[6])

if __name__ == "__main__":
    main()