# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

# Press the green button in the gutter to run the script.
from OsmApiController import OsmApiController
import BeamPyApiController

if __name__ == '__main__':
    api = OsmApiController()
    areaNodes = api.load_streets_in_area_to_nodes('Sankt Englmar')
    #areaNodesCategory = api.load_streets_in_area_to_categorized_nodes('Sankt Englmar')
    #streetNameNodes = api.load_streets_by_name({'Sankt Englmar': ['Galgenberg', 'Bayerweg'], 'Straubing': ['Dornierstraße']})
    #streetNameNodesWithCategory = api.load_streets_by_name_categorized({'Sankt Englmar': ['Galgenberg', 'Bayerweg'], 'Straubing': ['Dornierstraße']})
    BeamPyApiController.createScenario(areaNodes, "smallgrid")