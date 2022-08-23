import numpy as np
import googlemaps


class Location:

    def __init__(self, x, y, center_coords=(0, 0)):
        self.x = x
        self.y = y
        self.center_coords = center_coords
        self.dist_to_locations = {}
        self.dist_to_center = self.distance_to_center()

    def get_center_coords(self):
        return self.center_coords[0], self.center_coords[1]

    def get_coords(self):
        return self.x, self.y

    def distance_to_center(self):
        x, y = self.get_center_coords()
        return self.manhattan_distance(x, y)

    def distance_to_center_through(self, loc):
        dist = self.distance_to(loc)
        dist += loc.distance_to_center()
        return dist

    def distance_to(self, loc):
        coords = loc.get_coords()
        dist = self.dist_to_locations.get(coords)
        if dist is not None:
            return dist
        dist = self.manhattan_distance(loc.x, loc.y)
        self.dist_to_locations[coords] = dist
        return dist

    def google_distance(self, origin, destinations):
        # origin = tuple; example (36.3648284, 43.2003099)
        # destinations = list of tuples; example [(36.4101953, 43.1859467), (36.3631696, 43.1848604)]
        gmaps = googlemaps.Client(key='AIzaSyD1gxbKg2bwRVCo_7Z-SLnmea8CGcoQCKk')
        result = gmaps.distance_matrix(origin, destinations)['rows'][0]['elements']
        distances = [item['distance']['value']/1000 for item in result]
        return distances

    def manhattan_distance(self, x, y):
        dx = np.abs(self.x - x)
        dy = np.abs(self.y - y)
        distance = 100 * (dx + dy)
        return distance

    def __str__(self):
        return f"Location:<{self.x},{self.y}>"

    def __repr__(self):
        return self.__str__()
