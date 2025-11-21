from fastapi import APIRouter
from controllers import timezone_controller

router = APIRouter()

@router.get("/tz_region")
def tz_region(latitude: float, longitude: float):
    return timezone_controller.tz_region(latitude, longitude)

@router.get("/tz_regions")
def tz_regions():
    return timezone_controller.tz_regions()

@router.get("/tz_region_nearest")
def tz_region_nearest(latitude: float, longitude: float):
    return timezone_controller.tz_region_nearest(latitude, longitude)

@router.get("/tz_region_cities")
def tz_region_cities(region: str):
    return timezone_controller.tz_region_cities(region)

@router.get("/cities_nearest")
def cities_nearest(latitude: float, longitude: float):
    return timezone_controller.cities_nearest(latitude, longitude)

@router.get("/cities_in_radius")
def cities_in_radius(latitude: float, longitude: float, radius_km: float):
    return timezone_controller.cities_in_radius(latitude, longitude, radius_km)

@router.get("/cities_by_utc_offset")
def cities_by_utc_offset(offset: float):
    return timezone_controller.cities_by_utc_offset(offset)

@router.get("/cities_with_dst")
def cities_with_dst(dst: bool = True, region: str = None):
    return timezone_controller.cities_with_dst(dst, region)

@router.get("/city_extremes")
def city_extremes(offset: float):
    return timezone_controller.city_extremes(offset)
