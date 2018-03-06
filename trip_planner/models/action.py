from place import Place, MODE_BUS, MODE_WALK


class Action(object):

    def __init__(self, t, src, tgt, mode, duration, route=None):
        assert isinstance(src, Place)
        assert isinstance(tgt, Place)

        self.t = t
        self.source = src
        self.target = tgt
        self.mode = mode
        self.duration = duration
        self.route = route

    def to_dict(self):
        if self.target.IS_POI:
            place_id = self.target.data['place_id']
        else:
            place_id = self.target.data['owl:sameAs']
        place_type = self.target.get_category()
        if self.route is None:
            route_id = None
        else:
            route_id = self.route['owl:sameAs']
        mode = 'bus' if self.mode == MODE_BUS else 'walk'

        return {
            "departure_time" : int(self.t),
            "departure_location": list(self.source.location),
            "arrival_time": int(self.t + self.duration),
            "arrival_location": list(self.target.location),
            "place_id": place_id,
            "place_type": place_type,
            "mode" : mode,
            "route_id": route_id
        }

