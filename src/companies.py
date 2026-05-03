import requests

from .api_client import parse_levels_api_response, ua

def get_company_slug(search_text: str) -> str:
    """
    Hits the Levels entity search API to resolve a company name to a slug.
    """
    url = "https://api.levels.fyi/v2/search/entity"
    params = {"searchText": search_text}
    headers = {"User-Agent": ua.random}
    
    try:
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            data = parse_levels_api_response(res.json())
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("slug")
    except Exception as e:
        print(f"Server log: Error resolving slug: {e}")
        
    return search_text.lower().replace(" ", "-").replace("'", "").replace(".", "")