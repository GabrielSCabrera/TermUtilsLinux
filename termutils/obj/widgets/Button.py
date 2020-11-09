from warnings import warn
from textwrap import wrap
from typing import Union

from termutils.obj.Color import Color
from termutils.config import defaults

class Button:
    '''
        A button with a user-selected background color, text color, text style,
        and string.  To be used with class `SmartMenu`.
    '''

    def __init__(
    self, x0:int, y0:int, x1:int, y1:int, text:str, style:str = None,
    background:Union[str, Color] = None, foreground:Union[str, Color] = None):
        '''
            Returns a new instance of class `Button`.
        '''
        text = text.strip()

        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
        self._text = text

        self._size = (y1-y0)*(x1-x0)
        self._shape = (y1-y0, x1-x0)

        if self._shape[0] <= 0 or self._shape[1] <= 0:
            msg = (
                f'\n\nWhen instantiating class `Button`, arguments `x1` and '
                f'`y1` must be larger than `x0` and `y0`, respectively.'
            )
            raise ValueError(msg)

        if background is None:
            background = defaults.btn_background
        elif isinstance(background, str):
            background = Color.palette(background)
        elif isinstance(background, (tuple, list, np.ndarray)):
            background = Color(background)
        elif not isinstance(background, Color):
            msg = (
                f'\n\nInvalid attempt to create `Button` with background color '
                f'`{background}`.'
            )
            raise ValueError(msg)

        if foreground is None:
            foreground = defaults.btn_foreground
        elif isinstance(foreground, str):
            foreground = Color.palette(foreground)
        elif isinstance(foreground, (tuple, list, np.ndarray)):
            foreground = Color(foreground)
        elif not isinstance(foreground, Color):
            msg = (
                f'\n\nInvalid attempt to create `Button` with text color '
                f'`{foreground}`.'
            )
            raise ValueError(msg)

        if not isinstance(text, str):
            msg = (
                f'\n\nArgument `text` in constructor of class `Button` expects '
                f'a value of <class \'str\'>, got {type(text)}.'
            )
            raise TypeError(text)
        elif len(text) > self._size:
            msg = (
                f'\n\nButton text `{text}` will be cut off since text length '
                f'({len(text)}) exceeds button dimensions ({self._size}).'
            )
            self._text = text[:self._size-1].strip() + '…'
            warn(msg)
        elif len(text) > self._shape[1]:
            msg = (
                f'\n\nButton text `{text}` will be separated into multiple '
                f'lines, since text length ({len(text)}) exceeds button width '
                f'({(x1-x0)}).'
            )
            warn(msg)
        self._text = wrap(self._text, self._shape[1])

    def check_lims(self, x:int, y:int) -> bool:
        '''
            If the given coordinate is within the button limits, returns True.
            Returns False otherwise.
        '''
        if y < y0:
            return False
        elif y > y1:
            return False
        elif x < x0:
            return False
        elif x > x1:
            return False
        else:
            return True
