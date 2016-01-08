#!/usr/bin/env python3

""" A simple parser for the Enron e-mail corpus """

from collections import namedtuple
import argparse
import codecs
import json
import os
import re
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
    parser.add_argument("-s", "--sent", help='Only parse sent message folders',
                        action="store_true")
    parser.add_argument("-u", "--unique", help="Remove Duplicate messages",
                        action="store_true")
    parser.add_argument("-i", "--internal", help="Remove external messages",
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

def is_internal(message):
    """ Checks to see if a message is internal to Enron """
    enron_re = re.compile('@enron.com')
    if not enron_re.search(message.sender):
        return False
    if len(message.recipients) == 0:
        return False
    return all(r for r in message.recipients if enron_re.search(r))

def load_messages(path, sent, unique, internal, verbose):
    """ Loads messages from the corpus and returns them as Message objects """
    if unique:
        uniques = set()
        ingest_method = uniques.add
    else:
        messages = list()
        ingest_method = messages.append
    outbox_re = [re.compile(r) for r in ['sent_items$', 'sent$', 'sent_mail$']]
    for root, _, files in os.walk(path):
        if sent and not any(re.search(root) for re in outbox_re):
            continue
        if verbose:
            print("Processing {}".format(root))
        for message_file in files:
            message = read_message(os.path.join(root, message_file))
            if internal and not is_internal(message):
                continue
            ingest_method(message)
    if unique:
        return list(uniques)
    else:
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
    messages = load_messages(args.path, args.sent, args.unique, args.internal, args.verbose)
    messages.sort(key=operator.attrgetter('timestamp'))
    output_messages(args.output, messages)

if __name__ == '__main__':
    main()
