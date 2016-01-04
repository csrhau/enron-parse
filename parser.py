#!/usr/bin/env python3

import argparse

def process_arguments():
    parser = argparse.ArgumentParser(description="Enron Corpus Parser")
    parser.add_argument("-p", "--path", help='Path to Enron corpus',
                        required=True)
    return parser.parse_args()

def main():
    args = process_arguments()

print('Hello, World!')
