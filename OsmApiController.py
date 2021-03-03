from OSMPythonTools.overpass import Overpass
from GpsPoint import GpsPoint
import math


def _calculate_coordinates_to_meter(root, node):  #https://www.kompf.de/gps/distcalc.html
    if type(node[0]) is list:
        print(node)
    lat = (root[1] + node[1]) / 2 * 0.01745
    dx = 111.3 * math.cos(lat) * (root[0] - node[0])
    dy = 111.3 * (root[1] - node[1])
    return [dx * 1000, dy * 1000]


class OsmApiController:
    _possible_street_types = ['motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential']
    _streets = None
    _root = None

    def __init__(self):
        self._overpass = Overpass()

    def _generate_query_for_streets(self, area, max_speed):
        query = 'area[name="' + area + '"];('
        for type in self._possible_street_types:
            query += 'way[highway=' + type + ']'
            if type != 'motorway':
                query += '[maxspeed=' + str(max_speed) + '](area);'
            else:
                query += '(area);'
        query += ');out geom;'
        return query

    def load_streets_in_place_with_max_speed(self, place, max_speed):
        query = 'area[name="' + place + '"]; way[maxspeed="' + str(max_speed) + '"](area);out geom;'
        result = self._overpass.query(query)
        self._streets = result.elements()

    def load_streets_in_place_with_name(self, place, name):
        query = 'area[name="' + place + '"]; way[name="' + name + '"](area);out geom;'
        result = self._overpass.query(query)
        self._streets = result.elements()

    def load_streets_by_name(self, street_name_dict):
        self._root = None
        nodes = []
        for area in street_name_dict:
            streets = street_name_dict[area]
            for street in streets:
                self.load_streets_in_place_with_name(area, street)
                if self._root is None:
                    self._root = self._streets[0].geometry()['coordinates'][0]
                nodes.append(self.get_normalized_coordinates())
        return nodes

    def load_streets_by_name_categorized(self, street_name_dict):
        self._root = None
        nodes = []
        for area in street_name_dict:
            streets = street_name_dict[area]
            for street in streets:
                self.load_streets_in_place_with_name(area, street)
                if self._root is None:
                    self._root = self._streets[0].geometry()['coordinates'][0]
                nodes.append(self.get_normalized_coordinates_with_category())
        return nodes

    def _load_streets_in_area(self, areaName):
        query = 'area[name="' + areaName + '"]; way(area); out geom;'
        return self._overpass.query(query, timeout=150).elements()

    def load_streets_in_area_to_nodes(self, areaName):
        self._root = None
        a = self._load_streets_in_area(areaName)
        self._streets = self._load_streets_in_area(areaName)
        self._root = self._streets[0].geometry()['coordinates'][0]
        return self.get_normalized_coordinates()

    def load_streets_in_area_to_categorized_nodes(self, areaName):
        self._root = None
        self._streets = self._load_streets_in_area(areaName)
        self._root = self._streets[0].geometry()['coordinates'][0]
        return self.get_normalized_coordinates_with_category()

    def get_normalized_coordinates_with_category(self):
        nodes = {}
        for street in self._streets:
            new_nodes = []
            if 'tags' in street._json:
                if 'highway' in street._json['tags']:
                    street_type = street._json['tags']['highway']
                else:
                    street_type = 'unclassified'
            else:
                street_type = 'unclassified'

            if type not in nodes:
                nodes[street_type] = []
            for node in street.geometry()['coordinates']:
                if type(node[0]) is float:
                    new_node = _calculate_coordinates_to_meter(self._root, node)
                    new_nodes.append((new_node[0], new_node[1], 0))
                if type(node[0]) is list:
                    for n in node:
                        new_node = _calculate_coordinates_to_meter(self._root, n)
                        new_nodes.append((new_node[0], new_node[1], 0))
            nodes[street_type].append(new_nodes)
        return nodes

    def get_normalized_coordinates(self):
        nodes = []
        for street in self._streets:
            new_nodes = []
            for node in street.geometry()['coordinates']:
                if type(node[0]) is float:
                    new_node = _calculate_coordinates_to_meter(self._root, node)
                    new_nodes.append((new_node[0], new_node[1], 0))
                if type(node[0]) is list:
                    for n in node:
                        new_node = _calculate_coordinates_to_meter(self._root, n)
                        new_nodes.append((new_node[0], new_node[1], 0))
            nodes.append(new_nodes)
        return nodes

    def getStreetGpsPoints(self):
        gpsPoints = []
        for street in self._streets:
            for point in street.geometry()['coordinates']:
                newPoint = GpsPoint(point[1], point[0])
                gpsPoints.append(newPoint)
        return gpsPoints

    def generatePointsBetween(self, start, end):
        bearing = start.bearing_between_point(end)
        distance = int(start.distance_to_point(end))
        points = []
        for i in range(distance):
            points.append(start.point_with_distance(i, bearing))
        return points

    def generateLineForStreetGpsPoints(self):
        gpsPoints = []
        for street in self._streets:
            i = 0
            coordinates = street.geometry()['coordinates']
            while i < len(coordinates)-1:
                point_start = GpsPoint(coordinates[i][1], coordinates[i][0])
                point_end = GpsPoint(coordinates[i + 1][1], coordinates[i + 1][0])
                points = self.generatePointsBetween(point_start, point_end)
                gpsPoints.append(point_start)
                gpsPoints.extend(points)
                gpsPoints.append(point_end)
                i += 1
        return gpsPoints

    def getBoundingRectOfStreets(self):
        minLat = None
        minLong = None
        maxLat = None
        maxLong = None

        for street in self._streets:
            bounds = street._json['bounds']
            if minLat is None or minLat > bounds['minlat']:
                minLat = bounds['minlat']
            if minLong is None or minLong > bounds['minlon']:
                minLong = bounds['minlon']
            if maxLat is None or maxLat < bounds['maxlat']:
                maxLat = bounds['maxlat']
            if maxLong is None or maxLong < bounds['maxlon']:
                maxLong = bounds['maxlon']

        return {'min' : GpsPoint(minLat, minLong), 'max': GpsPoint(maxLat, maxLong)}





































