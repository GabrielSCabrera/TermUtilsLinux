from typing import Tuple, Callable, Any, Union, Dict
from string import punctuation, whitespace
import threading
import warnings
import readline
import termios
import time
import tty
import sys
import os

from termutils.config.keys import keys as keys_dict, mouse_btns
from termutils.config.defaults import (
    term_rows, term_cols, term_fd, term_settings
)

class LiveMenu:

    '''
        Allows the user to display live, changing text on the terminal while
        simultaneously accepting user inputs.
    '''

    _active = False
    _fd = term_fd                   # sys.stdin.fileno()
    _old_settings = term_settings   # termios.tcgetattr(_fd)
    _raw_mode = False
    _input_state = []               # History of all keys pressed
    _mouse_state = []               # History of all mouse actions

    '''CONSTRUCTOR'''

    def __init__(self, rows:int = None, cols:int = None) -> None:
        '''
            Creates a new, inactive instance of LiveMenu.  Arguments `rows`
            and `cols` should be integers greater than zero.
        '''
        if rows is None:
            rows = term_rows

        if cols is None:
            cols = term_cols

        self._dims = (rows, cols)
        self._current_active = False
        self._listener = self._default_listener
        self._writer = self._default_writer

    '''GETTERS'''

    @property
    def dims(self) -> Tuple[int]:
        '''
            Returns the terminal dimensions.
        '''
        return cls._dims

    @property
    def active(self) -> bool:
        '''
            Returns True if the current instance is active. False otherwise.
        '''
        return self._current_active

    '''SETTERS'''

    def set_dims(self, rows:int = None, cols:int = None) -> None:
        '''
            Sets the terminal dimensions.
        '''
        if rows is None:
            rows = cls._dims[0]
        if cols is None:
            cols = cls._dims[1]
        cls._dims = (rows, cols)

    def set_writer(self, writer:Callable) -> None:
        '''
            Sets the callable that will write to the terminal, using the input
            given by callable attribute `listener`
        '''
        self._writer = writer

    def set_listener(self, listener:Callable) -> None:
        '''
            The callable will create an input source for the `writer`
            attribute, seen in method `set_writer.`

            By default, calls private method `_default_listener`.

            Note: avoid changing the listener, the default will usually do the
            trick!
        '''
        self._listener = listener

    '''RUNTIME'''

    def start(self) -> None:
        '''
            Activates the LiveMenu session.
        '''
        if self.__class__._active:
            self.__class__._raw(False)
            msg = (
                '\n\nLiveMenu is already active, cannot run method `start` on '
                'multiple separate instances.  Call method `stop` on current '
                'active instance before attempting to activate this one.\n'
            )
            raise RuntimeError(msg)
        self._current_active = True
        self.__class__._active = True

        t_listener = threading.Thread(target = self._listener)
        t_writer = threading.Thread(target = self._writer)

        self._raw(True)

        try:
            t_listener.start()
            t_writer.start()

            while t_listener.is_alive():
                time.sleep(0.01)

            t_listener.join()
            t_writer.join()
        except Exception as e:
            self._raw(False)
            raise Exception(e)

        self._raw(False)

    def stop(self) -> None:
        '''
            Deactivates the LiveMenu session.
        '''
        if not self.__class__._active:
            switch = self.__class__._raw_mode
            if switch:
                self.__class__._raw(False)
            msg = (
                '\n\nAttempted to stop an inactive LiveMenu.\n'
            )
            warnings.warn(msg)
            if switch:
                self.__class__._raw(True)
        else:
            self.__class__._raw(False)
            self.__class__._active = False
            self._current_active = False

    def __enter__(self) -> None:
        '''
            Context manager wrapper for `start`.
        '''
        self.start()

    def __exit__(self, type, value, tb) -> None:
        '''
            Context manager wrapper for `stop`.
        '''
        self.stop()

    '''PRIVATE METHODS'''

    @classmethod
    def _raw(cls, state:bool) -> None:
        '''
            Sets the terminal to raw mode if True, or to echo mode if False
        '''
        if state:
            tty.setraw(sys.stdin.fileno())
            cls._raw_mode = True
        elif not state:
            termios.tcsetattr(
                cls._fd, termios.TCSADRAIN,
                cls._old_settings
            )
            cls._raw_mode = False

    @classmethod
    def _default_listener(cls, escape_hits:int = 3) -> str:
        '''
            An input source for the `writer` callable, as seen in method
            `set_writer.`  Updates the global variable `input_state` by
            appending the latest keypress to it.

            Expects `_raw_mode` to be True, implying the terminal will read user
            inputs immediately without echoing to the terminal.
        '''
        escape_hitcount = 0
        try:
            print('\033[?1002h', end = '', flush = True)
            while True:
                output = cls._get_input()
                if output == 'Esc':
                    if escape_hitcount < escape_hits - 1:
                        escape_hitcount += 1
                        continue
                    else:
                        cls._input_state.append('Kill')
                        break
                elif escape_hitcount > 0 and output != 'Esc':
                    escape_hitcount = 0
                if isinstance(output, str):
                    cls._input_state.append(output)
                elif isinstance(output, dict) and len(output) > 0:
                    cls._mouse_state.append(output)
        except Exception as e:
            print('\033[?1002l', end = '', flush = True)
            raise Exception(e)
        print('\033[?1002l', end = '', flush = True)

    @classmethod
    def _default_writer(cls, dt:float = 0.01, tab_len:int = 4):
        '''
            Default writer – acts as a simple text-editor.
        '''
        active = True
        idx_input = 0
        idx_mouse = 0
        idx_cursor = 0
        str_out = ''
        print(f'\033[2J\033[3J\033[f', end = '', flush = True)
        delims = list(punctuation + whitespace)
        mouse_state = {}
        while active:
            c1 = len(cls._input_state) > idx_input
            c2 = len(cls._mouse_state) > idx_mouse
            if c1 or c2:
                out = '\033[2J\033[3J\033[f'
                idx_mouse = len(cls._mouse_state)
                if cls._mouse_state:
                    mouse_state = cls._mouse_state[-1]
                    mouse_str = (
                        f"{mouse_state['action']} at row {mouse_state['y']} "
                        f"col {mouse_state['x']}"
                    )
                    out += f'\r{mouse_str}'
                while len(cls._input_state) > idx_input:

                    step = cls._input_state[idx_input]

                    if len(step) == 1:
                        str_out += step

                    elif step == 'Backspace' and len(str_out) > 0:
                        str_out = str_out.rstrip('\r')
                        str_out = str_out[:-1]

                    elif step == 'Ctrl-Backspace':
                        str_out = str_out.rstrip('\r _')
                        n = 0
                        while len(str_out) > 0:
                            c1 = len(str_out) == 0
                            c2 = str_out[-1] in delims and n > 0
                            if c1 or (c2):
                                break
                            str_out = str_out[:-1]
                            n += 1

                    elif step == 'Space':
                        str_out += ' '

                    elif step == 'Enter':
                        str_out += '\n\r'

                    elif step == 'Tab':
                        str_out += ' '*tab_len

                    elif step == 'Kill':
                        active = False
                        break

                    idx_input += 1

                if len(str_out) == 0:
                    row = 1
                    col = 0
                else:
                    split_lines = str_out.split('\n')
                    row = len(split_lines)+1
                    col = len(split_lines[-1])+1
                    if row == 1:
                        col += 1
                out += f'\n\r{str_out}\033[{row};{col}f'
                print(out, end = '', flush = True)

            time.sleep(dt)
        print(f'\033[2J\033[3J\033[f', end = '', flush = True)

    @classmethod
    def _get_input(cls) -> Union[str,Dict[str,Union[str,int]]]:
        '''
            Listens for keyboard or mouse input, and returns a string with a
            key name (such as `a`, `Z`, or `Backspace`) or a dictionary with
            information about how the mouse was clicked, and where.

            Expects `_raw_mode` to be True, implying the terminal will read user
            inputs immediately without echoing to the terminal.
        '''
        key = os.read(1,10).decode()
        if key in keys_dict.keys():
            output = keys_dict[str(key)]
        elif len(repr(key)) == 3:
            output = key
        else:
            output = cls._process_click(key)

        return output

    @classmethod
    def _process_click(cls, output) -> Dict[str, Union[str,int]]:
        '''
            Given a terminal output string from a mouse click operation, returns
            a dict containing information about the location and nature of the
            action.  If invalid, returns an empyty Dict.
        '''
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
