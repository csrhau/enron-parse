#!/usr/bin/env python3

""" A simple parser for the Enron e-mail corpus """

from collections import namedtuple, Counter
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
    parser.add_argument("-p", "--path", help='Path to Enron corpus',
                        required=True)
    return parser.parse_args()


def name_extractor(path):
    """ Extracts names from Enron E-mail files """
    parser = email.parser.Parser()
    for root, _, files in os.walk(path):
        for message_file in files:
            path = os.path.join(root, message_file)
            with codecs.open(path, 'r', 'Latin-1') as message_file:
                content = message_file.read()
                message = parser.parsestr(content)
                yield (message['From'], message['X-From'])


class UnionFind:
    """Union-find data structure.

    Each unionFind instance X maintains a family of disjoint sets of
    hashable objects, supporting the following two methods:

    - X[item] returns a name for the set containing the given item.
      Each set is named by an arbitrarily-chosen one of its members; as
      long as the set remains unchanged it will keep the same name. If
      the item is not yet part of a set in X, a new singleton set is
      created for it.

    - X.union(item1, item2, ...) merges the sets containing each item
      into a single larger set.  If any item is not yet part of a set
      in X, it is added to X as one of the members of the merged set.
    """

    def __init__(self):
        """Create a new empty union-find structure."""
        self.weights = {}
        self.parents = {}

    def __getitem__(self, object):
        """Find and return the name of the set containing the object."""

        # check for previously unknown object
        if object not in self.parents:
            self.parents[object] = object
            self.weights[object] = 1
            return object

        # find path of objects leading to the root
        path = [object]
        root = self.parents[object]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root
        
    def __iter__(self):
        """Iterate through all items ever found or unioned by this structure."""
        return iter(self.parents)

    def union(self, *objects):
        """Find the sets containing the objects and merge them all."""
        roots = [self[x] for x in objects]
        heaviest = max([(self.weights[r],r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest

def main():
    """ Applicaion entry point """
    args = process_arguments()
    pairings = set(name_extractor(args.path))
    uf = UnionFind()
    skip_regexes = [re.compile('no.address@enron.com')]
    for p in pairings:
        if p[0] is None or p[1] is None:
            print("Error in tuple: {}".format(p))
            continue
        if any(r.match(p[0]) for r in skip_regexes):
                continue
        if any(r.match(p[1]) for r in skip_regexes):
                continue 
        uf.union(p[0], p[1])
    unique_names = set(p[0] for p in pairings)
    for name in unique_names:
        print("{};{}".format(uf[name],name))
    
if __name__ == '__main__':
    main()
