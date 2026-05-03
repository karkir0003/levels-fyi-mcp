from datetime import datetime


def get_role_slug(role_name: str) -> str:
    """
    Converts 'Software Engineer' to 'software-engineer'.

    Best effort conversion
    """
    return role_name.lower().strip().replace(" ", "-")


def format_offer_date(date_str: str) -> str:
    """
    Sanitizes JavaScript Date.toString() outputs into standard ISO 8601 datetime strings.
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