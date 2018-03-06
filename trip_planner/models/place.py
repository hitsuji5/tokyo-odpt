MODE_WALK = 0
MODE_BUS = 1

CATEGORY_FOOD = 0
CATEGORY_SHOP = 1
CATEGORY_SPOT = 2
CATEGORY_STOP = 3
CATEGORY_OTHER = 4

def create_place(id, location, type, score, data):
    if type == CATEGORY_FOOD:
        cls = BusStop
    elif type == CATEGORY_SHOP:
        cls = Shop
    elif type == CATEGORY_SPOT:
        cls = Spot
    elif type == CATEGORY_STOP:
        cls = BusStop
    else:
        raise NotImplementedError
    return cls(id, location, score, data)


class Place(object):
    IS_POI = True
    AVAILABLE_MODES = [MODE_WALK]
    DURATION = 30.0 * 60
    CATEGORY = CATEGORY_OTHER
    CATEGORIES = [
        'food',
        'shop',
        'spot',
        'bus_stop',
        'others'
    ]

    def __init__(self, id, location, score=0, data=None):
        self.id = id
        self.location = location
        self.score = score
        self.data = data

    def get_category(self):
        return self.CATEGORIES[self.CATEGORY]

class BusStop(Place):
    IS_POI = False
    AVAILABLE_MODES = [MODE_WALK, MODE_BUS]
    DURATION = 5.0 * 60
    CATEGORY = CATEGORY_STOP


class Food(Place):
    CATEGORY = CATEGORY_FOOD

class Shop(Place):
    CATEGORY = CATEGORY_SHOP

class Spot(Place):
    CATEGORY = CATEGORY_SPOT
