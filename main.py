import numpy as np
import argparse
import termios
import time
import sys
import tty
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
    help_texteditor = (
        'A text editor with basic functionality.'
    )
    help_liveplot = (
        'To display matplotlib plots live, using the terminal for input.'
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
    parser.add_argument(
        '--texteditor', action='store_true', help = help_texteditor
    )
    parser.add_argument(
        '--liveplot', action='store_true', help = help_liveplot
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
    print(Color.list_colors())

def procedure_string():
    string = String('test', 'yellow', 'turquoise')
    print(string)

def procedure_livemenu():
    live_menu = LiveMenu()
    live_menu.start()
    live_menu.stop()

def procedure_texteditor():
    text_editor = TextEditor()
    text_editor.start()
    text_editor.stop()

def procedure_liveplot():
    live_plot = LivePlot()
    live_plot.start()
    live_plot.stop()

"""MAIN SCRIPT"""

args = parse_args()

if args.unit_tests is True:
    tests.run_all()

if args.test is True:

    import readline
    import subprocess
    import re
    from termutils.config.keys import mouse_btns
    from typing import Union, Dict

    print('\033[2J\033[f')

    _fd = sys.stdin.fileno()
    _old_settings = termios.tcgetattr(_fd)

    tty.setraw(sys.stdin.fileno())

    def _process_click(output) -> Dict[str, Union[str,int]]:
        '''
            Given a terminal output string from a mouse click operation, returns
            a dict containing information about the location and nature of the
            action.  If invalid, returns an empyty Dict.
        '''
        output = output.decode()
        if len(output) != 6:
            return dict()
        btn_key = ord(output[3])
        if btn_key not in mouse_btns:
            return dict()
        else:
            dict_out = {
                'action'    : mouse_btns[ord(output[3])],
                'y'         : ord(output[4])-33,
                'x'         : ord(output[5])-33,
            }
        return dict_out

    try:
        for i in range(10):
            print('\033[?1002h', flush = True)
            a = os.read(1,5)
            print('\033[?1002l', flush = True)
            time.sleep(0.05)
            print(_process_click(a), flush = True)
        time.sleep(0.1)

    except Exception as e:
        print(e)

    termios.tcsetattr(
        _fd, termios.TCSADRAIN,
        _old_settings
    )

    # print('\033[2J\033[f')

if args.color is True:
    procedure_color()

if args.string is True:
    procedure_string()

if args.livemenu is True:
    procedure_livemenu()

if args.texteditor is True:
    procedure_texteditor()

if args.liveplot is True:
    procedure_liveplot()
