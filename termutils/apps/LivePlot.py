from string import ascii_letters, digits
import threading
import time

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from termutils.obj.LiveMenu import LiveMenu
from termutils.obj.String import String


class LivePlot(LiveMenu):

    def __init__(
    self, rows:int = None, cols:int = None, dt:float = 0.01,
    tab_len:int = 4) -> None:
        '''
            Creates an instance of LivePlot.
        '''
        self._dt = dt
        self._x_points = []
        self._y_points = []
        self._marker = '-'
        self._active_plot = False
        self._grid = True
        self._xlabel = ''
        self._ylabel = ''
        self._title = ''
        self._tab_len = 4
        super().__init__(rows, cols)

    def __call__(self) -> None:
        '''
            Creates a matplotlib plot that can be modified live, by accepting
            user inputs in the terminal simultaneously.
        '''
        print('\033[?25l', end = '', flush = True)

        # '0' for no input, '1' for function, '2' for limits, '3' for steps
        mode = 0

        steps = '1000'
        limval = (-1,1)
        xlabel = ''
        ylabel = ''
        str_in_history = []
        str_in = []
        active = True
        key_idx = 0
        btn_idx = 0

        btn_1_text = '[function]'
        btn_2_text = '[domain]'
        btn_3_text = '[steps]'
        btn_4_text = '[exit]'
        btn_5_text = '[xlabel]'
        btn_6_text = '[ylabel]'
        btn_7_text = '[grid]'

        color_b = 'white'
        color_0 = 'dark slate gray'
        color_1 = 'prussian blue'
        color_2 = 'indigo dye'
        color_3 = 'royal blue (dark)'
        color_4 = 'red'
        color_5 = 'space cadet'
        color_6 = 'navy blue'
        color_7 = 'midnight blue'

        btn_1_pos = (1, len(btn_1_text) + 2)
        btn_2_pos = (
            btn_1_pos[1], btn_1_pos[1] + len(btn_2_text) + 2
        )
        btn_3_pos = (
            btn_2_pos[1], btn_2_pos[1] + len(btn_3_text) + 2
        )
        btn_4_pos = (self.cols-len(btn_4_text)-2, self.cols-1)
        btn_5_pos = (
            btn_3_pos[1], btn_3_pos[1] + len(btn_5_text) + 2
        )
        btn_6_pos = (
            btn_5_pos[1], btn_5_pos[1] + len(btn_6_text) + 2
        )
        btn_7_pos = (
            btn_6_pos[1], btn_6_pos[1] + len(btn_7_text) + 2
        )

        btn_1_out = String(
            f' {btn_1_text} ', foreground = color_b, background = color_1,
            style = 'bold'
        )
        btn_2_out = String(
            f' {btn_2_text} ', foreground = color_b, background = color_2,
            style = 'bold'
        )
        btn_3_out = String(
            f' {btn_3_text} ', foreground = color_b, background = color_3,
            style = 'bold'
        )
        btn_4_out = String(
            f' {btn_4_text} ', foreground = color_b, background = color_4,
            style = 'bold'
        )
        btn_5_out = String(
            f' {btn_5_text} ', foreground = color_b, background = color_5,
            style = 'bold'
        )
        btn_6_out = String(
            f' {btn_6_text} ', foreground = color_b, background = color_6,
            style = 'bold'
        )
        btn_7_out = String(
            f' {btn_7_text} ', foreground = color_b, background = color_7,
            style = 'bold'
        )

        btn_list = [
            str(btn_1_out), str(btn_2_out), str(btn_3_out), str(btn_5_out),
            str(btn_6_out), str(btn_7_out)
        ]

        title = String(
            (
                f' | Click Buttons | Hold `ESC` to Quit | '
                f' Hit <Enter> to Confirm an Input | '
            ), foreground = color_b, background = color_0, style = 'bold'
        )
        title = '\n\r ' + str(title) + '\n\n\r '

        btn_1_out_down = String(
            f' {btn_1_text} ', foreground = color_1, background = color_b,
        )
        btn_2_out_down = String(
            f' {btn_2_text} ', foreground = color_2, background = color_b,
        )
        btn_3_out_down = String(
            f' {btn_3_text} ', foreground = color_3, background = color_b,
        )
        btn_4_out_down = String(
            f' {btn_4_text} ', foreground = color_4, background = color_b,
        )
        btn_5_out_down = String(
            f' {btn_5_text} ', foreground = color_5, background = color_b,
        )
        btn_6_out_down = String(
            f' {btn_6_text} ', foreground = color_6, background = color_b,
        )
        btn_7_out_down = String(
            f' {btn_7_text} ', foreground = color_7, background = color_b,
        )

        btn_4_spaces = self._dims[1] - 1 - sum(
            (
                len(btn_1_out), len(btn_2_out), len(btn_3_out), len(btn_4_out),
                len(btn_5_out), len(btn_6_out), len(btn_7_out)
            )
        )

        oper = ['.', '(', ')', '+', '-', '*', '/', '%', '@', 'Space']
        valid_inputs_1 = list(ascii_letters + digits) + oper
        valid_inputs_2 = list(digits) + [',', '.', '-', '+', 'E', 'e', 'Space']
        valid_inputs_3 = list(digits) + ['.', '-', '+', 'E', 'e']
        disp_str = (
            f'{title}{"".join(btn_list)}'
        )
        disp_str += ' '*btn_4_spaces + str(btn_4_out)
        print(f'\033[2J\033[3J\033[f{disp_str}', end = '', flush = True)
        x = np.linspace(-1, 1, int(steps))


        eqn = ''
        lims = f'{x[0]:g}, {x[-1]:g}'

        while active:

            if key_idx <= len(self._key_history) - 1 or \
               btn_idx <= len(self._btn_history) - 1:

                while key_idx <= len(self._key_history) - 1:

                    key = self._key_history[key_idx]

                    if key == 'Kill' or mode == 4:
                        self._kill = True
                        active = False
                        break
                    elif mode == 1:
                        str_in, limval, steps, eqn, x =\
                        self._mode_1(
                            key, valid_inputs_1, str_in, limval, steps, eqn, x
                        )

                    elif mode == 2:
                        str_in, limval, steps, eqn =\
                        self._mode_2(
                            key, valid_inputs_2, str_in, limval, steps, eqn
                        )

                    elif mode == 3:
                        str_in, limval, lims, steps, eqn, x, y =\
                        self._mode_3(
                            key, valid_inputs_3, str_in, limval, lims, steps,
                            eqn, self._x_points, self._y_points
                        )

                    elif mode == 5:
                        str_in, xlabel =\
                        self._mode_5(key, str_in, xlabel)

                    elif mode == 6:
                        str_in, ylabel =\
                        self._mode_6(key, str_in, ylabel)

                    key_idx += 1

                while btn_idx <= len(self._btn_history) - 1:

                    btn = self._btn_history[btn_idx]

                    if btn["action"] == 'LeftClick' and btn["y"] == 3:

                        if btn_1_pos[0] <= btn["x"] <= btn_1_pos[1]:
                            btn_list[0] = str(btn_1_out_down)
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out)}'
                            )
                            mode = 1
                            str_in = list(eqn)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)

                        elif btn_2_pos[0] <= btn["x"] <= btn_2_pos[1]:
                            btn_list[1] = str(btn_2_out_down)
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out)}'
                            )
                            mode = 2
                            str_in = list(lims)
                            btn_2_down = True
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)

                        elif btn_3_pos[0] <= btn["x"] <= btn_3_pos[1]:
                            btn_list[2] = str(btn_3_out_down)
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out)}'
                            )
                            mode = 3
                            str_in = list(steps)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)

                        elif btn_4_pos[0] <= btn["x"] <= btn_4_pos[1]:
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out_down)}'
                            )
                            mode = 4
                            self._key_history.append('Kill')
                            str_in = []
                            print('\033[?25l', end = '', flush = True)

                        elif btn_5_pos[0] <= btn["x"] <= btn_5_pos[1]:
                            btn_list[3] = str(btn_5_out_down)
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out)}'
                            )
                            mode = 5
                            str_in = list(xlabel)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)

                        elif btn_6_pos[0] <= btn["x"] <= btn_6_pos[1]:
                            btn_list[4] = str(btn_6_out_down)
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out)}'
                            )
                            mode = 6
                            str_in = list(ylabel)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)

                        elif btn_7_pos[0] <= btn["x"] <= btn_7_pos[1]:
                            btn_list[5] = str(btn_7_out_down)
                            disp_str = (
                                f'{title}{"".join(btn_list)}{" "*btn_4_spaces}'
                                f'{str(btn_4_out)}'
                            )
                            self._grid = not self._grid

                    elif btn["action"] == 'MouseUp':
                        btn_list = [
                            str(btn_1_out), str(btn_2_out), str(btn_3_out),
                            str(btn_5_out), str(btn_6_out), str(btn_7_out)
                        ]
                        disp_str = (
                            f'{title}{"".join(btn_list)}'
                        )
                        disp_str += ' '*btn_4_spaces + str(btn_4_out)

                    btn_idx += 1

                if mode == 0 or mode == 4:
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}'
                    )

                elif mode == 1:
                    msg = String(
                        ' f(x):= ' + "".join(str_in) + ' ',
                        foreground = color_b, background = color_1,
                        style = 'bold'
                    )
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r {msg}\b'
                    )
                elif mode == 2:
                    msg = String(
                        ' (x₀, x₁): (' + "".join(str_in) + ') ',
                        foreground = color_b, background = color_2,
                        style = 'bold'
                    )
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r {msg}\b\b'
                    )
                elif mode == 3:
                    msg = String(
                        ' steps= ' + "".join(str_in) + ' ',
                        foreground = color_b, background = color_3,
                        style = 'bold'
                    )
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r {msg}\b'
                    )
                elif mode == 5:
                    msg = String(
                        ' xlabel: \"' + "".join(str_in) + '\" ',
                        foreground = color_b, background = color_5,
                        style = 'bold'
                    )
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r {msg}\b\b'
                    )
                elif mode == 6:
                    msg = String(
                        ' ylabel: \"' + "".join(str_in) + '\" ',
                        foreground = color_b, background = color_6,
                        style = 'bold'
                    )
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r {msg}\b\b'
                    )
                print(text_str, end = '', flush = True)

            time.sleep(self._dt)

        print('\033[?25h', end = '', flush = True)
        print('\033[1 q', end = '', flush = True)

    def start(self) -> None:
        '''
            Activates the LiveMenu session.
        '''
        sns.set_theme()

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

        fig = plt.figure()
        fignum = fig.number
        ax = fig.add_subplot(111)
        line, = ax.plot(self._x_points, self._y_points)
        active = True
        self._active_plot = True
        fig.canvas.mpl_connect('close_event', self._inactivate_plot)
        fig.canvas.draw()

        x_points = self._x_points.copy()
        y_points = self._y_points.copy()
        xlabel = self._xlabel
        ylabel = self._ylabel
        title = self._title
        grid = self._grid

        try:
            print(f'\033[2J\033[3J\033[f', end = '', flush = True)
            t_listener.start()
            t_writer.start()

            while self._active_plot and not self._kill:
                if x_points != self._x_points or y_points != self._y_points:

                    x_points = self._x_points.copy()
                    y_points = self._y_points.copy()

                    line.set_data(x_points, y_points)

                    ax.relim()
                    ax.set_xlim(np.min(self._x_points), np.max(self._x_points))
                    ax.autoscale_view(True,True,True)
                    fig.canvas.draw()

                if xlabel != self._xlabel or ylabel != self._ylabel or \
                title != self._title or grid != self._grid:

                    xlabel = self._xlabel
                    ylabel = self._ylabel
                    title = self._title
                    grid = self._grid
                    ax.grid(grid)
                    ax.set_xlabel(xlabel)
                    ax.set_ylabel(ylabel)
                    ax.set_title(title)
                    fig.canvas.draw()

                plt.pause(self._dt)
            t_listener.join()
            t_writer.join()
        except Exception as e:
            print(f'\033[2J\033[3J\033[f', end = '', flush = True)
            self._raw(False)
            raise Exception(e)

        self._raw(False)
        try:
            plt.close('all')
        except:
            pass

    def _inactivate_plot(self):
        self._active_plot = False
        self._kill = True

    def _mode_1(self, key, valid_inputs, str_in, limval, steps, eqn, x):
        if key in valid_inputs:
            if key == 'Space':
                key = ' '
            str_in.append(key)
        elif key == 'Enter':
            try:
                temp_eqn = ''.join(str_in)
                y = list(eval(temp_eqn, {'np':np}, {'x':x}))
                if isinstance(y, (int, float)):
                    y = [y,]
                elif isinstance(y, np.ndarray):
                    y = list(y)
                if len(y) == len(x):
                    self._x_points, self._y_points =\
                    list(x), y.copy()
                eqn = temp_eqn
            except Exception as e:
                pass
        elif key == 'Backspace':
            if str_in:
                str_in = str_in[:-1]
        return str_in, limval, steps, eqn, x

    def _mode_2(self, key, valid_inputs, str_in, limval, steps, eqn):
        if key in valid_inputs:
            if key == 'Space':
                key = ' '
            str_in.append(key)
        elif key == 'Enter':
            try:
                temp_lims = ''.join(str_in)
                limval = eval(f'({temp_lims})', {'np':np}, {})
                assert isinstance(limval, tuple)
                assert len(limval) == 2
                assert isinstance(limval[0], (int, float))
                assert isinstance(limval[1], (int, float))
                stepval = eval(steps, {'np':np}, {})
                x = np.linspace(limval[0], limval[1], int(stepval))
                y = list(eval(eqn, {'np':np}, {'x':x}))
                if len(y) == len(x):
                    self._x_points, self._y_points =\
                    list(x), y.copy()
                lims = temp_lims
            except Exception as e:
                pass
        elif key == 'Backspace':
            if str_in:
                str_in = str_in[:-1]
        return str_in, limval, steps, eqn

    def _mode_3(
    self, key, valid_inputs, str_in, limval, lims, steps, eqn, x, y):
        if key in valid_inputs:
            if key == 'Space':
                key = ' '
            str_in.append(key)
        elif key == 'Enter':
            try:
                temp_steps = ''.join(str_in)
                stepval = eval(temp_steps, {'np':np}, {})
                assert isinstance(stepval, (int, float))
                assert int(stepval) == stepval
                assert stepval > 1
                limval = eval(f'({lims})', {'np':np}, {})
                x = np.linspace(
                    limval[0], limval[1], int(stepval)
                )
                y = list(eval(eqn, {'np':np}, {'x':x}))
                if len(y) == len(x):
                    self._x_points, self._y_points =\
                    list(x), y.copy()
                steps = temp_steps
            except Exception as e:
                pass
        elif key == 'Backspace':
            if str_in:
                str_in = str_in[:-1]
        return str_in, limval, lims, steps, eqn, x, y

    def _mode_5(self, key, str_in, xlabel):
        if len(repr(key)) == 3:
            str_in.append(key)
        elif key == 'Space':
            str_in.append(' ')
        elif key == 'Tab':
            str_in.append(' '*self._tab_len)
        elif key == 'Enter':
            try:
                xlabel = ''.join(str_in)
                self._xlabel = xlabel
            except Exception as e:
                pass
        elif key == 'Backspace':
            if str_in:
                str_in = str_in[:-1]
        return str_in, xlabel

    def _mode_6(self, key, str_in, ylabel):
        if len(repr(key)) == 3:
            str_in.append(key)
        elif key == 'Space':
            str_in.append(' ')
        elif key == 'Tab':
            str_in.append(' '*self._tab_len)
        elif key == 'Enter':
            try:
                ylabel = ''.join(str_in)
                self._ylabel = ylabel
            except Exception as e:
                pass
        elif key == 'Backspace':
            if str_in:
                str_in = str_in[:-1]
        return str_in, ylabel
