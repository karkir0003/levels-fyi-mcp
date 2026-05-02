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
    """Hits the Levels autocomplete API to resolve a human name to a slug."""
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