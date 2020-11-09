class SmartMenu(LiveMenu):
    '''
        A smarter frontend variant of `LiveMenu` which automates many of the
        processes involved in creating a `LiveMenu` for simple usage.
    '''

    def __init__(self, rows:int = None, cols:int = None):
        '''
            Returns an instance of `SmartMenu`.
        '''
        super().__init__(rows = rows, cols = cols)

    def new_button(self, x0:int, y0:int, x1:int, y1:int):
