import math

import numpy as n
class GpsPoint:
    def __init__(self, latitude, longitude):
        self._latitude = latitude
        self._longitude = longitude
        self._latitude_radian = latitude * math.pi / 180
        self._longitude_radian = longitude * math.pi / 180
        self._earth_radius = 6371e3

    def latitude(self, value):
        self._latitude = value
        self._latitude_radian = value * math.pi/180

    def latitude(self):
        return self._latitude

    def latitude_radian(self):
        return self._latitude_radian

    def longitude(self, value):
        self._longitude = value
        self._longitude_radian = value * math.pi / 180

    def longitude(self):
        return self._longitude

    def longitude_radian(self):
        return self._longitude_radian

    def distance_to_point(self, point):
        delta_lat = (point.latitude() - self._latitude) * math.pi/180
        delta_long = (point.longitude() - self._longitude) * math.pi/180

        a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + math.cos(self.latitude_radian()) * \
            math.cos(point.latitude_radian()) * math.sin(delta_long/2) * math.sin(delta_long/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        #print('Distance: ' + str(self._earth_radius * c))
        return self._earth_radius * c

    def point_with_distance(self, distance, bearing):
        bearing = bearing * math.pi / 180
        lat_radian = math.asin(math.sin(self._latitude_radian) * math.cos(distance/self._earth_radius) +
                               math.cos(self.latitude_radian()) * math.sin(distance/self._earth_radius) *
                               math.cos(bearing))

        long_radian = self.longitude_radian() + math.atan2((math.sin(bearing) * math.sin(distance / self._earth_radius) * math.cos(self.latitude_radian())),
                                                           (math.cos(distance / self._earth_radius) - math.sin(self.latitude_radian()) * math.sin(lat_radian)))
        return GpsPoint(lat_radian * 180/math.pi, long_radian * 180/math.pi)

    def bearing_between_point(self, gpsPoint):
        y = math.sin(gpsPoint.longitude_radian() - self.longitude_radian()) * math.cos(gpsPoint.latitude_radian())
        x = math.cos(self.latitude_radian()) * math.sin(gpsPoint.latitude_radian()) - math.sin(self.latitude_radian()) * math.cos(gpsPoint.latitude_radian())*math.cos(gpsPoint.longitude_radian() - self.longitude_radian())
        return (math.atan2(y, x)*180/math.pi + 360) % 360

    def toString(self):
        return "Latitude: " + str(self.latitude()) + " Longitude: " + str(self.longitude())
