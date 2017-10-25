#!/usr/bin/env python3
"""Create a CSV index from a list of urls"""

import csv
import re
import sys
import argparse
from urllib.parse import unquote

def iter_url_index(urls, index_pattern):
    """[url1, url2, ...], index_pattern --> yield (index, url) for each url"""

    for url in urls:
        match = index_pattern.match(url)
        if not match:
            print('WARNING: {} doesn\'t match index_pattern'.format(url), file=sys.stderr)
        else:
            yield (unquote(match.group(1)), url)

def main():
    """Read input and write CSV index"""

    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--index-pattern', '-ip', nargs='?')
    args = parser.parse_args()

    input_file = open(args.input, encoding='utf-8')
    output_file = open(args.output, 'w', encoding='utf-8')
    pattern = re.compile(args.index_pattern)

    writer = csv.writer(output_file)
    urls = input_file.read().splitlines()
    input_file.close()

    for index, url in sorted(iter_url_index(urls, pattern), key=lambda row: row[0]):
        writer.writerow([index, url])

    output_file.close()

if __name__ == '__main__':
    main()
