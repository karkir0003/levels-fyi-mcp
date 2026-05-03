import requests

from .api_client import parse_levels_api_response, ua
from .processors import format_offer_date

SALARY_SEARCH_URL = "https://api.levels.fyi/v3/salary/search"
RECENT_OFFERS_LIMIT = 10


def salary_search_params(
    company_slug: str,
    job_family_slug: str,
    level: str,
    *,
    location_filters: dict | None = None,
) -> dict:
    """Query params for the recent salary / offer search API."""
    params = {
        "companySlug": company_slug,
        "jobFamilySlug": job_family_slug,
        "level": level,
        "limit": RECENT_OFFERS_LIMIT,
        "sortBy": "offer_date",
        "sortOrder": "DESC",
        "currency": "USD",
    }
    if location_filters:
        params.update(location_filters)
    return params


def _normalize_offer_row(row: dict) -> dict:
    return {
        "offer_date": format_offer_date(row.get("offerDate")),
        "total_compensation": row.get("totalCompensation"),
        "base_salary": row.get("baseSalary"),
        "stock_grant": row.get("avgAnnualStockGrantValue"),
        "years_of_experience": row.get("yearsOfExperience"),
        "location": row.get("location"),
    }


def fetch_recent_offers(
    company_slug: str,
    job_family_slug: str,
    level: str,
    *,
    location_filters: dict | None = None,
) -> tuple[list[dict] | None, int]:
    """
    Fetch recent structured offer rows.

    Returns ``(offers, status_code)``. ``offers`` is ``None`` when the HTTP call fails or the
    payload is not a mapping (same contract as ``fetch_company_level_mapping``).
    """
    res = requests.get(
        SALARY_SEARCH_URL,
        params=salary_search_params(
            company_slug,
            job_family_slug,
            level,
            location_filters=location_filters,
        ),
        headers={"User-Agent": ua.random},
        timeout=30,
    )
    if res.status_code != 200:
        return None, res.status_code
    parsed = parse_levels_api_response(res.json())
    if not isinstance(parsed, dict):
        return None, res.status_code
    rows = parsed.get("rows", []) or []
    clean_offers = [_normalize_offer_row(r) for r in rows if isinstance(r, dict)]
    return clean_offers, res.status_code
