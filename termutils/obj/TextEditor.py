from typing import Tuple, Union
from string import punctuation
from copy import deepcopy
import textwrap
import readline
import shutil
import time

from termutils.config.defaults import term_rows, term_cols
from termutils.obj.LiveMenu import LiveMenu

class TextEditor(LiveMenu):

    def __init__(self, dt:float = 0.01, tab_len:int = 4) -> None:
        '''
            Creates an instance of TextEditor.  Supports usage of the default
            listener provided by class LiveMenu.
        '''
        self._delimiters = list(punctuation)
        self._delimiters.remove('_')

        cols, rows = shutil.get_terminal_size((term_cols, term_rows))[:]
        self._dt = dt
        self._tab_len = tab_len
        super().__init__(rows = rows, cols = cols)

    def __call__(self) -> None:
        '''
            Main loop which runs on one thread, while a listener runs on
            another and provides commands to be read by this method.

            These inputs are accessed via the superclass attributes
            `LiveMenu._input_state` and `LiveMenu._mouse_state`, and are
            processed in an infinite loop until broken.
        '''

        print('\033[5 q', end = '', flush = True)

        active = True
        key_idx = 0
        btn_idx = 0
        row = 0
        col = 0

        history = [[[' ']]]
        row_history = [row]
        col_history = [col]
        history_idx = 0

        text = [[' ']]

        while active:

            if not text:
                text.append([' '])

            btn_outputs = len(self._btn_history)
            key_outputs = len(self._key_history)

            if btn_idx < btn_outputs or key_idx < key_outputs:

                while btn_idx < btn_outputs:
                    btn = self._btn_history[btn_idx]
                    text, row, col = self._process_btn(btn, text, row, col)
                    btn_idx += 1

                    if not text:
                        text.append([' '])

                while key_idx < key_outputs:
                    key = self._key_history[key_idx]

                    if key == 'Kill':
                        active = False
                        key_idx += 1
                        break
                    elif key == 'Ctrl-z':
                        history_idx = max(0, history_idx - 1)
                        text = deepcopy(history[history_idx])
                        row = row_history[history_idx]
                        col = col_history[history_idx]
                        key_idx += 1
                    elif key == 'Ctrl-y':
                        history_idx = min(len(history) - 1, history_idx + 1)
                        text = deepcopy(history[history_idx])
                        row = row_history[history_idx]
                        col = col_history[history_idx]
                        key_idx += 1
                    else:
                        text, row, col = self._process_key(key, text, row, col)
                        history = history[:history_idx+1]
                        row_history = row_history[:history_idx+1]
                        col_history = col_history[:history_idx+1]
                        key_idx += 1

                        if not text:
                            text.append([])

                        for i,j in enumerate(text):
                            if j and j[-1] != ' ':
                                text[i].append(' ')

                text_str = '\033[2J\033[3J\033[f'
                text_str += '\n\r'.join(''.join(line) for line in text)
                text_str += f'\033[{row+1};{col+1}f'

                if not history or text != history[history_idx]:
                    row_history.append(row)
                    col_history.append(col)
                    history.append(text)
                    history_idx += 1

                print(text_str, end = '', flush = True)

            time.sleep(self._dt)

        print('\033[1 q', end = '', flush = True)

    def _left_group(self, text, row, col) -> int:
        '''
            Returns the number of elements to the left of the current element
            which consist of a group (such as a word, or a word and a space).
        '''
        spaces = True
        delim_mode = False
        N = 0
        if col < 1:
            if row > 0:
                N += 1
                row -= 1
                col = max(0, len(text[row]) - 1)
            else:
                return N
        else:
            col = max(0, col - 1)

        if not text[row]:
            return N

        while True:
            letter = text[row][col]
            if spaces:
                if letter in self._delimiters:
                    delim_mode = True
                    spaces = False
                elif letter != ' ':
                    spaces = False
                elif col == 0:
                    N += 1
                    break
            elif delim_mode:
                if letter not in self._delimiters:
                    break
            else:
                if letter in self._delimiters or letter == ' ':
                    break

            if col > 0:
                col -= 1
            elif row > 0:
                row -= 1
                N += 1
                col = max(0, len(text[row])-1)
            else:
                N += 1
                break

            N += 1

        return N

    def _right_group(self, text, row, col) -> int:
        '''
            Returns the number of elements to the left of the current element
            which consist of a group (such as a word, or a word and a space).
        '''
        spaces = True
        delim_mode = False
        N = 0
        if col >= len(text[row]) - 1:
            if row < len(text) - 1:
                N += 2
                row += 1
                col = 0
            else:
                return N

        if not text[row]:
            return N

        while True:
            letter = text[row][col]
            if spaces:
                if letter in self._delimiters:
                    delim_mode = True
                    spaces = False
                elif letter != ' ':
                    spaces = False
            elif delim_mode:
                if letter not in self._delimiters:
                    break
            else:
                if letter in self._delimiters or letter == ' ':
                    N += 1
                    break

            if col < len(text[row]) - 1:
                col += 1
            else:
                N += 1
                break
            N += 1

        return N

    def _delete(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Performs a delete on the given list of characters, using the
            context attached to them (see docstring in self._process_key).
        '''
        if col < len(text[row]):
            text[row].pop(col)
        elif row < len(text) - 1:
            new_row = text.pop(row+1)
            text[row] += new_row
        return text, row, col

    def _ctrl_delete(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Performs a ctrl-delete on the given list of characters, using the
            context attached to them (see docstring in self._process_key).
        '''
        N = self._right_group(text, row, col)
        for i in range(N):
            text, row, col = self._delete(text, row, col)
        return text, row, col

    def _backspace(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Performs a backspace on the given list of characters, using the
            context attached to them (see docstring in self._process_key).
        '''
        if col > 0:
            text[row].pop(col-1)
            col -= 1
        elif row > 0:
            new_row = text.pop(row)
            text[row-1] += new_row
            row -= 1
            col = len(text[row])-len(new_row)
        return text, row, col

    def _ctrl_backspace(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Performs a ctrl-backspace on the given list of characters, using the
            context attached to them (see docstring in self._process_key).
        '''
        N = self._left_group(text, row, col)
        for i in range(N):
            text, row, col = self._backspace(text, row, col)
        return text, row, col

    def _ctrl_left(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Moves the cursor to the left until the beginning of the previous
            word is reached.
        '''
        N = self._left_group(text, row, col)
        for i in range(N):
            if col < 1:
                if row > 0:
                    row -= 1
                    col = len(text[row]) - 1
                else:
                    break
            else:
                col -= 1
        return text, row, col

    def _ctrl_right(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Moves the cursor to the right until the end of the current word is
            reached.
        '''
        N = self._right_group(text, row, col)
        for i in range(N):
            if col >= len(text[row]) - 1:
                if row < len(text) - 1:
                    row += 1
                    col = 0
                else:
                    break
            else:
                col += 1
        return text, row, col

    def _ctrl_up(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Swaps the above line with the current one.
        '''
        if row > 0:
            current_row = text.pop(row)
            text.insert(row - 1, current_row)
            row -= 1
        return text, row, col

    def _ctrl_down(self, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Swaps the below line with the current one.
        '''
        if row < len(text) - 1:
            current_row = text.pop(row)
            text.insert(row + 1, current_row)
            row += 1
        return text, row, col

    def _process_key(self, key, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Takes the current text and modifies it using the given key input.
        '''

        if len(key) == 1:
            text[row].insert(col, key)
            col += 1

        elif key == 'Space':
            text[row].insert(col, ' ')
            col += 1

        elif key == 'Tab':
            for i in range(self._tab_len):
                text[row].insert(col, ' ')
            col += self._tab_len

        elif key == 'Delete':
            text, row, col = self._delete(text, row, col)

        elif key == 'Ctrl-Delete':
            text, row, col = self._ctrl_delete(text, row, col)

        elif key == 'Backspace':
            text, row, col = self._backspace(text, row, col)

        elif key == 'Ctrl-Backspace':
            text, row, col = self._ctrl_backspace(text, row, col)

        elif key == 'Enter':
            top = text[:row] + [text[row][:col]]
            mid = [text[row][col:]]
            bottom = text[row+1:]
            text = top + mid + bottom
            row += 1
            col = 0
            if row >= len(text):
                text.append([' '])

        elif key == 'Up':
            row = max(0, row - 1)
            col = min(col, len(text[row])-1)

        elif key == 'Down':
            row = min(len(text)-1, row + 1)
            col = min(col, len(text[row])-1)

        elif key == 'Left':
            if col > 0:
                col -= 1
            elif row > 0:
                row -= 1
                col = len(text[row]) - 1

        elif key == 'Right':
            if col < len(text[row]) - 1:
                col += 1
            elif row < len(text) - 1:
                row += 1
                col = 0

        elif key == 'Ctrl-Up':
            text, row, col = self._ctrl_up(text, row, col)

        elif key == 'Ctrl-Down':
            text, row, col = self._ctrl_down(text, row, col)

        elif key == 'Ctrl-Left':
            text, row, col = self._ctrl_left(text, row, col)

        elif key == 'Ctrl-Right':
            text, row, col = self._ctrl_right(text, row, col)

        return text, row, col

    def _process_btn(self, btn, text, row, col) -> Tuple[Union[str,int]]:
        '''
            Processes mouse inputs and returns a modified output list based on
            that.
        '''
        if btn['action'] in ['LeftClick', 'LeftDrag']:
            row = min(btn['x'], len(text)-1)
            col = min(btn['y'], len(text[row])-1)

        return text, row, col
