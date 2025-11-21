# timezone-api

A FastAPI microservice for timezone and city lookup, region bounding, and geospatial queries.

---

## API Description

This API provides endpoints to:

-   Check API status and uptime
-   Find timezone regions by coordinates
-   List all timezone regions and their bounding boxes
-   Find the nearest timezone region or city to a point
-   List all cities in a region, within a radius, by UTC offset, or with DST
-   Find the northernmost, southernmost, easternmost, and westernmost cities for a UTC offset

All endpoints (except `/status`) require an API key via the `X-API-KEY` header.

---

## Endpoints

### 1. `GET /status`

Returns the status of the API, including name, version, and uptime (in seconds).

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/status'
```

**Response Example:**

```json
{
	"msg": "API status 🚀",
	"name": "timestamp-api",
	"version": "1.0.0",
	"uptime": 1234
}
```

### 2. `GET /tz_region`

Returns all regions that contain the given point (latitude, longitude).

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/tz_region?latitude=22.34&longitude=-78.983' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
	"regions": ["pacific", "america"]
}
```

### 3. `GET /tz_regions`

Returns all regions and their bounding box limits.

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/tz_regions' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
[
    {
        "name": "africa",
        "min_latitude": -29.32583,
        "max_latitude": 36.80649,
        "min_longitude": -17.44667,
        "max_longitude": 45.31816
    },
    ...
]
```

### 4. `GET /tz_region_nearest`

Returns the nearest region to the given point (latitude, longitude).

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/tz_region_nearest?latitude=38.954&longitude=-12.451' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
	"region": "europe",
	"distance_km": 2504.48
}
```

### 5. `GET /tz_region_cities`

Returns all cities/timezones within the specified region.

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/tz_region_cities?region=america' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
    "region": "america",
    "cities": [
        {
        "name": "New_York",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "utc_offset": -5,
        "dst": true,
        "region": "america"
        },
        ...
    ]
}
```

### 6. `GET /cities_nearest`

Returns the 4 nearest cities to the given point (latitude, longitude).

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/cities_nearest?latitude=40.7128&longitude=-74.0060' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
    "tz_location": "New_York",
    "nearest_cities": [
        {
        "name": "New_York",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "distance_km": 0.0,
        "utc_offset": -5,
        "dst": true,
        "region": "america"
        },
        ...
    ]
}
```

### 7. `GET /cities_in_radius`

Returns all cities within a given radius (in km) from the point.

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/cities_in_radius?latitude=40.7128&longitude=-74.0060&radius_km=750' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
	"cities": [
		{
			"name": "New_York",
			"latitude": 40.7128,
			"longitude": -74.006,
			"utc_offset": -5,
			"dst": true,
			"region": "america",
			"distance_km": 0.0
		},
		{
			"name": "Beulah",
			"latitude": 44.3759,
			"longitude": -73.2121,
			"utc_offset": -5,
			"dst": true,
			"region": "america",
			"distance_km": 412.47
		},
		{
			"name": "Montreal",
			"latitude": 45.5017,
			"longitude": -73.5673,
			"utc_offset": -5,
			"dst": true,
			"region": "america",
			"distance_km": 533.69
		},
		{
			"name": "Toronto",
			"latitude": 43.65107,
			"longitude": -79.347015,
			"utc_offset": -5,
			"dst": true,
			"region": "america",
			"distance_km": 547.92
		}
	]
}
```

### 8. `GET /cities_by_utc_offset`

Returns all cities with the specified UTC offset.

**Request Example:**

```bash
curl --location 'http://127.0.0.1:8000/cities_by_utc_offset?offset=-5' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
    "cities": [
        {
        "name": "New York",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "utc_offset": -5,
        "dst": true,
        "region": "america"
        },
        ...
    ]
}
```

### 9. `GET /cities_with_dst`

Returns all cities that currently have DST (Daylight Saving Time) active or not.

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/cities_with_dst?dst=true' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
    "cities": [
        {
        "name": "New York",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "utc_offset": -5,
        "dst": true,
        "region": "america"
        },
        ...
    ]
}
```

### 10. `GET /city_extremes`

Returns the northernmost, southernmost, easternmost, and westernmost cities for a given UTC offset.

**Request Example:**

```bash
    curl --location 'http://127.0.0.1:8000/city_extremes?offset=0' --header 'x-api-key: your_api_key_here'
```

**Response Example:**

```json
{
	"north": {
		"name": "Danmarkshavn",
		"latitude": 76.7697,
		"longitude": -18.6667,
		"utc_offset": 0,
		"dst": false,
		"region": "america"
	},
	"south": {
		"name": "South_Pole",
		"latitude": -90.0,
		"longitude": 0.0,
		"utc_offset": 0,
		"dst": false,
		"region": "antarctica"
	},
	"east": {
		"name": "Casey",
		"latitude": -66.2833,
		"longitude": 110.5333,
		"utc_offset": 0,
		"dst": false,
		"region": "antarctica"
	},
	"west": {
		"name": "Azores",
		"latitude": 37.7412,
		"longitude": -25.6756,
		"utc_offset": 0,
		"dst": true,
		"region": "atlantic"
	}
}
```

## Error Status Documentation

-   **401 Unauthorized:** Returned if the `X-API-KEY` header is missing or invalid (for all endpoints except /status).

```json
{
	"detail": "Invalid or missing API Key."
}
```

-   **422 Unprocessable Entity:** Returned if required query parameters are missing or invalid.
-   **404 Not Found:** Returned for endpoints like `/tz_region_cities` or `/city_extremes` if the region or UTC offset is not found.

```json
{
	"error": "Region not found"
}
```

or

```json
{
	"error": "No cities found for this UTC offset."
}
```

## How to Run Locally

-   Clone the repository
-   Install dependencies

```bash
pip install -r requirements.txt
```

-   Create a .env file and add your API key

```txt
API_KEY=your_api_key_here
```

-   Run the application

```bash
uvicorn main:app --reload
```

-   Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Relevant Notes

-   All endpoints except `/status` require the `X-API-KEY` header.
-   The API expects valid latitude and longitude values for geospatial queries.
-   The bounding boxes for regions are defined in `utils/timezones.py` (TZ_LOCATIONS).
-   CORS is enabled for all origins for easy testing.
-   For production, use a strong API key and restrict CORS as needed.
    REPLACE
