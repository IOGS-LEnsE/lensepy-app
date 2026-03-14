class PointCIE:
    """Class to manage x,y CIE point."""
    def __init__(self, x:float=0, y:float=0, name:str=''):
        self.pos_x = x
        self.pos_y = y
        self.name = name

    def get_coords(self):
        """Returns the coordinates of the point."""
        return [self.pos_x, self.pos_y]

    def get_name(self):
        """Returns the name of the point."""
        return self.name

