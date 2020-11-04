from typing import Tuple, Callable, Union, Dict
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
        Superclass that allows the user to display live, changing text on the
        terminal while simultaneously accepting user inputs.

        Must be inherited before instantiation, and __call__ must be
        overwritten.  The overwritten __call__ should contain the main loop
        displayed to the terminal
    '''

    _active = False
    _fd = term_fd                   # sys.stdin.fileno()
    _old_settings = term_settings   # termios.tcgetattr(_fd)
    _raw_mode = False

    '''CONSTRUCTOR'''

    def __init__(
    self, rows:int = None, cols:int = None, escape_hits:int = 15) -> None:
        '''
            Creates a new, inactive instance of LiveMenu.  Arguments `rows`
            and `cols` should be integers greater than zero.
        '''
        if rows is None:
            rows = term_rows

        if cols is None:
            cols = term_cols

        self._escape_hits = escape_hits

        self._dims = (rows, cols)
        self._current_active = False
        self._listener = self._default_listener
        self._kill = False
        self._key_history = []
        self._btn_history = []

    '''GETTERS'''

    @property
    def dims(self) -> Tuple[int]:
        '''
            Returns the terminal dimensions.
        '''
        return self._dims

    @property
    def rows(self) -> int:
        '''
            Returns the display height (number of rows).
        '''
        return self._dims[0]

    @property
    def cols(self) -> int:
        '''
            Returns the display width (number of columns).
        '''
        return self._dims[1]

    @property
    def active(self) -> bool:
        '''
            Returns True if the current instance is active. False otherwise.
        '''
        return self._current_active

    def __call__(self):
        '''
            Must be inherited before instantiation, and __call__ must be
            overwritten.  The overwritten __call__ should contain the main loop
            that prints to the terminal.
        '''
        raise NotImplementedError(self.__call__.__doc__)

    '''SETTERS'''

    def set_dims(self, rows:int = None, cols:int = None) -> None:
        '''
            Sets the terminal dimensions.
        '''
        if rows is None:
            rows = self._dims[0]
        if cols is None:
            cols = self._dims[1]
        self._dims = (rows, cols)

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
        t_writer = threading.Thread(target = self.__call__)

        self._raw(True)

        try:
            print(f'\033[2J\033[3J\033[f', end = '', flush = True)
            t_listener.start()
            t_writer.start()

            while t_listener.is_alive():
                time.sleep(0.01)

            t_listener.join()
            t_writer.join()
        except Exception as e:
            print(f'\033[2J\033[3J\033[f', end = '', flush = True)
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

        print(f'\033[2J\033[3J\033[f', end = '', flush = True)

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

    def _default_listener(self) -> str:
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
            while not self._kill:
                output = self._get_input()
                if output == 'Esc':
                    if escape_hitcount < self._escape_hits - 1:
                        escape_hitcount += 1
                        continue
                    else:
                        self._key_history.append('Kill')
                        break
                elif escape_hitcount > 0 and output != 'Esc':
                    escape_hitcount = 0
                if isinstance(output, str):
                    self._key_history.append(output)
                elif isinstance(output, dict):
                    self._btn_history.append(output)
        except Exception as e:
            print('\033[?1002l', end = '', flush = True)
            raise Exception(e)
        print('\033[?1002l', end = '', flush = True)

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
            return None
        btn_key = ord(output[3])
        if btn_key not in mouse_btns:
            return None
        else:
            dict_out = {
                'action'    : mouse_btns[ord(output[3])],
                'x'         : ord(output[4])-33,
                'y'         : ord(output[5])-33,
            }
        return dict_out
