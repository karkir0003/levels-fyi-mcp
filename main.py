from fastmcp import FastMCP, Context
import random
from utils import get_company_slug, get_location_details, get_role_slug,ResponseUtil, preprocess_levels,format_offer_date
from fake_useragent import UserAgent
import requests

# 1. Initialize the server with a name
mcp = FastMCP("LevelsFyi")
ua = UserAgent()

# Tool 1: Simple Math (Shows how MCP handles basic int inputs/outputs)
@mcp.tool()
def calculate_addition(a: int, b: int) -> int:
    """Add two numbers together. Use this when the user asks for addition."""
    print(f"Server log: Calculating {a} + {b}") # Logs show up in your terminal!
    return a + b

# Tool 2: Mock API (Shows how MCP handles strings and dynamic responses)
@mcp.tool()
def get_mock_weather(city: str) -> str:
    """Get the current mock weather for a given city."""
    print(f"Server log: Fetching weather for {city}")
    conditions = ["Sunny", "Pouring Rain", "Overcast", "Snowing"]
    temp = random.randint(30, 95)
    return f"It is currently {temp}°F and {random.choice(conditions)} in {city}."

# Tool 3: Default Arguments (Shows how the LLM knows what is optional)
@mcp.tool()
def generate_username(base_name: str, add_numbers: bool = True) -> str:
    """Generate a cool username based on a name."""
    print(f"Server log: Generating username for {base_name} (Numbers: {add_numbers})")
    username = base_name.lower().replace(" ", "_")
    if add_numbers:
        username += str(random.randint(100, 999))
    return f"Your new username is: @{username}"

@mcp.tool()
def get_level_mapping(company_name: str, role: str = "Software Engineer", ctx: Context) -> dict:
    """
    REQUIRED: Call this tool FIRST to find the company's specific level names 
    (e.g., '63', 'L5', 'E4') versus the industry 'Standard' ladder.
    'role' must be the full name: 'Software Engineer', 'Product Manager', etc.
    """
    company_slug = get_company_slug(company_name)
    await ctx.info(f"Server log: Mapping levels for {company_slug}")
    
    url = "https://api.levels.fyi/v1/levels"
    params = {
        "role": role,
        "countryId": 254, # Assuming US based companies as the standardized level
        "companies[0]": company_slug,
    }
    
    res = requests.get(url, params=params, headers={"User-Agent": ua.random})
    if res.status_code == 200:
        util = ResponseUtil()
        parsed_data = util.parse(res.json())
        levels = preprocess_levels(parsed_data)
        return {"company": company_slug, "role": role, "levels": levels}
    await ctx.error(f"Failed to fetch levels for {company_slug}. Status: {res.status_code}")
    return {"error": "Could not fetch level mapping."}

# Get Recent Offers Tool
@mcp.tool()
def get_recent_offers(company_name: str, role: str, level: str, location: str = None, ctx: Context) -> dict:
    """
    Fetch the most recent specific salary offers for a given role to gauge current market trends.
    Example: company_name='Amazon', role='Software Engineer', level='SDE II'
    """
    company_slug = get_company_slug(company_name)
    job_family = get_role_slug(role)
    await ctx.info(f"Fetching offers: {company_slug} | {level} | {location or 'Global'}")
    
    url = "https://api.levels.fyi/v3/salary/search"
    params = {
        "companySlug": company_slug,
        "jobFamilySlug": job_family,
        "level": level,
        "limit": 10, # Hard limit on amount of compensation data
        "sortBy": "offer_date",
        "sortOrder": "DESC",
        "currency": "USD"
    }

    # Inject the DMA/City/Country IDs if a location was provided
    if location:
        loc_details = get_location_details(location)
        await ctx.debug(f"Location '{location}' resolved to: {loc_details}")
        params.update(loc_details)
    
    headers = {"User-Agent": ua.random}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        util = ResponseUtil()
        parsed_data = util.parse(response.json())
        rows = parsed_data.get("rows", [])
        
        clean_offers = []
        for r in rows:
            clean_offers.append({
                "offer_date": format_offer_date(r.get("offerDate")),
                "total_compensation": r.get("totalCompensation"),
                "base_salary": r.get("baseSalary"),
                "stock_grant": r.get("avgAnnualStockGrantValue"),
                "years_of_experience": r.get("yearsOfExperience"),
                "location": r.get("location")
            })
            
        return {
            "resolved_company": company_slug,
            "query": f"{company_name} | {level}",
            "offers": clean_offers
        }
    else:
        await ctx.error(f"Failed to fetch offers: {company_slug} | {level} | {location or 'Global'} - Status: {response.status_code}")
        return {"error": f"API request failed with status {response.status_code}"}

if __name__ == "__main__":
    mcp.run()