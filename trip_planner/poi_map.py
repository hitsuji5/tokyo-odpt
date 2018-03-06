import numpy as np
from models.place import CATEGORY_FOOD, CATEGORY_SHOP, CATEGORY_SPOT
import geoutils

class POIMap(object):

    def __init__(self, pois):
        self.pois = pois
        self.place_ids = [x['place_id'] for x in pois]
        # self.pois_name2id = {name: i for i, name in enumerate(self.pois_name)}
        self.pois_location = np.array([[x['lat'], x['lon']] for x in pois])
        self.pois_base_score = np.array([x['rating'] * np.log( 2.0 + x['review_count']) for x in pois])
        self.pois_base_score[np.isnan(self.pois_base_score)] = 1.0
        self.pois_type = np.zeros(len(pois))
        for i, poi in enumerate(pois):
            if 'food' in poi['types']:
                self.pois_type[i] = CATEGORY_FOOD
            if 'shopping_mall' in poi['types'] or 'department_store' in poi['types']:
                self.pois_type[i] = CATEGORY_SHOP
            else:
                self.pois_type[i] = CATEGORY_SPOT

    def get_scores(self, poi_ids):
        base_score = self.pois_base_score[poi_ids]
        base_score = np.exp(base_score / 10.0)
        p = base_score / base_score.sum()
        return p

    def find_nearby_pois(self, category, p, r):
        lat, lon = p
        poi_ids = np.where(self.pois_type == category)[0]
        locs = self.pois_location[poi_ids, :]
        d = geoutils.distance_in_meters(lat, lon, locs[:, 0], locs[:, 1])
        return [(poi_ids[i], geoutils.estimate_walking_time(d[i]), None) for i in np.where(d < r)[0]]


    def find_nearby_foods(self, p, r=500):
        return self.find_nearby_pois(CATEGORY_FOOD, p, r)

    def find_nearby_shops(self, p, r=500):
        return self.find_nearby_pois(CATEGORY_SHOP, p, r)

    def find_nearby_spots(self, p, r=500):
        return self.find_nearby_pois(CATEGORY_SPOT, p, r)
