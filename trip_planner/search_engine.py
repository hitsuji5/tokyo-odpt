from bus_network import BusNetwork
from poi_map import POIMap
import numpy as np
import pandas as pd
from models.place import create_place, BusStop, MODE_BUS, MODE_WALK
from models.action import Action
import json

BUS_STOP_JSON_PATH = "../data/bus_stops.json"
BUS_ROUTE_JSON_PATH = "../data/bus_routes.json"
POI_CSV_PATH = "../data/odpt-POI.csv"

class SearchEngine(object):

    def __init__(self):
        bus_routes = json.load(open(BUS_ROUTE_JSON_PATH, 'r'))
        bus_stops = json.load(open(BUS_STOP_JSON_PATH, 'r'))
        self.bus_network = BusNetwork(bus_stops, bus_routes)
        poi_df = pd.read_csv(POI_CSV_PATH)
        self.poi_map = POIMap(poi_df.to_dict('records'))

    def create_bus_stop(self, idx):
        return BusStop(idx, self.bus_network.bus_stops_location[idx],
                       score=0, data=self.bus_network.bus_stops[idx])

    # def get_bus_stop_name(self, bus_stop_id):
    #     return self.bus_network.bus_stops_name[bus_stop_id]

    def create_poi(self, idx):
        return create_place(idx, self.poi_map.pois_location[idx], self.poi_map.pois_type[idx],
                            self.poi_map.pois_base_score[idx], self.poi_map.pois[idx])

    # def get_poi_name(self, place_id):
    #     return self.poi_map.pois_name[place_id]

    def get_action(self, state):
        stops, pois = self.search_reachable_places(state)
        if len(stops) == 0 and len(pois) == 0:
            return None

        action = self.explore(state, stops, pois)
        return action

    def explore(self, state, stops, pois):
        if np.random.randint(0, len(stops) + len(pois)) < len(stops):
            p = None
            idx = np.random.choice(np.arange(len(stops)), p=p)
            place_idx, eta, route_idx = stops.pop(idx)
            target = self.create_bus_stop(place_idx)
        else:
            p = self.poi_map.get_scores([place_id for place_id, _, _ in pois])
            idx = np.random.choice(np.arange(len(pois)), p=p)
            place_idx, eta, route_idx = pois.pop(idx)
            target = self.create_poi(place_idx)

        if route_idx is None:
            mode = MODE_WALK
            route = None
        else:
            mode = MODE_BUS
            route = self.bus_network.bus_routes[route_idx]

        action = Action(state.time, state.place, target, mode, eta, route)
        return action

    def search_reachable_places(self, state):
        source = state.place
        if state.is_hungry():
            stops = []
            pois = self.poi_map.find_nearby_foods(source.location)

        elif state.prev_mode == MODE_WALK and state.has_mode(MODE_BUS):
            stops = self.bus_network.find_bus_stops_on_routes(source.id)
            pois = []

        else:
            if state.prev_mode == MODE_BUS:
                stops = []
            else:
                stops = self.bus_network.find_nearby_bus_stops(source.location)
            shops = self.poi_map.find_nearby_shops(source.location)
            spots = self.poi_map.find_nearby_spots(source.location)
            pois = shops + spots
            pois = [x for x in pois if x[0] not in state.visited_pois]

        return stops, pois


search_engine = SearchEngine()