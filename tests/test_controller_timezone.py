import pytest
from controllers import timezone_controller

# Mock data for ALL_TIMEZONES and TZ_LOCATIONS
@pytest.fixture(autouse=True)
def mock_data(monkeypatch):
    # Arrange
    mock_timezones = [
        {
            "name": "London",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "utc_offset": 0,
            "dst": True,
            "region": "europe",
        },
        {
            "name": "Paris",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "utc_offset": 1,
            "dst": True,
            "region": "europe",
        },
        {
            "name": "Tokyo",
            "latitude": 35.6895,
            "longitude": 139.6917,
            "utc_offset": 9,
            "dst": False,
            "region": "asia",
        },
        {
            "name": "Cape Town",
            "latitude": -33.9249,
            "longitude": 18.4241,
            "utc_offset": 2,
            "dst": False,
            "region": "africa",
        },
    ]
    mock_locations = {
        "europe": {
            "min_latitude": 35.0,
            "max_latitude": 65.0,
            "min_longitude": -20.0,
            "max_longitude": 50.0,
        },
        "asia": {
            "min_latitude": 10.0,
            "max_latitude": 70.0,
            "min_longitude": 60.0,
            "max_longitude": 150.0,
        },
        "africa": {
            "min_latitude": -35.0,
            "max_latitude": 37.0,
            "min_longitude": -20.0,
            "max_longitude": 50.0,
        },
    }
    monkeypatch.setattr(timezone_controller, "ALL_TIMEZONES", mock_timezones)
    monkeypatch.setattr(timezone_controller, "TZ_LOCATIONS", mock_locations)
    from utils.geo import haversine
    monkeypatch.setattr(timezone_controller, "haversine", haversine)

@pytest.mark.parametrize(
    "latitude, longitude, expected_regions, description",
    [
        (51.0, 0.0, ["europe"], "inside europe"),
        (36.0, 18.0, ["europe", "africa"], "border between europe and africa"),
        (35.6895, 139.6917, ["asia"], "inside asia"),
        (0.0, 0.0, ["africa"], "inside africa (by bounds)"),
    ],
    ids=["europe", "border-europe-africa", "asia", "none"]
)
def test_tz_region(latitude, longitude, expected_regions, description):
    # Act
    result = timezone_controller.tz_region(latitude, longitude)

    # Assert
    assert set(result["regions"]) == set(expected_regions), f"Failed: {description}"

def test_tz_regions():
    # Act
    result = timezone_controller.tz_regions()

    # Assert
    assert isinstance(result, list)
    assert all("name" in r and "min_latitude" in r for r in result)
    assert {r["name"] for r in result} == {"europe", "asia", "africa"}

@pytest.mark.parametrize(
    "latitude, longitude, expected_region, description",
    [
        (51.0, 0.0, "europe", "nearest to europe"),
        (35.0, 140.0, "asia", "nearest to asia"),
        (-34.0, 19.0, "africa", "nearest to africa"),
    ],
    ids=["nearest-europe", "nearest-asia", "nearest-africa"]
)
def test_tz_region_nearest(latitude, longitude, expected_region, description):
    # Act
    result = timezone_controller.tz_region_nearest(latitude, longitude)

    # Assert
    assert result["region"] == expected_region, f"Failed: {description}"
    assert isinstance(result["distance_km"], float)

@pytest.mark.parametrize(
    "latitude, longitude, error_type, error_msg, description",
    [
        (100, 0, ValueError, "Latitude must be between -90 and 90.", "latitude > 90"),
        (-100, 0, ValueError, "Latitude must be between -90 and 90.", "latitude < -90"),
        (0, 200, ValueError, "Longitude must be between -180 and 180.", "longitude > 180"),
        (0, -200, ValueError, "Longitude must be between -180 and 180.", "longitude < -180"),
        ("a", 0, TypeError, "Latitude and longitude must be numeric.", "latitude not numeric"),
        (0, "b", TypeError, "Latitude and longitude must be numeric.", "longitude not numeric"),
    ],
    ids=["lat-over-90", "lat-under-90", "lon-over-180", "lon-under-180", "lat-not-numeric", "lon-not-numeric"]
)
def test_tz_region_nearest_invalid(latitude, longitude, error_type, error_msg, description):
    # Act & Assert
    with pytest.raises(error_type, match=error_msg):
        timezone_controller.tz_region_nearest(latitude, longitude)

@pytest.mark.parametrize(
    "region, expected_city_names, description",
    [
        ("europe", ["London", "Paris"], "cities in europe"),
        ("asia", ["Tokyo"], "cities in asia"),
        ("africa", ["Cape Town"], "cities in africa"),
        ("unknown", None, "region not found"),
    ],
    ids=["europe-cities", "asia-cities", "africa-cities", "region-not-found"]
)
def test_tz_region_cities(region, expected_city_names, description):
    # Act
    result = timezone_controller.tz_region_cities(region)

    # Assert
    if expected_city_names is None:
        assert "error" in result
    else:
        assert result["region"] == region.lower()
        assert {c["name"] for c in result["cities"]} == set(expected_city_names)

@pytest.mark.parametrize(
    "latitude, longitude, expected_names, description",
    [
        (51.5074, -0.1278, ["London", "Paris", "Tokyo", "Cape Town"], "London nearest"),
        (35.6895, 139.6917, ["Tokyo", "London", "Paris", "Cape Town"], "Tokyo nearest"),
        (-33.9249, 18.4241, ["Cape Town", "Paris", "London", "Tokyo"], "Cape Town nearest"),
    ],
    ids=["london-nearest", "tokyo-nearest", "capetown-nearest"]
)
def test_cities_nearest(latitude, longitude, expected_names, description):
    # Act
    result = timezone_controller.cities_nearest(latitude, longitude)

    # Assert
    assert result["tz_location"] == expected_names[0]
    assert [c["name"] for c in result["nearest_cities"]] == expected_names

@pytest.mark.parametrize(
    "latitude, longitude, error_type, error_msg, description",
    [
        (100, 0, ValueError, "Latitude must be between -90 and 90.", "latitude > 90"),
        (-100, 0, ValueError, "Latitude must be between -90 and 90.", "latitude < -90"),
        (0, 200, ValueError, "Longitude must be between -180 and 180.", "longitude > 180"),
        (0, -200, ValueError, "Longitude must be between -180 and 180.", "longitude < -180"),
        ("a", 0, TypeError, "Latitude and longitude must be numeric.", "latitude not numeric"),
        (0, "b", TypeError, "Latitude and longitude must be numeric.", "longitude not numeric"),
    ],
    ids=["lat-over-90", "lat-under-90", "lon-over-180", "lon-under-180", "lat-not-numeric", "lon-not-numeric"]
)
def test_cities_nearest_invalid(latitude, longitude, error_type, error_msg, description):
    # Act & Assert
    with pytest.raises(error_type, match=error_msg):
        timezone_controller.cities_nearest(latitude, longitude)

@pytest.mark.parametrize(
    "latitude, longitude, radius_km, expected_names, description",
    [
        (51.5074, -0.1278, 500, ["London", "Paris"], "London and Paris within 500km"),
        (35.6895, 139.6917, 100, ["Tokyo"], "Only Tokyo within 100km"),
        (0.0, 0.0, 100, [], "No cities within 100km of (0,0)"),
    ],
    ids=["london-paris-radius", "tokyo-radius", "none-radius"]
)
def test_cities_in_radius(latitude, longitude, radius_km, expected_names, description):
    # Act
    result = timezone_controller.cities_in_radius(latitude, longitude, radius_km)

    # Assert
    assert [c["name"] for c in result["cities"]] == expected_names

@pytest.mark.parametrize(
    "latitude, longitude, radius_km, error_type, error_msg, description",
    [
        (100, 0, 100, ValueError, "Latitude must be between -90 and 90.", "latitude > 90"),
        (0, 200, 100, ValueError, "Longitude must be between -180 and 180.", "longitude > 180"),
        (0, 0, -1, ValueError, "Radius must be a non-negative number.", "negative radius"),
        ("a", 0, 100, TypeError, "Latitude and longitude must be numeric.", "latitude not numeric"),
        (0, "b", 100, TypeError, "Latitude and longitude must be numeric.", "longitude not numeric"),
    ],
    ids=["lat-over-90", "lon-over-180", "negative-radius", "lat-not-numeric", "lon-not-numeric"]
)
def test_cities_in_radius_invalid(latitude, longitude, radius_km, error_type, error_msg, description):
    # Act & Assert
    with pytest.raises(error_type, match=error_msg):
        timezone_controller.cities_in_radius(latitude, longitude, radius_km)

@pytest.mark.parametrize(
    "offset, expected_names, description",
    [
        (0, ["London"], "UTC+0"),
        (1, ["Paris"], "UTC+1"),
        (9, ["Tokyo"], "UTC+9"),
    ],
    ids=["utc0", "utc1", "utc9"]
)
def test_cities_by_utc_offset(offset, expected_names, description):
    # Act
    result = timezone_controller.cities_by_utc_offset(offset)

    # Assert
    assert [c["name"] for c in result["cities"]] == expected_names

@pytest.mark.parametrize(
    "offset, error_type, error_msg, description",
    [
        (15, ValueError, "UTC offset must be between -12 and 14.", "offset > 14"),
        (-13, ValueError, "UTC offset must be between -12 and 14.", "offset < -12"),
        ("a", TypeError, "Offset must be numeric.", "offset not numeric"),
    ],
    ids=["offset-over-14", "offset-under-12", "offset-not-numeric"]
)
def test_cities_by_utc_offset_invalid(offset, error_type, error_msg, description):
    # Act & Assert
    with pytest.raises(error_type, match=error_msg):
        timezone_controller.cities_by_utc_offset(offset)

@pytest.mark.parametrize(
    "dst, region, expected_names, description",
    [
        (True, None, ["London", "Paris"], "DST true, all regions"),
        (False, None, ["Tokyo", "Cape Town"], "DST false, all regions"),
        (True, "europe", ["London", "Paris"], "DST true, europe only"),
        (False, "africa", ["Cape Town"], "DST false, africa only"),
        (True, "asia", [], "DST true, asia only"),
    ],
    ids=["dst-true-all", "dst-false-all", "dst-true-europe", "dst-false-africa", "dst-true-asia"]
)
def test_cities_with_dst(dst, region, expected_names, description):
    # Act
    result = timezone_controller.cities_with_dst(dst, region)

    # Assert
    assert [c["name"] for c in result["cities"]] == expected_names

@pytest.mark.parametrize(
    "offset, expected_extremes, description",
    [
        (0, {"north": "London", "south": "London", "east": "London", "west": "London"}, "UTC+0 extremes"),
        (1, {"north": "Paris", "south": "Paris", "east": "Paris", "west": "Paris"}, "UTC+1 extremes"),
        (2, {"north": "Cape Town", "south": "Cape Town", "east": "Cape Town", "west": "Cape Town"}, "UTC+2 extremes"),
        (9, {"north": "Tokyo", "south": "Tokyo", "east": "Tokyo", "west": "Tokyo"}, "UTC+9 extremes"),
        (5, None, "No cities found for this UTC offset."),
    ],
    ids=["extremes-utc0", "extremes-utc1", "extremes-utc2", "extremes-utc9", "extremes-utc5"]
)
def test_city_extremes(offset, expected_extremes, description):
    # Act
    result = timezone_controller.city_extremes(offset)

    # Assert
    if expected_extremes is None:
        assert "error" in result
    else:
        for key in ["north", "south", "east", "west"]:
            assert result[key]["name"] == expected_extremes[key]

@pytest.mark.parametrize(
    "offset, error_type, error_msg, description",
    [
        (15, ValueError, "UTC offset must be between -12 and 14.", "offset > 14"),
        (-13, ValueError, "UTC offset must be between -12 and 14.", "offset < -12"),
        ("a", TypeError, "Offset must be numeric.", "offset not numeric"),
        (99, ValueError, "UTC offset must be between -12 and 14.", "offset out of range"),
    ],
    ids=["offset-over-14", "offset-under-12", "offset-not-numeric", "offset-out-of-range"]
)
def test_city_extremes_invalid(offset, error_type, error_msg, description):
    # Act & Assert
    with pytest.raises(error_type, match=error_msg):
        timezone_controller.city_extremes(offset)
