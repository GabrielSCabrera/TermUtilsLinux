from string import punctuation, whitespace
from typing import Tuple, Callable, Any
import threading
import warnings
import readline
import termios
import time
import tty
import sys
import os

from termutils.config.keys import keys as keys_dict
from termutils.config.defaults import (
    term_rows, term_cols, term_fd, term_settings
)


class LiveMenu:

    '''
        Allows the user to display live, changing text on the terminal while
        simultaneously accepting user inputs.
    '''

    _active = False
    _fd = term_fd#sys.stdin.fileno()
    _old_settings = term_settings#termios.tcgetattr(_fd)
    _raw_mode = False
    _input_state = []       # History of all keys pressed

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

        t_listener.start()
        t_writer.start()

        while t_listener.is_alive():
            time.sleep(0.01)

        t_listener.join()
        t_writer.join()

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
        '''
        escape_hitcount = 0
        while True:
            output = cls._get_key_press()
            if output == 'Esc':
                if escape_hitcount < escape_hits - 1:
                    escape_hitcount += 1
                    continue
                else:
                    cls._input_state.append('Kill')
                    break
            elif escape_hitcount > 0 and output != 'Esc':
                escape_hitcount = 0
            cls._input_state.append(output)

        cls._raw(False)

    @classmethod
    def _get_key_press(cls):
        '''
            Returns the last key (or key combination) pressed as a string.
        '''
        key = os.read(1,20).decode()
        if key in keys_dict.keys():
            output = keys_dict[str(key)]
        else:
            output = key
        return output

    @classmethod
    def _default_writer(cls, sleep:float = 0.05):
        '''
            Default writer – will simply act as a simple text-editor.
        '''
        active = True
        idx = 0
        str_out = ''
        print(f'\033[2J\033[f', end = '', flush = True)
        delims = list(punctuation + whitespace)
        while active:
            if len(cls._input_state) > idx:
                while len(cls._input_state) > idx:
                    step = cls._input_state[idx]
                    if len(step) == 1:
                        str_out += step
                    elif step == 'Backspace':
                        str_out = str_out[:-1]
                    elif step == 'Ctrl-Backspace':
                        start = True
                        while True:
                            if start and str_out[-1] in delims:
                                pass
                            elif start and str_out[-1] not in delims:
                                start = False
                            elif len(str_out) == 0 or str_out[-1] in delims:
                                break
                            str_out = str_out[:-1]
                    elif step == 'Alt-Backspace':
                        while True:
                            if len(str_out) == 0 or str_out[-1] == '\n':
                                break
                            str_out = str_out[:-1]
                    elif step == 'Space':
                        str_out += ' '
                    elif step == 'Enter':
                        str_out += '\r\n'
                    elif step == 'Tab':
                        str_out += ' '*4
                    elif step == 'Kill':
                        active = False
                        break
                    idx += 1
                if str_out != '':
                    split_lines = str_out.split('\n')
                    row = len(split_lines)
                    col = len(split_lines[-1])+1
                else:
                    row = 0
                    col = 0
                out = f'\033[f\033[2J\r{str_out}\033[{row};{col}f'
                print(out, end = '', flush = True)
            time.sleep(sleep)
