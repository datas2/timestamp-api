import pytest
from utils.geo import haversine

@pytest.mark.parametrize(
    "lat1, lon1, lat2, lon2, expected, description",
    [
        # Happy path: same point
        (0, 0, 0, 0, 0.0, "zero distance (same point)"),
        # Happy path: equator to equator, 1 degree longitude apart
        (0, 0, 0, 1, 111.195, "equator, 1 degree longitude"),
        # Happy path: pole to pole
        (90, 0, -90, 0, 20015.087, "north pole to south pole"),
        # Happy path: known cities (London to Paris)
        (51.5074, -0.1278, 48.8566, 2.3522, 343.556, "London to Paris"),
        # Happy path: antipodal points
        (0, 0, 0, 180, 20015.087, "antipodal points"),
    ],
    ids=[
        "same-point",
        "equator-1deg-lon",
        "pole-to-pole",
        "london-to-paris",
        "antipodal",
    ]
)
def test_haversine_happy_and_edge_cases(lat1, lon1, lat2, lon2, expected, description):
    # Act
    result = haversine(lat1, lon1, lat2, lon2)

    # Assert
    # Allow a small margin of error due to floating point math
    assert pytest.approx(result, abs=0.01) == expected, f"Failed: {description}"


@pytest.mark.parametrize(
    "lat1, lon1, lat2, lon2, error_type, description",
    [
        # Error case: non-numeric input
        ("a", 0, 0, 0, TypeError, "lat1 is not a number"),
        (0, "b", 0, 0, TypeError, "lon1 is not a number"),
        (0, 0, "c", 0, TypeError, "lat2 is not a number"),
        (0, 0, 0, "d", TypeError, "lon2 is not a number"),
        # Error case: missing arguments
        (0, 0, 0, None, TypeError, "missing lon2"),
        (0, 0, None, None, TypeError, "missing lat2 and lon2"),
        # Error case: too few arguments
        (0, 0, 0, None, TypeError, "missing lon2"),
    ],
    ids=[
        "lat1-non-numeric",
        "lon1-non-numeric",
        "lat2-non-numeric",
        "lon2-non-numeric",
        "missing-lon2",
        "missing-lat2-lon2",
        "too-few-args",
    ]
)
def test_haversine_error_cases(lat1, lon1, lat2, lon2, error_type, description):
    # Act & Assert
    with pytest.raises(error_type, match=""):
        haversine(lat1, lon1, lat2, lon2)
