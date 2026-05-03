from fastmcp import FastMCP, Context
from src.companies import get_company_slug
from src.levels import fetch_company_level_mapping
from src.locations import get_location_details
from src.processors import get_role_slug
from src.salary import fetch_recent_offers

# 1. Initialize the server with a name
mcp = FastMCP("LevelsFyi")


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

    levels, status = fetch_company_level_mapping(company_slug, role)
    if levels is not None:
        return {"company": company_slug, "role": role, "levels": levels}
    if ctx:
        await ctx.error(f"Failed to fetch levels for {company_slug}. Status: {status}")
    return {"error": "Could not fetch level mapping."}


@mcp.tool()
async def get_recent_offers(company_name: str, role: str, level: str, location: str = None, ctx: Context=None) -> dict:
    """
    Fetch the most recent specific salary offers for a given role to gauge current market trends.
    Example: company_name='Amazon', role='Software Engineer', level='SDE II'

    Location must be a single city name (e.g., 'Seattle'). If the city is ambiguous, the most major tech hub will be chosen by default
    """
    company_slug = get_company_slug(company_name)
    job_family = get_role_slug(role)
    if ctx:
        await ctx.info(f"Fetching offers: {company_slug} | {level} | {location or 'Global'}")

    location_filters = None
    if location:
        location_filters = get_location_details(location)
        if ctx:
            await ctx.debug(f"Location '{location}' resolved to: {location_filters}")

    offers, status = fetch_recent_offers(
        company_slug,
        job_family,
        level,
        location_filters=location_filters,
    )

    if offers is not None:
        return {
            "resolved_company": company_slug,
            "query": f"{company_name} | {level}",
            "offers": offers,
        }

    if ctx:
        await ctx.error(
            f"Failed to fetch offers: {company_slug} | {level} | {location or 'Global'} - Status: {status}"
        )
    return {"error": f"API request failed with status {status}"}


if __name__ == "__main__":
    mcp.run()
