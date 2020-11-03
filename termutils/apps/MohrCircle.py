from string import ascii_letters, digits
from typing import Union
import threading
import time

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from termutils.obj.LiveMenu import LiveMenu
from termutils.obj.String import String
from termutils.obj.Color import Color

class MohrCircle(LiveMenu):

    def __init__(
    self, rows:int = None, cols:int = None, facecolor:str = 'C0',
    edgecolor:str = 'C1', annotations:bool = False, dt:float = 1E-3):
        '''
            Creates an interactive Mohr circle visualizer
        '''
        self._facecolor = facecolor
        self._edgecolor = edgecolor
        self._annotations = annotations
        self._dt = dt
        self._stress_tensor = np.zeros((3,3))
        self._update_principal_stresses()
        super().__init__(rows = rows, cols = cols)

    def _update_principal_stresses(self):
        '''
            Calculates the principal stresses sigma_1, sigma_2, sigma_3, and
            their three respective orientations in vector form.
        '''
        self._ps, self._ori = np.linalg.eig(self._stress_tensor)

    def _calculate_circles(self):
        '''
            Calculates and returns the centers and radii of each circle to be
            plotted.
        '''
        s_1 = self._ps[0]
        s_2 = self._ps[1]
        s_3 = self._ps[2]

        C1 = ((s_2 + s_3)/2, 0)
        R1 = abs((s_2 - s_3)/2)

        C2 = ((s_1 + s_3)/2, 0)
        R2 = abs((s_1 - s_3)/2)

        C3 = ((s_1 + s_2)/2, 0)
        R3 = abs((s_1 - s_2)/2)

        return C1, R1, C2, R2, C3, R3

    def _calculate_lims(self, C1, R1, C2, R2, C3, R3, pad:float = 0.2):
        '''
            Calculates and returns xlim and ylim to allow the user to see the
            Mohr diagrams as they update.
        '''
        y_bottom_1 = C1[1] - R1
        y_bottom_2 = C2[1] - R2
        y_bottom_3 = C3[1] - R3

        y_top_1 = C1[1] + R1
        y_top_2 = C2[1] + R2
        y_top_3 = C3[1] + R3

        x_left_1 = C1[0] - R1
        x_left_2 = C2[0] - R2
        x_left_3 = C3[0] - R3

        x_right_1 = C1[0] + R1
        x_right_2 = C2[0] + R2
        x_right_3 = C3[0] + R3

        xlim = (
            min(x_left_1, x_left_2, x_left_3),
            max(x_right_1, x_right_2, x_right_3)
        )

        ylim = (
            min(y_bottom_1, y_bottom_2, y_bottom_3),
            max(y_top_1, y_top_2, y_top_3)
        )

        dx = xlim[1] - xlim[0]
        dy = ylim[1] - ylim[0]

        xlim = (xlim[0] - dx*pad, xlim[1] + dx*pad)
        ylim = (ylim[0] - dy*pad, ylim[1] + dy*pad)

        if dx > dy:
            dxy = 0.5*(dx - dy)
            ylim = (ylim[0] - dxy, ylim[1] + dxy)
        elif dy > dx:
            dxy = 0.5*(dy - dx)
            xlim = (xlim[0] - dxy, xlim[1] + dxy)

        return xlim, ylim

    def _inactivate_plot(self):
        self._active_plot = False
        self._kill = True

    def start(self):
        '''
            Activates the MohrCircle session.
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

        fig = plt.figure()
        fignum = fig.number
        ax = fig.add_subplot(111)

        ax.set_aspect('equal')

        ax.axhline(y = 0, color = 'k', linestyle = '--')
        ax.axvline(x = 0, color = 'k', linestyle = '--')

        ax.set_xlabel(r'$\sigma_n$')
        ax.set_ylabel(r'$\tau_n$')

        stress_tensor = self._stress_tensor.copy()
        self._update_principal_stresses()
        C1, R1, C2, R2, C3, R3 = self._calculate_circles()

        circle_2 = ax.add_artist(plt.Circle(
            C2, R2, edgecolor = self._edgecolor, facecolor = self._facecolor
        ))
        circle_1 = ax.add_artist(plt.Circle(
            C1, R1, edgecolor = self._edgecolor, facecolor = 'w'
        ))
        circle_3 = ax.add_artist(plt.Circle(
            C3, R3, edgecolor = self._edgecolor, facecolor = 'w'
        ))

        xlim, ylim = self._calculate_lims(C1, R1, C2, R2, C3, R3)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        active = True
        self._active_plot = True
        fig.canvas.mpl_connect('close_event', self._inactivate_plot)
        fig.canvas.draw()

        try:
            print(f'\033[2J\033[3J\033[f', end = '', flush = True)
            t_listener.start()
            t_writer.start()

            while self._active_plot and not self._kill:
                if not np.array_equal(self._stress_tensor, stress_tensor):

                    stress_tensor = self._stress_tensor.copy()
                    self._update_principal_stresses()
                    C1, R1, C2, R2, C3, R3 = self._calculate_circles()

                    circle_2.set_radius(R2)
                    circle_1.set_radius(R1)
                    circle_3.set_radius(R3)

                    circle_2.set_center(C2)
                    circle_1.set_center(C1)
                    circle_3.set_center(C3)

                    # ax.relim()
                    xlim, ylim = self._calculate_lims(C1, R1, C2, R2, C3, R3)
                    ax.set_xlim(xlim)
                    ax.set_ylim(ylim)
                    # ax.autoscale_view(True, True, True)
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

    def __call__(self):
        '''
            The user interface.
        '''
        print('\033[?25l', end = '', flush = True)

        active = True
        key_idx = 0
        btn_idx = 0

        disp_str = 'Mohr Circle Plotter'

        print(f'\033[2J\033[3J\033[f{disp_str}', end = '', flush = True)

        while active:
            msg = ''

            if key_idx <= len(self._key_history) - 1 or \
               btn_idx <= len(self._btn_history) - 1:

                while key_idx <= len(self._key_history) - 1:

                    key = self._key_history[key_idx]

                    if key == 'Kill':
                        self._kill = True
                        active = False
                        break
                    elif key == 'Up':
                        self._stress_tensor[0,0] += 1
                    elif key == 'Down':
                        self._stress_tensor[0,0] -= 1
                    elif key == 'Left':
                        self._stress_tensor[2,2] += 1
                    elif key == 'Right':
                        self._stress_tensor[2,2] -= 1

                    key_idx += 1

                while btn_idx <= len(self._btn_history) - 1:

                    btn_idx += 1

                text_str = (
                    f'\033[2J\033[3J\033[f{disp_str}\n\n\r {msg}\b\b'
                )
                print(text_str, end = '', flush = True)

            time.sleep(self._dt)

        print('\033[?25h', end = '', flush = True)
        print('\033[1 q', end = '', flush = True)
