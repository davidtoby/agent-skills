# Demoted legacy skill: `openclaw-imports/local-places`

This file was copied during an umbrella-building consolidation pass. The original skill directory was archived, not deleted.


## `.clawhub/origin.json`

```
{
  "version": 1,
  "registry": "https://clawhub.ai",
  "slug": "local-places",
  "installedVersion": "1.0.0",
  "installedAt": 1772275682049
}

```


## `SERVER_README.md`

````
# Local Places

This repo is a fusion of two pieces:

- A FastAPI server that exposes endpoints for searching and resolving places via the Google Maps Places API.
- A companion agent skill that explains how to use the API and can call it to find places efficiently.

Together, the skill and server let an agent turn natural-language place queries into structured results quickly.

## Run locally

```bash
# copy skill definition into the relevant folder (where the agent looks for it)
# then run the server

uv venv
uv pip install -e ".[dev]"
uv run --env-file .env uvicorn local_places.main:app --host 0.0.0.0 --reload
```

Open the API docs at http://127.0.0.1:8000/docs.

## Places API

Set the Google Places API key before running:

```bash
export GOOGLE_PLACES_API_KEY="your-key"
```

Endpoints:

- `POST /places/search` (free-text query + filters)
- `GET /places/{place_id}` (place details)
- `POST /locations/resolve` (resolve a user-provided location string)

Example search request:

```json
{
  "query": "italian restaurant",
  "filters": {
    "types": ["restaurant"],
    "open_now": true,
    "min_rating": 4.0,
    "price_levels": [1, 2]
  },
  "limit": 10
}
```

Notes:

- `filters.types` supports a single type (mapped to Google `includedType`).

Example search request (curl):

```bash
curl -X POST http://127.0.0.1:8000/places/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "italian restaurant",
    "location_bias": {
      "lat": 40.8065,
      "lng": -73.9719,
      "radius_m": 3000
    },
    "filters": {
      "types": ["restaurant"],
      "open_now": true,
      "min_rating": 4.0,
      "price_levels": [1, 2, 3]
    },
    "limit": 10
  }'
```

Example resolve request (curl):

```bash
curl -X POST http://127.0.0.1:8000/locations/resolve \
  -H "Content-Type: application/json" \
  -d '{
    "location_text": "Riverside Park, New York",
    "limit": 5
  }'
```

## Test

```bash
uv run pytest
```

## OpenAPI

Generate the OpenAPI schema:

```bash
uv run python scripts/generate_openapi.py
```

````


## `SKILL.md`

````
---
name: local-places
description: Search for places (restaurants, cafes, etc.) via Google Places API proxy on localhost.
homepage: https://github.com/Hyaxia/local_places
metadata: {"clawdbot":{"emoji":"📍","requires":{"bins":["uv"],"env":["GOOGLE_PLACES_API_KEY"]},"primaryEnv":"GOOGLE_PLACES_API_KEY"}}
---

# 📍 Local Places

*Find places, Go fast*

Search for nearby places using a local Google Places API proxy. Two-step flow: resolve location first, then search.

## Setup

```bash
cd {baseDir}
echo "GOOGLE_PLACES_API_KEY=your-key" > .env
uv venv && uv pip install -e ".[dev]"
uv run --env-file .env uvicorn local_places.main:app --host 127.0.0.1 --port 8000
```

Requires `GOOGLE_PLACES_API_KEY` in `.env` or environment.

## Quick Start

1. **Check server:** `curl http://127.0.0.1:8000/ping`

2. **Resolve location:**
```bash
curl -X POST http://127.0.0.1:8000/locations/resolve \
  -H "Content-Type: application/json" \
  -d '{"location_text": "Soho, London", "limit": 5}'
```

3. **Search places:**
```bash
curl -X POST http://127.0.0.1:8000/places/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "coffee shop",
    "location_bias": {"lat": 51.5137, "lng": -0.1366, "radius_m": 1000},
    "filters": {"open_now": true, "min_rating": 4.0},
    "limit": 10
  }'
```

4. **Get details:**
```bash
curl http://127.0.0.1:8000/places/{place_id}
```

## Conversation Flow

1. If user says "near me" or gives vague location → resolve it first
2. If multiple results → show numbered list, ask user to pick
3. Ask for preferences: type, open now, rating, price level
4. Search with `location_bias` from chosen location
5. Present results with name, rating, address, open status
6. Offer to fetch details or refine search

## Filter Constraints

- `filters.types`: exactly ONE type (e.g., "restaurant", "cafe", "gym")
- `filters.price_levels`: integers 0-4 (0=free, 4=very expensive)
- `filters.min_rating`: 0-5 in 0.5 increments
- `filters.open_now`: boolean
- `limit`: 1-20 for search, 1-10 for resolve
- `location_bias.radius_m`: must be > 0

## Response Format

```json
{
  "results": [
    {
      "place_id": "ChIJ...",
      "name": "Coffee Shop",
      "address": "123 Main St",
      "location": {"lat": 51.5, "lng": -0.1},
      "rating": 4.6,
      "price_level": 2,
      "types": ["cafe", "food"],
      "open_now": true
    }
  ],
  "next_page_token": "..." 
}
```

Use `next_page_token` as `page_token` in next request for more results.

````


## `_meta.json`

```
{
  "ownerId": "kn70pywhg0fyz996kpa8xj89s57yhv26",
  "slug": "local-places",
  "version": "1.0.0",
  "publishedAt": 1767545354524
}
```


## `pyproject.toml`

```
[project]
name = "my-api"
version = "0.1.0"
description = "FastAPI server"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110.0",
  "httpx>=0.27.0",
  "uvicorn[standard]>=0.29.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/local_places"]

[tool.pytest.ini_options]
addopts = "-q"
testpaths = ["tests"]

```


## `src/local_places/__init__.py`

```
__all__ = ["__version__"]
__version__ = "0.1.0"

```


## `src/local_places/google_places.py`

```
from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import HTTPException

from local_places.schemas import (
    LatLng,
    LocationResolveRequest,
    LocationResolveResponse,
    PlaceDetails,
    PlaceSummary,
    ResolvedLocation,
    SearchRequest,
    SearchResponse,
)

GOOGLE_PLACES_BASE_URL = os.getenv(
    "GOOGLE_PLACES_BASE_URL", "https://places.googleapis.com/v1"
)
logger = logging.getLogger("local_places.google_places")

_PRICE_LEVEL_TO_ENUM = {
    0: "PRICE_LEVEL_FREE",
    1: "PRICE_LEVEL_INEXPENSIVE",
    2: "PRICE_LEVEL_MODERATE",
    3: "PRICE_LEVEL_EXPENSIVE",
    4: "PRICE_LEVEL_VERY_EXPENSIVE",
}
_ENUM_TO_PRICE_LEVEL = {value: key for key, value in _PRICE_LEVEL_TO_ENUM.items()}

_SEARCH_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.rating,"
    "places.priceLevel,"
    "places.types,"
    "places.currentOpeningHours,"
    "nextPageToken"
)

_DETAILS_FIELD_MASK = (
    "id,"
    "displayName,"
    "formattedAddress,"
    "location,"
    "rating,"
    "priceLevel,"
    "types,"
    "regularOpeningHours,"
    "currentOpeningHours,"
    "nationalPhoneNumber,"
    "websiteUri"
)

_RESOLVE_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.types"
)


class _GoogleResponse:
    def __init__(self, response: httpx.Response):
        self.status_code = response.status_code
        self._response = response

    def json(self) -> dict[str, Any]:
        return self._response.json()

    @property
    def text(self) -> str:
        return self._response.text


def _api_headers(field_mask: str) -> dict[str, str]:
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GOOGLE_PLACES_API_KEY is not set.",
        )
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": field_mask,
    }


def _request(
    method: str, url: str, payload: dict[str, Any] | None, field_mask: str
) -> _GoogleResponse:
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers=_api_headers(field_mask),
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="Google Places API unavailable.") from exc

    return _GoogleResponse(response)


def _build_text_query(request: SearchRequest) -> str:
    keyword = request.filters.keyword if request.filters else None
    if keyword:
        return f"{request.query} {keyword}".strip()
    return request.query


def _build_search_body(request: SearchRequest) -> dict[str, Any]:
    body: dict[str, Any] = {
        "textQuery": _build_text_query(request),
        "pageSize": request.limit,
    }

    if request.page_token:
        body["pageToken"] = request.page_token

    if request.location_bias:
        body["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": request.location_bias.lat,
                    "longitude": request.location_bias.lng,
                },
                "radius": request.location_bias.radius_m,
            }
        }

    if request.filters:
        filters = request.filters
        if filters.types:
            body["includedType"] = filters.types[0]
        if filters.open_now is not None:
            body["openNow"] = filters.open_now
        if filters.min_rating is not None:
            body["minRating"] = filters.min_rating
        if filters.price_levels:
            body["priceLevels"] = [
                _PRICE_LEVEL_TO_ENUM[level] for level in filters.price_levels
            ]

    return body


def _parse_lat_lng(raw: dict[str, Any] | None) -> LatLng | None:
    if not raw:
        return None
    latitude = raw.get("latitude")
    longitude = raw.get("longitude")
    if latitude is None or longitude is None:
        return None
    return LatLng(lat=latitude, lng=longitude)


def _parse_display_name(raw: dict[str, Any] | None) -> str | None:
    if not raw:
        return None
    return raw.get("text")


def _parse_open_now(raw: dict[str, Any] | None) -> bool | None:
    if not raw:
        return None
    return raw.get("openNow")


def _parse_hours(raw: dict[str, Any] | None) -> list[str] | None:
    if not raw:
        return None
    return raw.get("weekdayDescriptions")


def _parse_price_level(raw: str | None) -> int | None:
    if not raw:
        return None
    return _ENUM_TO_PRICE_LEVEL.get(raw)


def search_places(request: SearchRequest) -> SearchResponse:
    url = f"{GOOGLE_PLACES_BASE_URL}/places:searchText"
    response = _request("POST", url, _build_search_body(request), _SEARCH_FIELD_MASK)

    if response.status_code >= 400:
        logger.error(
            "Google Places API error %s. response=%s",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail=f"Google Places API error ({response.status_code}).",
        )

    try:
        payload = response.json()
    except ValueError as exc:
        logger.error(
            "Google Places API returned invalid JSON. response=%s",
            response.text,
        )
        raise HTTPException(status_code=502, detail="Invalid Google response.") from exc

    places = payload.get("places", [])
    results = []
    for place in places:
        results.append(
            PlaceSummary(
                place_id=place.get("id", ""),
                name=_parse_display_name(place.get("displayName")),
                address=place.get("formattedAddress"),
                location=_parse_lat_lng(place.get("location")),
                rating=place.get("rating"),
                price_level=_parse_price_level(place.get("priceLevel")),
                types=place.get("types"),
                open_now=_parse_open_now(place.get("currentOpeningHours")),
            )
        )

    return SearchResponse(
        results=results,
        next_page_token=payload.get("nextPageToken"),
    )


def get_place_details(place_id: str) -> PlaceDetails:
    url = f"{GOOGLE_PLACES_BASE_URL}/places/{place_id}"
    response = _request("GET", url, None, _DETAILS_FIELD_MASK)

    if response.status_code >= 400:
        logger.error(
            "Google Places API error %s. response=%s",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail=f"Google Places API error ({response.status_code}).",
        )

    try:
        payload = response.json()
    except ValueError as exc:
        logger.error(
            "Google Places API returned invalid JSON. response=%s",
            response.text,
        )
        raise HTTPException(status_code=502, detail="Invalid Google response.") from exc

    return PlaceDetails(
        place_id=payload.get("id", place_id),
        name=_parse_display_name(payload.get("displayName")),
        address=payload.get("formattedAddress"),
        location=_parse_lat_lng(payload.get("location")),
        rating=payload.get("rating"),
        price_level=_parse_price_level(payload.get("priceLevel")),
        types=payload.get("types"),
        phone=payload.get("nationalPhoneNumber"),
        website=payload.get("websiteUri"),
        hours=_parse_hours(payload.get("regularOpeningHours")),
        open_now=_parse_open_now(payload.get("currentOpeningHours")),
    )


def resolve_locations(request: LocationResolveRequest) -> LocationResolveResponse:
    url = f"{GOOGLE_PLACES_BASE_URL}/places:searchText"
    body = {"textQuery": request.location_text, "pageSize": request.limit}
    response = _request("POST", url, body, _RESOLVE_FIELD_MASK)

    if response.status_code >= 400:
        logger.error(
            "Google Places API error %s. response=%s",
            response.status_code,
            response.text,
        )
        raise HTTPException(
            status_code=502,
            detail=f"Google Places API error ({response.status_code}).",
        )

    try:
        payload = response.json()
    except ValueError as exc:
        logger.error(
            "Google Places API returned invalid JSON. response=%s",
            response.text,
        )
        raise HTTPException(status_code=502, detail="Invalid Google response.") from exc

    places = payload.get("places", [])
    results = []
    for place in places:
        results.append(
            ResolvedLocation(
                place_id=place.get("id", ""),
                name=_parse_display_name(place.get("displayName")),
                address=place.get("formattedAddress"),
                location=_parse_lat_lng(place.get("location")),
                types=place.get("types"),
            )
        )

    return LocationResolveResponse(results=results)

```


## `src/local_places/main.py`

```
import logging
import os

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from local_places.google_places import get_place_details, resolve_locations, search_places
from local_places.schemas import (
    LocationResolveRequest,
    LocationResolveResponse,
    PlaceDetails,
    SearchRequest,
    SearchResponse,
)

app = FastAPI(
    title="My API",
    servers=[{"url": os.getenv("OPENAPI_SERVER_URL", "http://maxims-macbook-air:8000")}],
)
logger = logging.getLogger("local_places.validation")


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "pong"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error(
        "Validation error on %s %s. body=%s errors=%s",
        request.method,
        request.url.path,
        exc.body,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.post("/places/search", response_model=SearchResponse)
def places_search(request: SearchRequest) -> SearchResponse:
    return search_places(request)


@app.get("/places/{place_id}", response_model=PlaceDetails)
def places_details(place_id: str) -> PlaceDetails:
    return get_place_details(place_id)


@app.post("/locations/resolve", response_model=LocationResolveResponse)
def locations_resolve(request: LocationResolveRequest) -> LocationResolveResponse:
    return resolve_locations(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("local_places.main:app", host="0.0.0.0", port=8000)

```


## `src/local_places/schemas.py`

```
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class LatLng(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class LocationBias(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_m: float = Field(gt=0)


class Filters(BaseModel):
    types: list[str] | None = None
    open_now: bool | None = None
    min_rating: float | None = Field(default=None, ge=0, le=5)
    price_levels: list[int] | None = None
    keyword: str | None = Field(default=None, min_length=1)

    @field_validator("types")
    @classmethod
    def validate_types(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return value
        if len(value) > 1:
            raise ValueError(
                "Only one type is supported. Use query/keyword for additional filtering."
            )
        return value

    @field_validator("price_levels")
    @classmethod
    def validate_price_levels(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        invalid = [level for level in value if level not in range(0, 5)]
        if invalid:
            raise ValueError("price_levels must be integers between 0 and 4.")
        return value

    @field_validator("min_rating")
    @classmethod
    def validate_min_rating(cls, value: float | None) -> float | None:
        if value is None:
            return value
        if (value * 2) % 1 != 0:
            raise ValueError("min_rating must be in 0.5 increments.")
        return value


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    location_bias: LocationBias | None = None
    filters: Filters | None = None
    limit: int = Field(default=10, ge=1, le=20)
    page_token: str | None = None


class PlaceSummary(BaseModel):
    place_id: str
    name: str | None = None
    address: str | None = None
    location: LatLng | None = None
    rating: float | None = None
    price_level: int | None = None
    types: list[str] | None = None
    open_now: bool | None = None


class SearchResponse(BaseModel):
    results: list[PlaceSummary]
    next_page_token: str | None = None


class LocationResolveRequest(BaseModel):
    location_text: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=10)


class ResolvedLocation(BaseModel):
    place_id: str
    name: str | None = None
    address: str | None = None
    location: LatLng | None = None
    types: list[str] | None = None


class LocationResolveResponse(BaseModel):
    results: list[ResolvedLocation]


class PlaceDetails(BaseModel):
    place_id: str
    name: str | None = None
    address: str | None = None
    location: LatLng | None = None
    rating: float | None = None
    price_level: int | None = None
    types: list[str] | None = None
    phone: str | None = None
    website: str | None = None
    hours: list[str] | None = None
    open_now: bool | None = None

```
