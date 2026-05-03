import requests

from .api_client import parse_levels_api_response, ua

def get_location_details(search_text: str) -> dict:
    """
    Find location details for a given search query
    Prioritizes DMAs (Market Areas) by checking both direct hits and city parents.

    Example: 
        Input:  "NYC"
        Output: {"cityIds[]": 10182}
    """
    if not search_text: 
        return {}
    
    url = "https://api.levels.fyi/v2/search/entity"
    params = {
        "searchText": search_text,
        "searchEntityTypes[0]": "city",
        "searchEntityTypes[1]": "dma",
        "searchEntityTypes[2]": "country"
    }
    
    try:
        res = requests.get(url, params=params, headers={"User-Agent": ua.random})
        if res.status_code != 200: 
            return {}
        
        data = parse_levels_api_response(res.json())
        
        if not isinstance(data, list): 
            return {}

        # The Allowlist: Only process these geographic types
        VALID_GEO_TYPES = {"dma", "city", "country"}

        for item in data:
            item_type = item.get("type")
            
            # Ignore anything not in our allowlist (e.g. companies)
            if item_type not in VALID_GEO_TYPES:
                continue

            # Market-First Logic: If we hit a DMA directly, we're done.
            if item_type == "dma":
                return {"dmaIds[]": item.get("id")}
            
            # Parent-Aware Logic: If it's a city, prioritize the market area (DMA)
            if item_type == "city":
                parent = item.get("parent")
                if parent and parent.get("type") == "dma":
                    print(f"Server log: Mapping city '{item.get('displayValue')}' to Market '{parent.get('displayValue')}'")
                    return {"dmaIds[]": parent.get("id")}
                # If no DMA parent exists, fall back to the specific city
                return {"cityIds[]": item.get("id")}

            # 4. Global Fallback: If it's a country (e.g. 'Canada')
            if item_type == "country":
                return {"countryIds[]": item.get("id")}
                
    except Exception as e:
        print(f"Server log: Location resolution error - {e}")
        
    return {}