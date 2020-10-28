from string import ascii_letters, digits
import threading
import time

import matplotlib.pyplot as plt
import numpy as np

from termutils.obj.LiveMenu import LiveMenu
from termutils.obj.String import String

class LivePlot(LiveMenu):

    def __init__(self, rows:int = None, cols:int = None, dt:float = 0.01) -> None:
        '''
            Creates an instance of LivePlot.
        '''
        self._dt = dt
        self._x_points = []
        self._y_points = []
        self._marker = '-'
        self._kill = False
        self._active_plot = False
        super().__init__(rows, cols)

    def __call__(self) -> None:
        '''
            Creates a matplotlib plot that can be modified live, by accepting
            user inputs in the terminal simultaneously.
        '''
        print('\033[?25l', end = '', flush = True)

        # '0' for no input, '1' for function input, '2' for limits input
        mode = 0

        steps = '1000'
        str_in_history = []
        str_in = []
        active = True
        key_idx = 0
        btn_idx = 0
        row = 0
        col = 0

        btn_1_text = 'function'
        btn_2_text = 'domain'
        btn_3_text = 'steps'
        btn_4_text = 'exit'

        btn_1_pos = (1, len(btn_1_text) + 2)
        btn_2_pos = (
            btn_1_pos[1], btn_1_pos[1] + len(btn_2_text) + 2
        )
        btn_3_pos = (
            btn_2_pos[1], btn_2_pos[1] + len(btn_3_text) + 2
        )
        btn_4_pos = (self.cols-len(btn_4_text)-3, self.cols-1)

        btn_1_out = String(
            f' {btn_1_text} ', foreground = 'white', background = 'purple',
            style = 'bold'
        )
        btn_2_out = String(
            f' {btn_2_text} ', foreground = 'white', background = 'green',
            style = 'bold'
        )
        btn_3_out = String(
            f' {btn_3_text} ', foreground = 'white', background = 'blue',
            style = 'bold'
        )
        btn_4_out = String(
            f' {btn_4_text} ', foreground = 'white', background = 'red',
            style = 'bold'
        )

        oper = ['.', '(', ')', '+', '-', '*', '/', '%', '@', 'Space']
        valid_inputs_1 = list(ascii_letters + digits) + oper
        valid_inputs_2 = list(digits) + [',', '.', '-', '+', 'E', 'e', 'Space']
        valid_inputs_3 = list(digits) + ['.', '-', '+', 'E', 'e']
        disp_str = (
            f'\n\rClick a Button to Modify Plot (Hold `ESC` to Quit)'
            f'\n\n\r {btn_1_out}{btn_2_out}{btn_3_out}'
        )
        print(f'\033[2J\033[3J\033[f{disp_str}', end = '', flush = True)
        x = np.linspace(-1, 1, int(steps))


        eqn = ''
        lims = f'{x[0]:g}, {x[-1]:g}'

        while active:

            if key_idx <= len(self._key_history) - 1 or \
               btn_idx <= len(self._btn_history) - 1:

                while key_idx <= len(self._key_history) - 1:

                    key = self._key_history[key_idx]

                    if key == 'Kill':
                        self._kill = True
                        active = False
                        break
                    elif mode == 1:
                        if key in valid_inputs_1:
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
                                str_in_history.append(str_in.copy())
                                eqn = temp_eqn
                            except Exception as e:
                                pass
                        elif key == 'Backspace':
                            if str_in:
                                str_in = str_in[:-1]
                    elif mode == 2:
                        if key in valid_inputs_2:
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
                                str_in_history.append(str_in.copy())
                                lims = temp_lims
                            except Exception as e:
                                pass
                        elif key == 'Backspace':
                            if str_in:
                                str_in = str_in[:-1]
                    elif mode == 3:
                        if key in valid_inputs_3:
                            if key == 'Space':
                                key = ' '
                            str_in.append(key)
                        elif key == 'Enter':
                            try:
                                temp_steps = ''.join(str_in)
                                stepval = eval(temp_steps, {'np':np}, {})
                                assert isinstance(stepval, (int, float))
                                assert int(stepval) == stepval
                                limval = eval(f'({lims})', {'np':np}, {})
                                x = np.linspace(
                                    limval[0], limval[1], int(stepval)
                                )
                                y = list(eval(eqn, {'np':np}, {'x':x}))
                                if len(y) == len(x):
                                    self._x_points, self._y_points =\
                                    list(x), y.copy()
                                str_in_history.append(str_in.copy())
                                steps = temp_steps
                            except Exception as e:
                                pass
                        elif key == 'Backspace':
                            if str_in:
                                str_in = str_in[:-1]
                    key_idx += 1

                while btn_idx <= len(self._btn_history) - 1:

                    btn = self._btn_history[btn_idx]

                    if btn["action"] == 'LeftClick' and btn["y"] == 3:

                        if btn_1_pos[0] <= btn["x"] <= btn_1_pos[1]:
                            mode = 1
                            str_in = list(eqn)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)


                        elif btn_2_pos[0] <= btn["x"] <= btn_2_pos[1]:
                            mode = 2
                            str_in = list(lims)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)


                        elif btn_3_pos[0] <= btn["x"] <= btn_3_pos[1]:
                            mode = 3
                            str_in = list(steps)
                            print('\033[?25h', end = '', flush = True)
                            print('\033[5 q', end = '', flush = True)

                    btn_idx += 1

                if mode == 0:
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}{"".join(str_in)}'
                    )
                elif mode == 1:
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r f(x):= '
                        f'{"".join(str_in)}'
                    )
                elif mode == 2:
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r (x₀, x₁): '
                        f'({"".join(str_in)})\b'
                    )
                elif mode == 3:
                    text_str = (
                        f'\033[2J\033[3J\033[f{disp_str}\n\n\r steps= '
                        f'{"".join(str_in)}'
                    )
                print(text_str, end = '', flush = True)

            time.sleep(self._dt)

        print('\033[?25h', end = '', flush = True)
        print('\033[1 q', end = '', flush = True)

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

        # plt.ion()
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
