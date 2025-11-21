from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (in km).
    """
    if not all(isinstance(coord, (int, float)) for coord in [lat1, lon1, lat2, lon2]):
        raise TypeError("All coordinates must be numeric values.")

    if any(coord > 90 or coord < -90 for coord in [lat1, lat2]):
        raise ValueError("Latitude must be between -90 and 90 degrees.")
    if any(coord > 180 or coord < -180 for coord in [lon1, lon2]):
        raise ValueError("Longitude must be between -180 and 180 degrees.")

    R = 6371.0  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
