import geoutils
import numpy as np

class BusNetwork(object):
    def __init__(self, bus_stops, bus_routes):
        self.bus_stops = bus_stops
        # bus_stops_ids = [x['owl:sameAs'] for x in bus_stops]
        # self.bus_stops_id2idx = {id_ : i for i, id_ in enumerate(bus_stops_ids)}
        self.bus_stops_location = np.array([[bs['geo:lat'], bs['geo:long']] for bs in bus_stops])

        self.bus_routes = bus_routes
        # bus_routes_ids = [x['owl:sameAs'] for x in bus_routes]
        self.route_table = self.create_route_table(bus_stops, bus_routes)
        bus_routes_id2idx = {x['owl:sameAs'] : i for i, x in enumerate(bus_routes)}
        self.bus_stops_route_idx = [[bus_routes_id2idx[route_id] for route_id in bs['odpt:busroutePattern']]
                                   for bs in bus_stops]

    def get_available_bus_routes(self, bus_stop_idx):
        return self.bus_stops_route_idx[bus_stop_idx]

    def create_route_table(self, bus_stops, bus_routes):
        rt = []
        bus_stops_id2idx = {x['owl:sameAs']: i for i, x in enumerate(bus_stops)}
        for route_id, route in enumerate(bus_routes):
            bus_stop_ids = []
            polyline = []
            for p in route['odpt:busstopPoleOrder']:
                bus_stop_name = p['odpt:busstopPole']
                bus_stop_id = bus_stops_id2idx[bus_stop_name]
                bus_stop_ids.append(bus_stop_id)
                lat, lon = self.bus_stops_location[bus_stop_id]
                polyline.append((lat, lon))
            lats, lons = zip(*polyline)
            r = {}
            r["bus_stop_id"] = bus_stop_ids
            r["bus_stop_order"] = {bs_id : i for i, bs_id in enumerate(bus_stop_ids)}
            d = geoutils.distance_in_meters(lats[:-1], lons[:-1], lats[1:], lons[1:])
            r["eta"] = geoutils.estimate_bus_trip_time(d)
            rt.append(r)
        return rt

    def find_nearby_bus_stops(self, p, r=500):
        lat, lon = p
        d = geoutils.distance_in_meters(lat, lon, self.bus_stops_location[:, 0], self.bus_stops_location[:, 1])
        return [(i, geoutils.estimate_walking_time(d[i]), None) for i in np.where(d < r)[0]]


    def find_bus_stops_on_routes(self, src_bus_stop_id, wait_time=300, min_eta=640, max_eta=1800):
        # src_bus_stop = self.bus_stops[src_bus_stop_id]
        tgt_bus_stops = []
        # for route_id in src_bus_stop['odpt:busroutePattern']:
        for route_idx in self.get_available_bus_routes(src_bus_stop_id):
            bus_stop_order = self.route_table[route_idx]["bus_stop_order"][src_bus_stop_id]
            eta = wait_time
            for i, tgt in enumerate(self.route_table[route_idx]["bus_stop_id"][bus_stop_order + 1:]):
                eta += self.route_table[route_idx]["eta"][bus_stop_order + i]
                if eta < min_eta:
                    continue
                if eta > max_eta:
                    break
                # if route_id not in tgt_bus_stop_ids:
                #     tgt_bus_stop_ids[route_id] = []
                tgt_bus_stops.append((tgt, eta, route_idx))
        return tgt_bus_stops


