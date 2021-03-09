# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
from OsmApiController import OsmApiController
from Plotter import Plotter

if __name__ == '__main__':
    api = OsmApiController()
    plotter = Plotter()
    points = api.load_route_between_streets([["Straubing", "Dornierstraße"], ["Straubing", "Sachsenring"], ["Straubing", "Heerstraße"]])
    plotter.plot(points)