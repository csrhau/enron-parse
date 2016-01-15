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
    parser.add_argument("-w", "--whitelist", help='path to e-mail whitelist',
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

def extract_messages(path, whitelist, outboxes, verbose):
    """ Extracts e-mails from the Enron corpus """
    # Set ensures messages are unique
    messages = set()
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
                message = parser.parsestr(message_file.read())
                # Resolve senders and recipients
                sender = message['From']
                if sender not in whitelist:
                    continue
                recipients = []
                if message['To'] is not None:
                    recipients += [m.strip(',') for m in message['To'].split()]
                if message['Cc'] is not None:
                    recipients += [m.strip(',') for m in message['Cc'].split()]
                if message['Bcc'] is not None:
                    recipients += [m.strip(',') for m in message['Bcc'].split()]
                # Only include recipients in whitelist
                wl_recipients = tuple(r for r in recipients if r in whitelist)
                if len(wl_recipients) == 0:
                    continue
                messages.add(Message(sender, wl_recipients, dateutil.parser.parse(message['Date'])))
    return sorted(messages, key=lambda x: x.timestamp)

def save_messages(messages, outfile):
    """ Serializes messages to JSON """
    data = [message._asdict() for message in messages]
    for message in data:
        message['timestamp'] = message['timestamp'].isoformat()
    json.dump(data, outfile, indent=2)

def main():
    """ Applicaion entry point """
    args = process_arguments()
    whitelist = set(json.load(args.whitelist))
    args.whitelist.close()

    messages = extract_messages(args.path, whitelist, args.sent, args.verbose)
    save_messages(messages, args.output)

if __name__ == '__main__':
    main()
