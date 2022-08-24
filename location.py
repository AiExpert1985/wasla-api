import numpy as np
import googlemaps


class Location:
    def __init__(self, x, y, center_coords=(0, 0)):
        self.x = x
        self.y = y
        self.center_coords = center_coords
        self.dist_to_locations = {}
        self.dist_to_center = self.distance_to_center()
        self.google_api_key = 'AIzaSyD1gxbKg2bwRVCo_7Z-SLnmea8CGcoQCKk'

    def get_center_coords(self):
        return self.center_coords[0], self.center_coords[1]

    def get_coords(self):
        return self.x, self.y

    def distance_to_center(self):
        x, y = self.get_center_coords()
        return self.distance(x, y)

    def distance_to_center_through(self, loc):
        dist = self.distance_to(loc)
        dist += loc.distance_to_center()
        return dist

    def distance_to(self, loc):
        coords = loc.get_coords()
        dist = self.dist_to_locations.get(coords)
        if dist is not None:
            return dist
        dist = self.distance(loc.x, loc.y)
        self.dist_to_locations[coords] = dist
        return dist

    def google_distance(self, x, y):
        """ Calculate google distance for two points """
        gmaps = googlemaps.Client(key=self.google_api_key)
        origin = (self.y, self.x)
        destination = (y, x)
        result = gmaps.distance_matrix(origin, destination)['rows'][0]['elements']
        distance = result['distance']['value']/1000
        return distance

    def populate_dist_lookup_with_google(self, locations):
        """ Calculate google distance for a point verses multiple points"""
        google_limit = 25  # google limited maximum number of elements per request
        origin = (self.y, self.x)
        locations = [(loc.y, loc.x) for loc in locations]
        len_last_batch = len(locations) % google_limit
        destinations_batches = []
        for i in range(0, len(locations[:-len_last_batch]), google_limit):
            destinations_batches.append(locations[i:i+google_limit])
        destinations_batches.append(locations[-len_last_batch:])
        gmaps = googlemaps.Client(key=self.google_api_key)
        distances = []
        for destinations in destinations_batches:
            result = gmaps.distance_matrix(origin, destinations)['rows'][0]['elements']
            distances.extend([item['distance']['value']/1000 for item in result])
        for idx, dist in enumerate(distances):
            coords = locations[idx]
            if not self.dist_to_locations.get(coords):
                self.dist_to_locations[coords] = dist

    def manhattan_distance(self, x, y):
        dx = np.abs(self.x - x)
        dy = np.abs(self.y - y)
        distance = 100 * (dx + dy)
        return distance

    def distance(self, x, y):
        try:
            dist = self.google_distance(x, y)
        except:
            dist = self.manhattan_distance(x, y)
        return dist


    def __str__(self):
        return f"Location:<{self.x},{self.y}>"

    def __repr__(self):
        return self.__str__()
