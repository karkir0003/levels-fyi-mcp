from fastmcp import FastMCP, Context
from utils import (
    format_offer_date,
    get_company_slug,
    get_location_details,
    get_role_slug,
    parse_levels_api_response,
    preprocess_levels,
)
from fake_useragent import UserAgent
import requests

# 1. Initialize the server with a name
mcp = FastMCP("LevelsFyi")
ua = UserAgent()

@mcp.tool()
async def get_level_mapping(company_name: str, role: str = "Software Engineer", ctx: Context=None) -> dict:
    """
    REQUIRED: Call this tool FIRST to find the company's specific level names 
    (e.g., '63', 'L5', 'E4') versus the industry 'Standard' ladder.
    'role' must be the full name: 'Software Engineer', 'Product Manager', etc.
    """
    company_slug = get_company_slug(company_name)
    if ctx:
        await ctx.info(f"Server log: Mapping levels for {company_slug}")
    
    url = "https://api.levels.fyi/v1/levels"
    params = {
        "role": role,
        "countryId": 254, # Assuming US based companies as the standardized level
        "companies[0]": company_slug,
    }
    
    res = requests.get(url, params=params, headers={"User-Agent": ua.random})
    if res.status_code == 200:
        parsed_data = parse_levels_api_response(res.json())
        levels = preprocess_levels(parsed_data)
        return {"company": company_slug, "role": role, "levels": levels}
    if ctx:
        await ctx.error(f"Failed to fetch levels for {company_slug}. Status: {res.status_code}")
    return {"error": "Could not fetch level mapping."}

# Get Recent Offers Tool
@mcp.tool()
async def get_recent_offers(company_name: str, role: str, level: str, location: str = None, ctx: Context=None) -> dict:
    """
    Fetch the most recent specific salary offers for a given role to gauge current market trends.
    Example: company_name='Amazon', role='Software Engineer', level='SDE II'
    """
    company_slug = get_company_slug(company_name)
    job_family = get_role_slug(role)
    if ctx:
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
        if ctx:
            await ctx.debug(f"Location '{location}' resolved to: {loc_details}")
        params.update(loc_details)
    
    headers = {"User-Agent": ua.random}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        parsed_data = parse_levels_api_response(response.json())
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
        if ctx:
            await ctx.error(f"Failed to fetch offers: {company_slug} | {level} | {location or 'Global'} - Status: {response.status_code}")
        return {"error": f"API request failed with status {response.status_code}"}

if __name__ == "__main__":
    mcp.run()