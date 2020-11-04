from string import digits
from typing import Union
import threading
import time

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from termutils.obj.LiveMenu import LiveMenu
from termutils.obj.String import String

class MohrCircle(LiveMenu):

    def __init__(
    self, rows:int = None, cols:int = None, facecolor:str = 'C0',
    edgecolor:str = 'C1', annotations:bool = False, dt:float = 1E-2):
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
        self._escape_hits = 1

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

    def _get_buttons(self, selected:int = 0):
        '''
            Prepares the buttons that will be used to select options in the
            menu. `selected` is a value 0-9, where 0 means nothing is selected,
            and 1-9 represent the stress tensor elements in the order:

                    σ₁₁, σ₁₂, σ₁₃, σ₂₁, σ₂₂, σ₂₃, σ₃₁, σ₃₂, σ₃₃
        '''
        buttons_matrix = [
            ['σ₁₁', 'σ₁₂', 'σ₁₃'],
            ['σ₂₁', 'σ₂₂', 'σ₂₃'],
            ['σ₃₁', 'σ₃₂', 'σ₃₃'],
        ]

        color_1 = 'black'
        color_2 = 'white'

        selected_color_1 = 'cadmium green'
        selected_color_2 = 'magic mint'

        border_color_1 = 'white'
        border_color_2 = 'sapphire'

        b_colors = [
            [color_1, color_1, color_1],
            [color_1, color_1, color_1],
            [color_1, color_1, color_1],
        ]

        t_colors = [
            [color_2, color_2, color_2],
            [color_2, color_2, color_2],
            [color_2, color_2, color_2],
        ]

        if selected != 0:
            selected -= 1
            idx = (int(selected // 3), int(selected % 3))
            b_colors[idx[0]][idx[1]] = selected_color_1
            t_colors[idx[0]][idx[1]] = selected_color_2

        row = 1
        col = 1
        idx = []
        labels = []

        border_mid = str(String(' ', border_color_1, border_color_2))

        h_border_top = '┌' + 21*' ' + '┐'
        h_border_top = str(String(h_border_top, border_color_1, border_color_2))
        h_border_bot = '└' + 21*' ' + '┘'
        h_border_bot = str(String(h_border_bot, border_color_1, border_color_2))

        v_border = str(String('│', border_color_1, border_color_2))

        rows = [h_border_top]
        for c1,(i,j,k) in enumerate(zip(buttons_matrix, b_colors, t_colors)):
            rows.append(v_border + border_mid)
            for c2,(l,m,n) in enumerate(zip(i,j,k)):
                new_col = col + len(l) + 2
                idx.append([row, col+1, new_col])
                labels.append(l)
                rows[-1] += str(String(f' {l} ', m, n, 'bold'))
                if c2 < len(i) - 1:
                    rows[-1] += border_mid*2
                else:
                    rows[-1] += border_mid + v_border
                col = new_col + 2
            if c1 < len(buttons_matrix) - 1:
                rows.append(v_border + border_mid*21 + v_border)
            else:
                rows.append(h_border_bot)
            row += 2
            col = 1

        return idx, labels, rows

    def _get_st_rows(self):
        '''
            Returns the stress tensor as a list of formatted strings.
        '''
        num_rows = [' '*7 + '┌' + ' '*30 + '┐']
        for n,i in enumerate(self._stress_tensor):
            if n == 1:
                num_rows.append(' '*3 + '=' + ' '*3 + '│')
            else:
                num_rows.append(' '*7 + '│')
            for j in i:
                num_rows[-1] += f'{j:>9.2E} '
            num_rows[-1] = num_rows[-1] + '│'
            if n < self._stress_tensor.shape[0] - 1:
                num_rows.append(' '*7 + '│' + ' '*30 + '│')
        num_rows.append(' '*7 + '└' + ' '*30 + '┘')
        return num_rows

    def __call__(self):
        '''
            The user interface.
        '''
        print('\033[?25l', end = '', flush = True)

        active = True
        key_idx = 0
        btn_idx = 0
        selected = 0
        mode = 0
        user_io = ''
        x0_mat, y0_mat = 0, 4

        valid_inputs = list(digits) + ['.', '-', '+', 'E', 'e']

        str_in = []

        disp_str = ' '*12 + 'Mohr Circle Plotter (ESC to Quit)' + ' '*17
        disp_str += '\n\r' + ' '*62 + '\n\r' + '    Click to Modify' + ' '*16
        disp_str += 'Current Stress Tensor      '

        disp_str = str(String(
            disp_str, foreground = 'white', background = 'black', style = 'bold'
        ))

        print(f'\033[2J\033[3J\033[f{disp_str}', end = '', flush = True)

        idx, labels, rows = self._get_buttons(selected = selected)

        mat = self._get_st_rows()

        for n,(i,j) in enumerate(zip(rows, mat)):
            rows[n] = f"{i}{j}"

        msg = '\n\r'.join(rows)
        text_str = (
            f'\033[2J\033[3J\033[f{disp_str}\n\n\r{msg}{user_io}'
        )
        print(text_str, end = '', flush = True)

        while active:

            if key_idx <= len(self._key_history) - 1 or \
                btn_idx <= len(self._btn_history) - 1:

                while key_idx <= len(self._key_history) - 1:

                    key = self._key_history[key_idx]

                    if key == 'Kill':
                        self._kill = True
                        active = False
                        break
                    elif key == 'Up':
                        self._stress_tensor[0,0] += 0.25
                    elif key == 'Down':
                        self._stress_tensor[0,0] -= 0.25
                    elif key == 'Left':
                        self._stress_tensor[2,2] += 0.25
                    elif key == 'Right':
                        self._stress_tensor[2,2] -= 0.25
                    elif mode != 0:
                        if key in valid_inputs:
                            str_in.append(key)
                        elif key == 'Enter':
                            try:
                                new_val = eval(''.join(str_in), {'np':np})
                                i = (int((mode-1) // 3), int((mode-1) % 3))
                                self._stress_tensor[i[0], i[1]] = new_val
                                self._stress_tensor[i[1], i[0]] = new_val
                                str_in = []
                                mode = 0
                            except Exception as e:
                                pass
                        elif key == 'Backspace' and str_in:
                            str_in = str_in[:-1]

                    key_idx += 1

                while btn_idx <= len(self._btn_history) - 1:

                    action = self._btn_history[btn_idx]['action']
                    x = self._btn_history[btn_idx]['x'] - x0_mat
                    y = self._btn_history[btn_idx]['y'] - y0_mat

                    if action == 'LeftClick':
                        for n,i in enumerate(idx):
                            if i[0] == y and i[1] <= x <= i[2]:
                                selected = n + 1
                                mode = n + 1
                                j = (int((mode-1) // 3), int((mode-1) % 3))
                                val = self._stress_tensor[j]
                                str_in = list(f'{val:g}')
                                break
                        else:
                            selected = 0

                    elif action == 'ScrollUp':
                        for n,i in enumerate(idx):
                            if i[0] == y and i[1] <= x <= i[2]:
                                j = (int(n // 3), int(n % 3))
                                self._stress_tensor[j] += 0.25
                                if j[0] != j[1]:
                                    self._stress_tensor[j[1], j[0]] += 0.25
                                break

                    elif action == 'ScrollDown':
                        for n,i in enumerate(idx):
                            if i[0] == y and i[1] <= x <= i[2]:
                                j = (int(n // 3), int(n % 3))
                                self._stress_tensor[j] -= 0.25
                                if j[0] != j[1]:
                                    self._stress_tensor[j[1], j[0]] -= 0.25
                                break

                    elif action == 'MouseUp':
                        selected = 0

                    btn_idx += 1

                if mode == 0:
                    user_io = ''
                else:
                    prefix = str(String(
                        labels[mode-1], foreground = 'white',
                        background = 'black', style = 'bold'
                    ))
                    user_io = f'\n\n\r{prefix} := {"".join(str_in)}'

                idx, labels, rows = self._get_buttons(selected = selected)
                mat = self._get_st_rows()

                for n,(i,j) in enumerate(zip(rows, mat)):
                    rows[n] = f"{i}{j}"

                msg = '\n\r'.join(rows)

                text_str = (
                    f'\033[2J\033[3J\033[f{disp_str}\n\n\r{msg}{user_io}'
                )
                print(text_str, end = '', flush = True)

            time.sleep(self._dt)

        print('\033[?25h', end = '', flush = True)
        print('\033[1 q', end = '', flush = True)
