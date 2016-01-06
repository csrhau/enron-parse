#!/usr/bin/env python3

""" A simple parser for the Enron e-mail corpus """

from collections import namedtuple
import argparse
import codecs
import json
import os
import operator
import email.parser
import dateutil.parser

Message = namedtuple('Message', ['sender', 'recipients', 'timestamp', 'subject', 'body'])

def process_arguments():
    """ Process command line arguments """
    parser = argparse.ArgumentParser(description="Enron Corpus Parser")
    parser.add_argument("-p", "--path", help='Path to Enron corpus',
                        required=True)
    parser.add_argument("-o", "--output", help='Path to output file',
                        required=True)
    parser.add_argument("-u", "--unique", help="Remove Duplicate messages",
                        action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    return parser.parse_args()

def read_message(path):
    """ Reads an enron message file into a Message tuple """
    parser = email.parser.Parser()
    with codecs.open(path, 'r', 'Latin-1') as message_file:
        content = message_file.read()
        message = parser.parsestr(content)
        recipients = ()
        if message['To'] is not None:
            recipients = tuple(m.strip(',') for m in message['To'].split())
        return Message(message['From'],
                       recipients,
                       dateutil.parser.parse(message['Date']),
                       message['Subject'],
                       message.get_payload())

def load_messages(path, unique, verbose):
    """ Loads messages from the corpus and returns them as Message objects """
    if unique:
        messages = set()
    else:
        messages = list()
    for root, _, files in os.walk(path):
        if verbose:
            print("Processing {}".format(root))
        for message_file in files:
            message = read_message(os.path.join(root, message_file))
            if unique:
                messages.add(message)
            else:
                messages.append(message)
    if unique:
        messages = list(messages)
    return messages

def output_messages(path, messages):
    """ Serializes messages to JSON """
    data = [message._asdict() for message in messages]
    for message in data:
        message['timestamp'] = message['timestamp'].isoformat()
    with open(path, 'w') as output:
        json.dump(data, output, indent=2)

def main():
    """ Applicaion entry point """
    args = process_arguments()
    messages = load_messages(args.path, args.unique, args.verbose)
    messages.sort(key=operator.attrgetter('timestamp'))
    output_messages(args.output, messages)

if __name__ == '__main__':
    main()
