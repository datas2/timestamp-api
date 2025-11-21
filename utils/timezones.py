import yaml
from pathlib import Path

def load_all_timezones():
    """
    Loads all timezone YAML files from the 'data/timezones' directory,
    returning a single sorted list of city/timezone dictionaries.
    Each YAML file should represent a region and contain cities as keys.
    """
    # Adjust the path to point to the data/timezones directory
    tz_dir = Path(__file__).parent.parent / "data" / "timezones"
    all_timezones = []
    for file in tz_dir.glob("*.yaml"):
        region = file.stem.lower()
        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            all_timezones.extend(
                {
                    "name": name,
                    "latitude": float(info["latitude"]),
                    "longitude": float(info["longitude"]),
                    "utc_offset": info.get("utc_offset"),
                    "dst": info.get("dst"),
                    "region": region,
                }
                for name, info in data.items()
            )
    # Global sorted list for efficient lookups
    # Sort by utc_offset, then longitude, then latitude
    all_timezones.sort(key=lambda x: (
        float(x["utc_offset"]) if x["utc_offset"] is not None else 0.0,
        x["longitude"],
        x["latitude"]
    ))
    return all_timezones

TZ_LOCATIONS = dict(
    sorted(
        {
            "africa": {
                "min_latitude": -29.32583,
                "max_latitude": 36.80649,
                "min_longitude": -17.44667,
                "max_longitude": 45.31816,
            },
            "america": {
                "min_latitude": -54.8019,
                "max_latitude": 76.7697,
                "min_longitude": -176.65,
                "max_longitude": -18.6667
            },
            "antarctica": {
                "min_latitude": -90.0,
                "max_latitude": -54.4974,
                "min_longitude": -68.1258,
                "max_longitude": 166.6863
            },
            "arctic": {
                "min_latitude": 77.5536,
                "max_latitude": 78.2232,
                "min_longitude": 15.6469,
                "max_longitude": 23.6703
            },
            "asia": {
                "min_latitude": -8.5569,
                "max_latitude": 67.4667,
                "min_longitude": 33.3823,
                "max_longitude": 177.5167
            },
            "atlantic": {
                "min_latitude": -54.4296,
                "max_latitude": 71.0,
                "min_longitude": -64.7505,
                "max_longitude": 8.0
            },
            "australia": {
                "min_latitude": -42.8821,
                "max_latitude": -12.4634,
                "min_longitude": 115.8605,
                "max_longitude": 159.0833
            },
            "europe": {
                "min_latitude": 35.1856,
                "max_latitude": 64.9631,
                "min_longitude": -19.0208,
                "max_longitude": 49.6676
            },
            "indian": {
                "min_latitude": -49.2800,
                "max_latitude": 3.2028,
                "min_longitude": 43.3333,
                "max_longitude": 105.6904
            },
            "pacific": {
                "min_latitude": -78.4644,
                "max_latitude": 28.2000,
                "min_longitude": -177.3500,
                "max_longitude": 179.2167
            }
        }.items(),
        key=lambda item: item[1]["min_longitude"]
    )
)
