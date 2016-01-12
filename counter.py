#!/usr/bin/env python3

""" A simple parser for the Enron e-mail corpus """

from collections import namedtuple, Counter, defaultdict
import argparse
import codecs
import json
import os
import re
import operator
import email.parser
import dateutil.parser


def process_arguments():
    """ Process command line arguments """
    parser = argparse.ArgumentParser(description="Enron Corpus Parser")
    parser.add_argument("-a", "--aliases", help='Path to Alias file',
                        type=argparse.FileType('r'), required=True)
    parser.add_argument("-p", "--path", help='Path to Enron corpus',
                        required=True)
    return parser.parse_args()

def name_extractor(path):
    """ Extracts names from Enron E-mail files """
    parser = email.parser.Parser()
    for root, _, files in os.walk(path):
        print(root)
        for message_file in files:
            path = os.path.join(root, message_file)
            with codecs.open(path, 'r', 'Latin-1') as message_file:
                content = message_file.read()
                message = parser.parsestr(content)
                yield (message['From'], message['X-From'])

def main():
    """ Applicaion entry point """
    args = process_arguments()
    address_book = {email: name for name, emails in json.load(args.aliases).items() 
                                for email in emails}
    args.aliases.close()
    sendcount = Counter()
    aliases = defaultdict(set)
    for sender, alias in name_extractor(args.path):
        sendcount[sender] += 1
        if alias is not None:
            aliases[sender].add(alias)
    for sender, count in sendcount.most_common():
        if sender in address_book:
            continue
        if sender in aliases:
            print("{}: {}. Aliases: {}".format(sender, count, ','.join(aliases[sender])))
        else:
            print("{}: {}.".format(sender, count))

if __name__ == '__main__':
    main()
