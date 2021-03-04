from OsmApiController import OsmApiController

def test_load_streets_by_name():
    api = OsmApiController()
    nodes = api.load_streets_by_name({"Sankt Englmar": ["Galgenberg"]})
    assert len(nodes[0][0]) == 9

def test_load_multiple_streets_load_streets_by_name():
    api = OsmApiController()
    nodes = api.load_streets_by_name({"Sankt Englmar": ["Galgenberg", "Pfarrhofweg", "Kirchplatz"]})
    # result is a list of 3 entries one for each street
    # each list does have multiple list for the case a street is not only straight
    # for example a crossroad would cause to have a list with more lists as entry
    # the inner list does have the coordinates in itf
    assert len(nodes) == 3
    assert len(nodes[0][0]) == 9
    assert len(nodes[1]) == 2
    assert len(nodes[1][0]) == 8
    assert len(nodes[1][1]) == 4
    assert len(nodes[2]) == 3
    assert len(nodes[2][0]) == 3
    assert len(nodes[2][1]) == 3
    assert len(nodes[2][2]) == 2

def test_load_streets_by_name_categorized():
    api = OsmApiController()
    nodes = api.load_streets_by_name_categorized({"Sankt Englmar": ["Galgenberg", "Pfarrhofweg", "Kirchplatz"]})
    # result is a list of 3 entries one for each street
    # the entries in the list are dictionaries in which the keys are the type of the street
    # in this example the types are 'residential' and 'service'
    # the values in the dictionary is a list with a list for each street of this type
    assert len(nodes) == 3
    assert len(nodes[0]) == 1
    assert len(nodes[1]) == 1
    assert len(nodes[2]) == 2
    assert 'residential' in nodes[0]
    assert 'residential' in nodes[1]
    assert 'residential' in nodes[2]
    assert 'service' in nodes[2]


def test_load_streets_in_area_to_nodes():
    api = OsmApiController()
    nodes = api.load_streets_in_area_to_nodes("Sankt Englmar")
    # this method returns all streets of the given city
    # the result of this method is a list with a list as entry for each street of this city
    # the street lists contain directly the coordinate points
    assert len(nodes) == 2802


def test_load_streets_in_area_to_categorized_nodes():
    api = OsmApiController()
    nodes = api.load_streets_in_area_to_categorized_nodes("Sankt Englmar")
    assert 'residential' in nodes
    assert 'path' in nodes
    assert 'service' in nodes
    assert 'unclassified' in nodes
    assert 'secondary' in nodes
    assert 'tertiary' in nodes
    assert 'track' in nodes
    assert 'footway' in nodes
    assert 'steps' in nodes
    assert 'platform' in nodes
    assert 'cycleway' in nodes

