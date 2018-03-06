import numpy as np

R = 6371000#earth's radius in meters.
AVERAGE_BUS_SPEED = 5.0 #m/s
AVERAGE_WALKING_SPEED = 0.8 #m/s

def distance_in_meters(start_lat, start_lon, end_lat, end_lon):
    """Distance in meters

    """
    start_lat, start_lon, end_lat, end_lon = map(np.deg2rad, [start_lat, start_lon, end_lat, end_lon])
    x = (end_lon - start_lon) * np.cos(0.5*(start_lat+end_lat))
    y = end_lat - start_lat
    return R * np.sqrt(x**2 + y**2)


def estimate_walking_time(d):
    return d / AVERAGE_WALKING_SPEED

def estimate_bus_trip_time(d):
    return d / AVERAGE_BUS_SPEED