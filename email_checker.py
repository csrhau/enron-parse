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


def email_extractor(path):
    """ Extracts email addresses from Enron E-mail files """
    parser = email.parser.Parser()
    outbox_re = [re.compile(r) for r in ['sent_items$', 'sent$', 'sent_mail$']]
    for root, _, files in os.walk(path):
        if not any(re.search(root) for re in outbox_re):
            continue
        print(root)
        for message_file in files:
            path = os.path.join(root, message_file)
            with codecs.open(path, 'r', 'Latin-1') as message_file:
                content = message_file.read()
                message = parser.parsestr(content)
                yield message['From']
                if message['To'] is not None:
                    for m in message['To'].replace(',', ' ').split():
                        if m is not None:
                            yield m

def main():
    """ Applicaion entry point """
    args = process_arguments()
    address_book = {email: name for name, emails in json.load(args.aliases).items() 
                                for email in emails}
    args.aliases.close()
    sendcount = Counter()

    for email in email_extractor(args.path):
        sendcount[email] += 1
    for email in address_book.keys():
        if sendcount[email] == 0:
            print("Error for key {}".format(email))
    print("Missing e-mails report")
    for email, count in sendcount.most_common():
        if email not in address_book.keys():
            print("{}: {}.".format(email, count))

        
    print("Done!")

if __name__ == '__main__':
    main()
