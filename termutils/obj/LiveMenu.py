from typing import Tuple, Callable
from atexit import register
import threading
import warnings
import termios
import tty
import sys

from termutils.config.defaults import term_height, term_width

class LiveMenu:

    '''
        Allows the user to display live, changing text on the terminal while
        simultaneously accepting user inputs.
    '''

    _active = False
    _fd = sys.stdin.fileno()
    _old_settings = termios.tcgetattr(_fd)
    _raw_mode = False

    '''CONSTRUCTOR'''

    def __init__(self, height:int = None, width:int = None) -> None:
        '''
            Creates a new, inactive instance of LiveMenu.  Arguments `height`
            and `width` should be integers greater than zero.
        '''
        if height is None:
            height = term_height

        if width is None:
            width = term_width

        self._dims = (height, width)
        self._current_active = False

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

    def set_display(self, display:Callable) -> None:
        '''
            Setting this value with a callable will cause the terminal display
            to print whatever is returned from `display`.  Callable should
            accept whatever is returned from `input` callable, seen in method
            `set_input`.
        '''
        self._display = display

    def set_input(self, input:Callable) -> None:
        '''
            Setting this value with a callable will cause the terminal display
            to include interactive actions.  Callable should allow for user
            input, which is then returned and read by the `display` callable.
        '''
        self._input = input

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
        self.__class__._raw(True)

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
