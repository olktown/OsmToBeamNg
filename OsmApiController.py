from OSMPythonTools.overpass import Overpass
import math


# PARAMETERS:
#   root: gps point
#   node: gps point
#
# DESCRIPTION:
#   this function calculates a gps point to a point
#   in a coordination system with the root node as virtual zero
#
# RETURN:
#   [x, y]
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

    # ------------------------------- public methods ------------------------------- #
    # PARAMETERS:
    #   street_name_dict: dictionary
    #       key: city name
    #       value: list of street names in this city
    #   timeout: int
    #       timeout for the osm api
    #
    # DESCRIPTION:
    #   this method returns a list of lists for each street with points
    #   normalized into a coordination system with one of the points as
    #   virtual zero
    #
    # RETURN:
    #   list[list[list]]>
    def load_streets_by_name(self, street_name_dict, timeout=50):
        self._root = None
        nodes = []
        for area in street_name_dict:
            streets = street_name_dict[area]
            for street in streets:
                self._load_streets_in_area_with_name(area, street, timeout)
                if self._root is None:
                    self._root = self._streets[0].geometry()['coordinates'][0]
                nodes.append(self._get_normalized_coordinates())
        return nodes

    # PARAMETERS:
    #   street_name_dict: dictionary
    #       key: city name
    #       value: list of street names in this city
    #   timeout: int
    #       timeout for the osm api
    #
    # DESCRIPTION:
    #   this method returns a dictionary with the type of a street as key and a list of streets
    #   as value
    #   key: type of street
    #   value: list of streets of this type, this lists contain lists with the coordination points
    #
    # RETURN:
    #   dictionary<string, list[list[list]]>
    def load_streets_by_name_categorized(self, street_name_dict, timeout=50):
        self._root = None
        nodes = []
        for area in street_name_dict:
            streets = street_name_dict[area]
            for street in streets:
                self._load_streets_in_area_with_name(area, street, timeout)
                if self._root is None:
                    self._root = self._streets[0].geometry()['coordinates'][0]
                nodes.append(self._get_normalized_coordinates_with_category())
        return nodes

    # PARAMETERS:
    #   area_name: string
    #       name of a city, where you want to download the street points
    #   timeout: int
    #       timeout for the osm api
    #
    # DESCRIPTION:
    #   this method returns a list of lists for each street with points
    #   normalized into a coordination system with one of the points as
    #   virtual zero
    #
    # RETURN:
    #   list[list[list]]>
    def load_streets_in_area_to_nodes(self, area_name, timeout=50):
        self._root = None
        a = self._load_streets_in_area(area_name)
        self._streets = self._load_streets_in_area(area_name, timeout)
        self._root = self._streets[0].geometry()['coordinates'][0]
        return self._get_normalized_coordinates()

    # PARAMETERS:
    #   area_name: string
    #       name of a city, where you want to download the street points
    #   timeout: int
    #       timeout for the osm api
    #
    # DESCRIPTION:
    #   this method returns a dictionary with the type of a street as key and a list of streets
    #   as value
    #   key: type of street
    #   value: list of streets of this type, this lists contain lists with the coordination points
    #
    # RETURN:
    #   dictionary<string, list[list[list]]>
    def load_streets_in_area_to_categorized_nodes(self, area_name, timeout=50):
        self._root = None
        self._streets = self._load_streets_in_area(area_name, timeout)
        self._root = self._streets[0].geometry()['coordinates'][0]
        return self._get_normalized_coordinates_with_category()

    # ------------------------------- private methods ------------------------------- #

    # PARAMETERS:
    #   area_name: string
    #       name of a city, where you want to download the street points
    #   street_name: string
    #       name of a street in the given city
    #   timeout: int
    #       timeout for the osm api
    #
    # DESCRIPTION:
    #   this method returns the elements of the result of the osm query
    #
    # RETURN:
    #   object, osm result elements
    def _load_streets_in_area_with_name(self, area_name, street_name, timeout=50):
        query = 'area[name="' + area_name + '"]; way[name="' + street_name + '"](area);out geom;'
        self._streets = self._overpass.query(query, timeout).elements()

    # PARAMETERS:
    #   area_name: string
    #       name of a city, where you want to download the street points
    #   timeout: int
    #       timeout for the osm api
    #
    # DESCRIPTION:
    #   this method returns the elements of the result of the osm query
    #
    # RETURN:
    #   object, osm result elements
    def _load_streets_in_area(self, area_name, timeout=50):
        query = 'area[name="' + area_name + '"]; way(area); out geom;'
        return self._overpass.query(query, timeout).elements()

    # DESCRIPTION:
    #   this method takes every single gps point of the loaded streets in self._streets and
    #   transforms it into a virtual coordination system with the self._root as virtual zero
    #
    # RETURN:
    #   list[list[list]]>
    def _get_normalized_coordinates(self):
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

    # DESCRIPTION:
    #   this method takes every single gps point of the loaded streets in self._streets and
    #   transforms it into a virtual coordination system with the self._root as virtual zero
    #   the streets are categorized by its types
    #
    # RETURN:
    #   dictionary<string, list[list[list]]>
    def _get_normalized_coordinates_with_category(self):
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





































