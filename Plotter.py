import matplotlib.pyplot as plt


class Plotter:
    def plot(self, points):
        x = []
        y = []
        for point in points:
            x.append(point[0])
            y.append(point[1])
        plt.axis([max(x), min(x), max(y), min(y)])
        plt.plot(x, y)
        plt.show()
