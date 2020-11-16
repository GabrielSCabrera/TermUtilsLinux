from typing import Union, Tuple
from textwrap import wrap

from termutils.obj.Color import Color
from termutils.config import defaults

class Widget:

    '''
        Backend used to simplify & standardize more complex classes such as
        <class 'Button'> or <class 'Display'>.  Should normally be inherited.
    '''

    def __init__(
    self, x0:int, y0:int, x1:int, y1:int, background:Union[str, Color] = None,
    foreground:Union[str, Color] = None):
        '''
            Returns a new instance of class `Widget`.  Shouldn't normally be
            instantiated directly, but inherited.
        '''
        # `Widget`, or the name of the subclass that inherits `Widget`.
        self._cls_name = self.__class__.__name__
        self._type = f'<class \'{self._cls_name}\'>'

        for i,j in zip((y1, y0, x1, x0), ('y1', 'y0', 'x1', 'x0')):
            if i != int(i) or i < 0:
                msg = (
                    f'\n\nArgument `{j}` in the instantiation of {self._type} '
                    f'must be a positive integer.'
                )
                raise ValueError(msg)

        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1

        self._size = (y1-y0)*(x1-x0)
        self._shape = (y1-y0, x1-x0)
        self._view = np.zeros(2, dtype = np.int64)

        for i,j in zip(self._shape, (('y1','y0'), ('x1','x0'))):
            if i <= 0:
                msg = (
                    f'\n\nArgument `{j[0]}` must be larger than argument '
                    f'`{j[1]}` in the instantiation of {self._type}.'
                )
                raise ValueError(msg)

        if background is None:
            background = defaults.background_color
        elif isinstance(background, str):
            background = Color.palette(background)
        elif isinstance(background, (tuple, list, np.ndarray)):
            background = Color(background)
        elif not isinstance(background, Color):
            msg = (
                f'\n\nArgument `background` in instantiation of {self._type} '
                f'must be a valid color as an instance of <class \'str\'>, or '
                f'an instance of <class \'Color\'>.\n\nCannot recognize the'
                f' user-provided color: `{background}`.'
            )
            raise ValueError(msg)

        if foreground is None:
            foreground = defaults.foreground_color
        elif isinstance(foreground, str):
            foreground = Color.palette(foreground)
        elif isinstance(foreground, (tuple, list, np.ndarray)):
            foreground = Color(foreground)
        elif not isinstance(foreground, Color):
            msg = (
                f'\n\nArgument `foreground` in instantiation of {self._type} '
                f'must be a valid color as an instance of <class \'str\'>, or '
                f'an instance of <class \'Color\'>.\n\nCannot recognize the'
                f' user-provided color: `{foreground}`.'
            )
            raise ValueError(msg)

        self._text = self.__call__('')

    def __call__(self, text:str) -> None:
        '''
            Sets the current state of the widget to the given text.
        '''
        if not isinstance(text, str):
            msg = (
                f'\n\nAttribute `text` in calling of {self._type} instance must'
                f' be of <class \'str\'>.'
            )
            raise TypeError(msg)
        self._text = text

    def set_view(self, y:int, x:int) -> None:
        '''
            Sets the current view on the text to the given coordinates. For
            example, given a widget with shape (rows=1, cols=10) the string

              "We're no strangers to love\nYou know the rules and so do I"

            would by default only display: "We're no s".  By default, the view
            is set to (y=0, x=0), the values representing the upper left part
            of the view into the text.

            If we were to run set_view(y=0, x=10), then the widget would instead
            display "trangers t". Or if we run set_view(y=1, x=-15), we would
            get "les and so".
        '''

        for i,j in zip((y,x), ('y','x')):
            if not isinstance(i, (int, float)) or i != int(i):
                msg = (
                    f'\n\nAttribute `{j}` in method `set_view` of a '
                    f'{self._type} instance must be an integer.'
                )
                raise TypeError(msg)

        y_idx = np.arange(0, self._shape[0], 1)
        x_idx = np.arange(0, self._shape[1], 1)

        Y,X = np.meshgrid(y_idx, x_idx)

        # TODO: THIS STUFF

    # def scroll(self, )

    def lines(self, fmt_spec:str = '<') -> Tuple[str]:
        '''
            Returns the current view of the text: this is dependent on the
            text dimensions and shape of the widget, as well as the current
            view state.

            The returned list will contain equidistant strings, each exactly as
            long as the widget's width.
        '''
        rows = []
        for i in self._text:
            rows.append(f'{i:{fmt_spec}{self._shape[1]}s}')
        return tuple(rows)
