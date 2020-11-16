from string import digits
from typing import Union
import threading
import time

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from termutils.obj.LiveMenu import LiveMenu
from termutils.obj.String import String


class RailGun(LiveMenu):

    def __init__(self, rows:int = None, cols:int = None):

        super().__init__(rows = rows, cols = cols, escape_hits = 1)

        raise NotImplementedError('<class \'RailGun\'> is not yet implemented.')
