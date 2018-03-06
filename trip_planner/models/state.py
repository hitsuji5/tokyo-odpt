from place import MODE_WALK, MODE_BUS, CATEGORY_STOP, CATEGORY_SPOT, CATEGORY_SHOP, CATEGORY_FOOD
import numpy as np
import copy


def sigmoid(x, x0, a=1.0):
    return 1.0 / (1.0 + np.exp(-a * (x - x0)))

class State(object):
    LUNCH_TIME = [12.5 * 3600, 13.5 * 3600]
    DINNER_TIME = [19.5 * 3600, 20.5 * 3600]


    def __init__(self, place, time, prev_mode=None):
        self.place = place
        self.time = time
        self.prev_mode = prev_mode
        self.total_poi_score = 0
        self.total_bus_score = 0
        self.total_walking_cost = 0
        self.visited_pois = []
        self.had_food = False

    def copy(self):
        state = copy.copy(self)
        state.visited_pois = self.visited_pois[:]
        return state

    def step(self, action):
        place = action.target
        if place.IS_POI:
            self.visited_pois.append(place.id)
        self.place = place
        self.time += action.duration + place.DURATION
        self.prev_mode = action.mode
        self.total_poi_score += self.get_place_score(place)

        if place.CATEGORY == CATEGORY_FOOD:
            self.had_food = True
            self.total_poi_score += 10.0

        minutes = action.duration / 60.0
        mode = action.mode
        if mode == MODE_WALK:
            self.total_walking_cost += self.get_walking_cost(minutes)
        elif mode == MODE_BUS:
            self.total_bus_score += self.get_bus_score(minutes)

    def get_place_score(self, place):
        if place.IS_POI:
            return place.score + 1.0
        return 0.0

    def get_bus_score(self, minutes):
        score = 5.0 * (sigmoid(minutes, 10, 0.5) - sigmoid(minutes, 30, 0.5)) # bonus for 10~30 minutes trip
        return score

    def get_walking_cost(self, minutes):
        cost = minutes * 0.5
        return cost

    def has_mode(self, mode):
        return mode in self.place.AVAILABLE_MODES

    def is_hungry(self):
        if not self.had_food and State.LUNCH_TIME[0] <= self.time and self.time < State.LUNCH_TIME[1]:
            return True
        if not self.had_food and State.DINNER_TIME[0] <= self.time and self.time < State.DINNER_TIME[1]:
            return True
        return False
