from string import digits
import time

from numba import njit
import numpy as np

from termutils.obj.LiveMenu import LiveMenu
from termutils.obj.String import String
from termutils.obj.Color import Color

class SpringToy(LiveMenu):

    def __init__(
    self, mass:float = 1.0, size:float = 1E-2, g:float = 9.81, k:float = 100,
    radius:int = 1, fps:float = 60, dt:float = 1E-4, zeta:float = 0.01,
    block_color:str = 'platinum', background_color = 'navy blue'):
        '''
            Creates a new instance of class `SpringToy`.

            `mass` is the mass of the block in [kg].
            `size` is the distance represented by char height.
            `g` is the gravitational acceleration in [m/s²].
            `k` is the spring force in [N/m].
            `zeta` is the damping ratio.
            `radius` is the radius of the displayed block in pixels.
            `fps` is the printing rate.
            `dt` is the simulation rate.
        '''
        self._m = mass
        self._size = size
        self._g = g
        self._k = k
        self._radius = radius
        self._fps = fps
        self._dt = dt
        self._zeta = zeta
        self._c = 2*self._zeta*np.sqrt(self._m*self._k)
        self._block_color = Color.palette(block_color)
        self._background_color = Color.palette(background_color)
        super().__init__(escape_hits = 1)

        # Caching the integrator
        self._integrate(np.zeros(2),np.zeros(2),np.zeros(2),1,1,1,1,1,1)

    @staticmethod
    # @njit(cache = True)
    def _integrate(
    x0:np.ndarray, x1:np.ndarray, v0:np.ndarray, k:float, g:float, c:float,
    m:float, dt:float, T:float):
        '''
            Performs the integration required to move the block.
        '''
        x = x1.copy()
        v = v0.copy()
        for i in range(int(T//dt)):
            a = (-k*(x - x0) -c*v)/m
            a[0] += g
            v = v + a*dt
            x = x + v*dt
        return np.round(x), v

    def _block_str(self, block, mid_idx):
        '''
            Returns a string where the block is in the given position.
        '''
        range_0 = range(self._dims[0]-1)
        range_1 = range(self._dims[1]-1)

        canvas = [[' ' for j in range_1] for i in range_0]
        canvas[int(mid_idx[0])][int(mid_idx[1])] = '╋'
        for idx in block:
            if 0 < idx[0] < self._dims[0] - 1 and 0 < idx[1] < self._dims[1] - 1:
                canvas[idx[0]][idx[1]] = '█'
        canvas = '\n\r'.join((''.join(row) for row in canvas))
        return String(canvas, self._block_color, self._background_color)

    def __call__(self):
        '''
            Displays the current state of the block.
        '''
        print('\033[?25l', end = '', flush = True)

        active = True
        dragging = False
        key_idx = 0
        btn_idx = 0
        sleep_time = 1/self._fps
        t0 = None
        locked = False

        # Coordinate System
        y_mid = self._dims[0] // 2
        x_mid = self._dims[1] // 2

        # Physical Variables
        mid_idx = np.array([y_mid, x_mid], dtype = np.float64)
        pos = mid_idx.copy()
        vel = np.zeros(2, dtype = np.float64)

        # Formatting
        y_px = self._radius
        x_px = 2*self._radius
        y_idx = np.arange(y_mid - y_px, y_mid + y_px, 1, dtype = np.int64)
        x_idx = np.arange(x_mid - x_px, x_mid + x_px, 1, dtype = np.int64)
        y_idx, x_idx = np.meshgrid(y_idx, x_idx)
        block = np.concatenate([y_idx[:,:,None], x_idx[:,:,None]], axis = 2)
        block = block.reshape((block.shape[0]*block.shape[1], block.shape[2]))

        while active:

            if key_idx <= len(self._key_history) - 1 or \
               btn_idx <= len(self._btn_history) - 1:

                while btn_idx <= len(self._btn_history) - 1:

                    action = self._btn_history[btn_idx]['action']
                    y = self._btn_history[btn_idx]['y']
                    x = self._btn_history[btn_idx]['x']

                    if locked:
                        pass

                    elif action == 'LeftClick' and [y,x] in block.tolist():
                        dragging = True
                        pos = np.array([y,x])
                        t0 = time.perf_counter()

                    elif action == 'LeftDrag' and dragging:
                        block[:,0] += y - pos[0]
                        block[:,1] += x - pos[1]
                        t1 = time.perf_counter()
                        vel[0] = self._size*(y - pos[0])/(t1-t0)
                        vel[1] = self._size*(x - pos[1])/(t1-t0)
                        pos[0] = y
                        pos[1] = x
                        t0 = t1

                    elif action == 'MouseUp' and dragging:
                        dragging = False
                        if time.perf_counter() - t0 > 0.5:
                            vel[0] = 0
                            vel[1] = 0
                        t0 = None

                    elif action == 'RightClick':
                        pos = mid_idx.copy()
                        dragging = False
                        vel[0] = 0
                        vel[1] = 0

                    btn_idx += 1

            while key_idx <= len(self._key_history) - 1:
                key = self._key_history[key_idx]
                if key == 'Kill':
                    self._kill = True
                    active = False
                    break
                elif key == 'Space':
                    locked = not locked
                elif locked:
                    pass
                elif key == 'Up':
                    mid_idx[0] -= 1
                elif key == 'Down':
                    mid_idx[0] += 1
                elif key == 'Left':
                    mid_idx[1] -= 2
                elif key == 'Right':
                    mid_idx[1] += 2

                key_idx += 1


            if not dragging and not locked:
                new_pos, vel = self._integrate(
                    mid_idx, pos, vel, self._k, self._g, self._c, self._m,
                    self._dt, sleep_time
                )
                block[:,0] = block[:,0] + new_pos[0] - pos[0]
                block[:,1] = block[:,1] + new_pos[1] - pos[1]
                pos = new_pos

            text_str = (
                f'\033[2J\033[3J\033[f\r{str(self._block_str(block, mid_idx))}'
            )
            print(text_str, end = '', flush = True)

            time.sleep(sleep_time)

        print('\033[?25h', end = '', flush = True)
        print('\033[1 q', end = '', flush = True)
