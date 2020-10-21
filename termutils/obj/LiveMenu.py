from typing import Tuple
import threading
import termios
import tty
import sys

class LiveMenu:

    '''
        Allows the user to display live, changing text on the terminal while
        simultaneously accepting user inputs.
    '''

    _dims = (24, 79)
    _active = False
    _fd = None
    _old_settings = None

    '''CONSTRUCTOR EXCEPTION'''

    def __init__(self):
        '''
            LiveMenu cannot be instantiated – all methods are class methods or
            static methods.
        '''
        msg = (
            "\n\nInvalid attempt to create instance of <class 'LiveMenu'>.\n"
            "All methods of this class are classmethod or staticmethod.\n"
        )
        raise RuntimeError(msg)

    '''GETTERS'''

    @classmethod
    def dims(cls) -> Tuple[int]:
        '''
            Returns the terminal dimensions.
        '''
        return cls._dims

    '''SETTERS'''

    @classmethod
    def set_dims(cls, rows:int = None, cols:int = None) -> None:
        '''
            Sets the terminal dimensions.
        '''
        if rows is None:
            rows = cls._dims[0]
        if cols is None:
            cols = cls._dims[1]
        cls._dims = (rows, cols)

    '''RUNTIME'''

    @classmethod
    def start(cls) -> None:
        '''
            Activates the LiveMenu session.
        '''
        if cls._active:
            msg = (
                'LiveMenu is already active, cannot run method `start` again.'
            )
            raise RuntimeError(msg)
        cls._active = True
        cls._fd = sys.stdin.fileno()
        cls._old_settings = termios.tcgetattr(cls._fd)
        tty.setraw(sys.stdin.fileno())

    @classmethod
    def stop(cls) -> None:
        '''
            Deactivates the LiveMenu session.
        '''
        if not cls._active:
            msg = (
                'LiveMenu must be active before running method `stop`.'
            )
            raise RuntimeError(msg)
        termios.tcsetattr(cls._fd, termios.TCSADRAIN, cls._old_settings)
        cls._fd = None
        cls._old_settings = None
        cls._active = False

    @classmethod
    def __enter__(cls) -> None:
        '''
            Context manager wrapper for `start`.
        '''
        cls.start()

    @classmethod
    def __exit__(cls) -> None:
        '''
            Context manager wrapper for `stop`.
        '''
        cls.stop()
