import numpy as np
import argparse
import time
import sys
import os

from termutils import *

globals()['status_entries'] = []

def parse_args():

    argparse_desc = (
        'Manages ML-based fish identification tools, both locally and on GCP.'
    )
    help_color = (
        'A sample of class Color showcasing its usage.'
    )
    help_string = (
        'A sample of class String displaying its abilities.'
    )
    help_livemenu = (
        'A sample of class LiveMenu presenting a few of its uses.'
    )

    parser = argparse.ArgumentParser(description = argparse_desc)

    parser.add_argument(
        '--unit_tests', action='store_true', help = 'Runs all unit tests'
    )
    parser.add_argument(
        '--test', action='store_true', help = 'Runs the latest test script'
    )
    parser.add_argument(
        '--color', action='store_true', help = help_color
    )
    parser.add_argument(
        '--string', action='store_true', help = help_string
    )
    parser.add_argument(
        '--livemenu', action='store_true', help = help_livemenu
    )

    return parser.parse_args()

def update_status(new_entry):
    tab_len = len('Prev. Selections:') + 7
    tot_len = tab_len
    max_len = 80
    for entry in globals()['status_entries']:
        if entry == '<newline>':
            continue
        elif tot_len + len(entry) + 3 >= max_len:
            tot_len = tab_len + len(entry) + 3
        else:
            tot_len += len(entry) + 3
    if tot_len + len(new_entry) >= max_len:
        globals()['status_entries'].append('<newline>')
    globals()['status_entries'].append(new_entry)

def display_status():
    tab_len = len('Prev. Selections:') + 7
    status = text.bold('Prev. Selections:') + ' '*7
    for n,entry in enumerate(globals()['status_entries']):
        if entry == '<newline>':
            status += '\n' + ' '*tab_len
        elif n == len(globals()['status_entries'])-1:
            status += f'{text.italic(entry)}'
        else:
            status += f'{text.italic(entry)} > '
    return status + '\n'

"""SCRIPT PROCEDURES"""

def procedure_color():
    color = Color((255, 255, 255))

def procedure_string():
    for i in range(0, 256):
        print(f'\033[f{Color.chart(b = i)}')
        time.sleep(0.001)
    # string = String('test', 'fuchsia')
    # print(string)


def procedure_livemenu():
    LiveMenu.start()
    LiveMenu.stop()

"""MAIN SCRIPT"""

args = parse_args()

if args.unit_tests is True:
    tests.run_all()

if args.test is True:
    print('No Tests Implemented')

if args.color is True:
    procedure_color()

if args.string is True:
    procedure_string()

if args.livemenu is True:
    procedure_livemenu()
