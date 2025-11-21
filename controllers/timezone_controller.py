from utils.timezones import (
    load_all_timezones,
    TZ_LOCATIONS,
)
from utils.geo import haversine


ALL_TIMEZONES = load_all_timezones()

def validate_lat_lon(latitude, longitude):
    """
    Validate that latitude and longitude are numeric and within valid ranges.

    Args:
        latitude (float or int): Latitude value.
        longitude (float or int): Longitude value.

    Raises:
        TypeError: If latitude or longitude are not numeric.
        ValueError: If latitude or longitude are out of valid ranges.
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        raise TypeError("Latitude and longitude must be numeric.")
    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90.")
    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180.")

def validate_offset(offset):
    """
    Validate that the UTC offset is numeric and within valid ranges.

    Args:
        offset (float or int): UTC offset value.

    Raises:
        TypeError: If offset is not numeric.
        ValueError: If offset is out of valid UTC range.
    """
    if not isinstance(offset, (int, float)):
        raise TypeError("Offset must be numeric.")
    if not (-12 <= offset <= 14):
        raise ValueError("UTC offset must be between -12 and 14.")


def tz_region(latitude: float, longitude: float):
    """
    Find all timezone regions that contain the given latitude and longitude.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.

    Returns:
        dict: Dictionary with a list of matching region names.
    """
    regions = []
    regions.extend(
        name
        for name, bounds in TZ_LOCATIONS.items()
        if (
            bounds["min_latitude"] <= latitude <= bounds["max_latitude"]
            and bounds["min_longitude"] <= longitude <= bounds["max_longitude"]
        )
    )
    return {"regions": regions}

def tz_regions():
    """
    Get a list of all timezone regions with their bounding coordinates.

    Returns:
        list: List of dictionaries with region name and bounds.
    """
    return [
        {"name": name, **bounds}
        for name, bounds in TZ_LOCATIONS.items()
    ]

def tz_region_nearest(latitude: float, longitude: float):
    """
    Find the nearest timezone region to the given latitude and longitude.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.

    Returns:
        dict: Dictionary with the nearest region name and distance in kilometers.
    """
    validate_lat_lon(latitude, longitude)
    min_dist = None
    nearest_region = None
    for name, bounds in TZ_LOCATIONS.items():
        center_lat = (bounds["min_latitude"] + bounds["max_latitude"]) / 2
        center_lon = (bounds["min_longitude"] + bounds["max_longitude"]) / 2
        dist = haversine(latitude, longitude, center_lat, center_lon)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            nearest_region = name
    return {
        "region": nearest_region,
        "distance_km": round(min_dist, 2) if min_dist is not None else None
    }

def tz_region_cities(region: str):
    """
    Get all cities within the bounding box of a given timezone region.

    Args:
        region (str): Name of the region.

    Returns:
        dict: Dictionary with region name and list of cities, or error if not
            found.
    """
    region = region.lower()
    if region not in TZ_LOCATIONS:
        return {"error": "Region not found"}
    bounds = TZ_LOCATIONS[region]
    cities = [
        tz for tz in ALL_TIMEZONES
        if (
            bounds["min_latitude"] <= tz["latitude"] <= bounds["max_latitude"]
            and bounds["min_longitude"] <= tz["longitude"] <= bounds["max_longitude"]
        )
    ]
    return {"region": region, "cities": cities}

def cities_nearest(latitude: float, longitude: float):
    """
    Find the four nearest timezone cities to the given latitude and longitude.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.

    Returns:
        dict: Dictionary with the closest timezone location and a list of
            nearest cities.
    """
    validate_lat_lon(latitude, longitude)
    distances = []
    for tz in ALL_TIMEZONES:
        dist = haversine(latitude, longitude, tz["latitude"], tz["longitude"])
        distances.append((dist, tz))
    distances.sort(key=lambda x: x[0])
    nearest = [
        {
            "name": tz["name"],
            "latitude": tz["latitude"],
            "longitude": tz["longitude"],
            "distance_km": round(dist, 2),
            "utc_offset": tz["utc_offset"],
            "dst": tz["dst"],
            "region": tz["region"],
        }
        for dist, tz in distances[:4]
    ]
    tz_location = nearest[0]["name"] if nearest else None
    return {
        "tz_location": tz_location,
        "nearest_cities": nearest,
    }

def cities_in_radius(latitude: float, longitude: float, radius_km: float):
    """
    Find all timezone cities within a given radius (in kilometers) of a point.

    Args:
        latitude (float): Latitude value.
        longitude (float): Longitude value.
        radius_km (float): Search radius in kilometers.

    Returns:
        dict: Dictionary with a list of cities within the radius.

    Raises:
        ValueError: If radius_km is not a non-negative number.
    """
    validate_lat_lon(latitude, longitude)
    if not isinstance(radius_km, (int, float)) or radius_km < 0:
        raise ValueError("Radius must be a non-negative number.")

    result = []
    for city in ALL_TIMEZONES:
        dist = haversine(latitude, longitude, city["latitude"], city["longitude"])
        if dist <= radius_km:
            city_copy = city.copy()
            city_copy["distance_km"] = round(dist, 2)
            result.append(city_copy)
    result.sort(key=lambda c: c["distance_km"])
    return {"cities": result}

def cities_by_utc_offset(offset: float):
    """
    Get all timezone cities with a specific UTC offset.

    Args:
        offset (float): UTC offset value.

    Returns:
        dict: Dictionary with a list of cities matching the offset.
    """
    validate_offset(offset)
    result = []
    for city in ALL_TIMEZONES:
        if float(city.get("utc_offset", 0)) == offset:
            city_copy = city.copy()
            result.append(city_copy)
    return {"cities": result}

def cities_with_dst(dst: bool = True, region: str = None):
    """
    Get all timezone cities that observe (or do not observe) daylight saving
    time (DST).

    Args:
        dst (bool, optional): Whether to filter for DST-observing cities.
            Defaults to True.
        region (str, optional): If provided, filter by region.

    Returns:
        dict: Dictionary with a list of cities matching the DST and region
            criteria.
    """
    result = []
    for city in ALL_TIMEZONES:
        if bool(city.get("dst", False)) == dst:
            if region and city["region"] != region:
                continue
            city_copy = city.copy()
            result.append(city_copy)
    return {"cities": result}

def city_extremes(offset: float):
    """
    Find the northernmost, southernmost, easternmost, and westernmost cities for
    a given UTC offset.

    Args:
        offset (float): UTC offset value.

    Returns:
        dict: Dictionary with the extreme cities, or error if none found.
    """
    validate_offset(offset)
    cities = [
        city
        for city in ALL_TIMEZONES
        if float(city.get("utc_offset", 0)) == offset
    ]
    if not cities:
        return {"error": "No cities found for this UTC offset."}
    north = max(cities, key=lambda c: c["latitude"])
    south = min(cities, key=lambda c: c["latitude"])
    east = max(cities, key=lambda c: c["longitude"])
    west = min(cities, key=lambda c: c["longitude"])
    return {
        "north": north,
        "south": south,
        "east": east,
        "west": west,
    }