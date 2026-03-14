
class TriangleGammut:
    """Class to manage a triangle for x,y CIE coordinates."""

    def __init__(self, name:str=''):
        self.points = []
        self.name = name

    def add_point(self, point):
        """Add a point to the triangle."""
        if len(self.points) < 3:
            self.points.append(point)

    def set_name(self, name:str):
        """Set the name of the triangle."""
        self.name = name

    def is_complete(self):
        """Return if the triangle has 3 points."""
        return len(self.points) == 3

    def get_points(self):
        """Return the list of points [(x1,y1),(x2,y2),...]."""
        p_list = []
        for point in self.points:
            p_list.append((point.pos_x, point.pos_y))
        return p_list


if __name__ == "__main__":
    from lensepy_app.modules.optics.cie1931.cie1931_model import PointCIE
    triangle = TriangleGammut()

    print(f'Is OK ? {triangle.is_complete()}')
    p1 = PointCIE(0.2, 0.4, 'A')
    triangle.add_point(p1)
    p2 = PointCIE(0.4, 0.6, 'B')
    triangle.add_point(p2)
    p3 = PointCIE(0.1, 0.1, 'C')
    triangle.add_point(p3)
    print(f'Is OK ? {triangle.is_complete()}')