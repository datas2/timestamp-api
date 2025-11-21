import pytest
import yaml
from pathlib import Path
from unittest import mock

from utils.timezones import load_all_timezones

@pytest.fixture
def mock_tz_dir(tmp_path):
    # Arrange
    # Create a mock directory structure and files
    tz_dir = tmp_path / "data" / "timezones"
    tz_dir.mkdir(parents=True)
    return tz_dir

@pytest.mark.parametrize(
    "files, expected, description",
    [
        (
            # Happy path: two regions, multiple cities
            {
                "europe.yaml": {
                    "London": {
                        "latitude": "51.5074",
                        "longitude": "-0.1278",
                        "utc_offset": "0",
                        "dst": True,
                    },
                    "Paris": {
                        "latitude": "48.8566",
                        "longitude": "2.3522",
                        "utc_offset": "1",
                        "dst": True,
                    },
                },
                "asia.yaml": {
                    "Tokyo": {
                        "latitude": "35.6895",
                        "longitude": "139.6917",
                        "utc_offset": "9",
                        "dst": False,
                    }
                },
            },
            [
                # Sorted by utc_offset, then longitude, then latitude
                {
                    "name": "London",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "utc_offset": "0",
                    "dst": True,
                    "region": "europe",
                },
                {
                    "name": "Paris",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "utc_offset": "1",
                    "dst": True,
                    "region": "europe",
                },
                {
                    "name": "Tokyo",
                    "latitude": 35.6895,
                    "longitude": 139.6917,
                    "utc_offset": "9",
                    "dst": False,
                    "region": "asia",
                },
            ],
            "multiple regions, multiple cities",
        ),
        (
            # Edge case: missing utc_offset and dst
            {
                "america.yaml": {
                    "New York": {
                        "latitude": "40.7128",
                        "longitude": "-74.0060",
                    }
                }
            },
            [
                {
                    "name": "New York",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "utc_offset": None,
                    "dst": None,
                    "region": "america",
                }
            ],
            "missing utc_offset and dst",
        ),
        (
            # Edge case: empty file
            {
                "empty.yaml": {}
            },
            [],
            "empty file",
        ),
        (
            # Edge case: multiple cities with same utc_offset
            {
                "test.yaml": {
                    "A": {
                        "latitude": "1.0",
                        "longitude": "2.0",
                        "utc_offset": "3",
                    },
                    "B": {
                        "latitude": "2.0",
                        "longitude": "1.0",
                        "utc_offset": "3",
                    },
                }
            },
            [
                {
                    "name": "B",
                    "latitude": 2.0,
                    "longitude": 1.0,
                    "utc_offset": "3",
                    "dst": None,
                    "region": "test",
                },
                {
                    "name": "A",
                    "latitude": 1.0,
                    "longitude": 2.0,
                    "utc_offset": "3",
                    "dst": None,
                    "region": "test",
                },
            ],
            "same utc_offset, sort by longitude",
        ),
    ],
    ids=[
        "happy-path-multi-region",
        "missing-utc-dst",
        "empty-file",
        "same-utc-offset",
    ]
)
def test_load_all_timezones_happy_and_edge_cases(files, expected, description, mock_tz_dir, monkeypatch):
    # Arrange
    # Write the YAML files
    for fname, content in files.items():
        with open(mock_tz_dir / fname, "w", encoding="utf-8") as f:
            yaml.dump(content, f)

    # Patch the tz_dir path in the function to use our temp directory
    patch_path = mock.patch(
        "utils.timezones.Path",
        wraps=Path,
    )
    with patch_path as mock_path:
        # Patch __file__ to simulate the correct parent directory
        monkeypatch.setattr("utils.timezones.__file__", str(mock_tz_dir.parent.parent / "utils" / "timezones.py"))
        # Patch Path.glob to only return our test files, avoiding recursion
        original_glob = Path.glob
        monkeypatch.setattr(
            Path,
            "glob",
            lambda self, pattern: list(original_glob(self, pattern)) if self != mock_tz_dir else list(original_glob(mock_tz_dir, pattern))
        )

        # Act
        result = load_all_timezones()

    # Assert
    assert result == expected, f"Failed: {description}"


@pytest.mark.parametrize(
    "files, error_type, description",
    [
        (
            # Error case: malformed YAML
            {"bad.yaml": "not: [valid, yaml"},
            yaml.YAMLError,
            "malformed yaml",
        ),
        (
            # Error case: missing latitude/longitude keys
            {"bad.yaml": {"City": {"utc_offset": "1"}}},
            KeyError,
            "missing latitude/longitude",
        ),
        (
            # Error case: latitude/longitude not convertible to float
            {"bad.yaml": {"City": {"latitude": "not_a_float", "longitude": "0"}}},
            ValueError,
            "latitude not float",
        ),
    ],
    ids=[
        "malformed-yaml",
        "missing-lat-lon",
        "lat-not-float",
    ]
)
def test_load_all_timezones_error_cases(files, error_type, description, mock_tz_dir, monkeypatch):
    # Arrange
    for fname, content in files.items():
        with open(mock_tz_dir / fname, "w", encoding="utf-8") as f:
            if isinstance(content, dict):
                yaml.dump(content, f)
            else:
                f.write(content)  # Write malformed YAML directly

    patch_path = mock.patch(
        "utils.timezones.Path",
        wraps=Path,
    )
    with patch_path as mock_path:
        monkeypatch.setattr("utils.timezones.__file__", str(mock_tz_dir.parent.parent / "utils" / "timezones.py"))
        # Patch Path.glob to only return our test files, avoiding recursion
        original_glob = Path.glob
        monkeypatch.setattr(
            Path,
            "glob",
            lambda self, pattern: list(original_glob(self, pattern)) if self != mock_tz_dir else list(original_glob(mock_tz_dir, pattern))
        )

        # Act & Assert
        with pytest.raises(error_type):
            load_all_timezones()
