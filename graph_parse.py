#!/usr/bin/env python3

""" A parser for the Enron e-mail corpus """

import argparse
import os
import re
import codecs
from collections import namedtuple
import json
import email.parser
import dateutil.parser

Message = namedtuple('Message', ['sender', 'recipients', 'timestamp'])

def process_arguments():
    """ Process command line arguments """
    parser = argparse.ArgumentParser(description="Enron Corpus Parser")
    parser.add_argument("-a", "--aliases", help='path to Alias file',
                        type=argparse.FileType('r'), required=True)
    parser.add_argument("-o", "--output", help='path to output file',
                        type=argparse.FileType('w'), required=True)
    parser.add_argument("-p", "--path", help='path to Enron corpus',
                        required=True)
    parser.add_argument("-s", "--sent", help="only parse sent message folders",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    return parser.parse_args()

def message_extractor(path, address_book, outboxes, verbose):
    """ Extracts e-mails from the Enron corpus """
    parser = email.parser.Parser()
    outbox_re = [re.compile(r) for r in ['sent_items$', 'sent$', 'sent_mail$']]
    for root, _, files in os.walk(path):
        # Only parse messages in 'sent' folder
        if outboxes and not any(re.search(root) for re in outbox_re):
            continue
        if verbose:
            print(root)
        for message_file in files:
            path = os.path.join(root, message_file)
            with codecs.open(path, 'r', 'Latin-1') as message_file:
                content = message_file.read()
                message = parser.parsestr(content)
                # Resolve senders and recipients
                sender = message['From']
                if sender not in address_book:
                    continue
                sender = address_book[sender]
                if message['To'] is None:
                    continue
                recipients = [m.strip(',') for m in message['To'].split()]
                recipients = tuple(address_book[r] for r in recipients if r in address_book)
                if len(recipients) == 0:
                    continue
                yield Message(sender, recipients, dateutil.parser.parse(message['Date']))

def save_messages(messages, outfile):
    """ Serializes messages to JSON """
    data = [message._asdict() for message in messages]
    for message in data:
        message['timestamp'] = message['timestamp'].isoformat()
    json.dump(data, outfile, indent=2)

def main():
    """ Applicaion entry point """
    args = process_arguments()
    address_book = {email: name for name, emails in json.load(args.aliases).items()\
                                for email in emails}
    args.aliases.close()
    # Set ensures messages are unique
    messages = set(message_extractor(args.path, address_book, args.sent, args.verbose))
    save_messages(messages, args.output)

if __name__ == '__main__':
    main()
