import numpy as np
import matplotlib.pyplot as plt
from beamngpy import BeamNGpy, Vehicle, Scenario, Road
from beamngpy.sensors import Camera


def createScenario(streetPoints, levelName):
    _streetPoints = []

    for street in streetPoints:
        _streetPoints.append([])
        for point in street:
            _streetPoints[-1].append(point)

    beamCtrl = BeamNgController(levelName)
    for street in _streetPoints:
        beamCtrl.add_road(street)
    beamCtrl.start_game()


def plot_road(bng, ax):
    for road in bng.get_roads():
        road_geometry = bng.get_road_edges(road)
        left_edge_x = np.array([e['left'][0] for e in road_geometry])
        left_edge_y = np.array([e['left'][1] for e in road_geometry])
        right_edge_x = np.array([e['right'][0] for e in road_geometry])
        right_edge_y = np.array([e['right'][1] for e in road_geometry])
        x_min = min(left_edge_x.min(),
                    right_edge_x.min()) - 10  # We add/subtract 10 from the min/max coordinates to pad
        x_max = max(left_edge_x.max(), right_edge_x.max()) + 10  # the area of the plot a bit
        y_min = min(left_edge_y.min(), right_edge_y.min()) - 10
        y_max = max(left_edge_y.max(), right_edge_y.max()) + 10
        ax.set_aspect('equal', 'datalim')
        ax.set_xlim(left=0, right=256)
        ax.set_ylim(bottom=0, top=256)
        ax.plot(left_edge_x, left_edge_y, 'b-')
        ax.plot(right_edge_x, right_edge_y, 'b-')


class BeamNgController:
    def __init__(self, level):
        self._beamng = BeamNGpy('localhost', 64256, home='C:/Users/wio1sab/Desktop/BeamNG.research.v1.7.0.0')
        self._scenario = Scenario(level, '')
        self._root_node = 0

    def add_road(self, nodes):
        self._root_node = nodes[-1]
        road = Road('track_editor_C_center', texture_length=5, interpolate=False, options={'over_objects': True, 'smoothness': 1, 'drivability': 10})
        for node in nodes:
            road.nodes.append((*node, 7))
        self._scenario.add_road(road)

    def create_ego_car(self):
        vehicle = Vehicle('ego_vehicle', model='etk800', licence='PYTHON')
        overhead = Camera((0, -10, 5), (0, 1, -0.75), 60, (1024, 1024))
        vehicle.attach_sensor('overhead', overhead)
        node = (self._root_node[0], self._root_node[1], 0)
        self._scenario.add_vehicle(vehicle, pos=node, rot=(0, 0, 0))

    def start_game(self):
        self.create_ego_car()
        self._scenario.make(self._beamng)
        bng = self._beamng.open()
        bng.load_scenario(self._scenario)
        bng.start_scenario()

        plt.figure(figsize=(10, 10))
        plot_road(bng, plt.gca())
        plt.show()