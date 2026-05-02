import requests
import json
import zlib
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from base64 import b64encode, b64decode
from fake_useragent import UserAgent
from datetime import datetime

ua = UserAgent()

class ResponseUtil:
    """
    Utility for parsing and decrypting the response from the Levels FYI API. 

    NOTE: The API response payload is encrypted and compressed. This decryption is based on the rendered JS code

    Source: https://stackoverflow.com/questions/76496884/how-levels-fyi-is-encoding-the-api-response
    """
    def __init__(self):
        self.key = "levelstothemoon!!"
        self.n = 16

    def parse(self, t):
        if "payload" not in t:
            return t
        r = t["payload"]
        a = MD5.new(self.key.encode()).digest()
        a_base64 = b64encode(a)[: self.n]
        cipher = AES.new(a_base64, AES.MODE_ECB)
        decrypted_data = cipher.decrypt(b64decode(r))
        decompressed_data = zlib.decompress(decrypted_data)
        return json.loads(decompressed_data.decode())

def get_role_slug(role_name: str) -> str:
    """
    Converts 'Software Engineer' to 'software-engineer'.

    Best effort conversion
    """
    return role_name.lower().strip().replace(" ", "-")


def format_offer_date(date_str: str) -> str:
    """
    Sanitizes JavaScript Date.toString() outputs into standard ISO 8601 strings.
    This prevents token bloat and makes it easier for the LLM to process timelines.
    
    Example: 
        Input:  "Sat May 02 2026 10:27:36 GMT+0000 (Coordinated Universal Time)"
        Output: "2026-05-02"
    """
    if not date_str:
        return "Unknown"
    
    try:
        # Slice off the timezone garbage and parse the standardized JS date string
        clean_time = str(date_str).split(" GMT")[0]
        parsed = datetime.strptime(clean_time, "%a %b %d %Y %H:%M:%S")
        return parsed.strftime("%Y-%m-%d")
        
    except Exception as e:
        print(f"Server log: Date parsing failed for {date_str} - {e}")
        return str(date_str)

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
            data = res.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("slug")
    except Exception as e:
        print(f"Server log: Error resolving slug: {e}")
        
    return search_text.lower().replace(" ", "-").replace("'", "").replace(".", "")

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
        
        data = res.json()
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
            
            # Parent-Aware Logic: If it's a city, prioritize the market bubble (DMA)
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