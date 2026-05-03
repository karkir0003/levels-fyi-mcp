import requests

from .api_client import parse_levels_api_response, ua

LEVEL_MAPPING_URL = "https://api.levels.fyi/v1/levels"
LEVEL_MAPPING_US_COUNTRY_ID = 254  # Assuming US-based companies as the standardized ladder


def preprocess_levels(decrypted_data: dict) -> list:
    """
    Extracts only the level titles for the first company in the response.
    Returns a simple list of objects that map rank to titles.
    """
    companies = decrypted_data.get("companies", [])
    if not companies:
        return []

    # Just take the first company since that's the best result (the one we requested)
    target_co = companies[0]
    
    # Return a clean list of just the rank and the title strings
    return [
        {
            "rank": entry.get("order"),
            "titles": entry.get("titles")
        } for entry in target_co.get("levels", [])
    ]


def level_mapping_params(company_slug: str, role: str) -> dict:
    """Query params for the company / role ladder API."""
    return {
        "role": role,
        "countryId": LEVEL_MAPPING_US_COUNTRY_ID,
        "companies[0]": company_slug,
    }


def fetch_company_level_mapping(company_slug: str, role: str = "Software Engineer") -> tuple[list | None, int]:
    """
    Fetch and normalize level titles for a company + role.

    Returns ``(levels, status_code)``. ``levels`` is ``None`` when the HTTP call fails or
    decoding yields nothing useful.
    """
    res = requests.get(
        LEVEL_MAPPING_URL,
        params=level_mapping_params(company_slug, role),
        headers={"User-Agent": ua.random},
        timeout=30,
    )
    if res.status_code != 200:
        return None, res.status_code
    parsed = parse_levels_api_response(res.json())
    if not isinstance(parsed, dict):
        return None, res.status_code
    levels = preprocess_levels(parsed)
    return levels, res.status_code