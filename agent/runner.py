import os
from dotenv import load_dotenv
load_dotenv()

import httpx
from agents import Agent, Runner
from agents.tracing import set_tracing_disabled
set_tracing_disabled(True)

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")


async def tavily_search(query: str) -> str:
    """Search Tavily directly via HTTP — no MCP needed."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
            },
            timeout=30,
        )
        data = response.json()
        results = data.get("results", [])
        return "\n\n".join([
            f"**{r.get('title', '')}**\n{r.get('content', '')}"
            for r in results
        ])


ANALYST_PROMPT = """
You are an insurance analysis specialist. Compare all quotes
and produce a clear ranked comparison table with recommendation.
Use two sections: Traditional Insurers and AI-Powered Insurers.
Format as markdown with ranked tables and a top recommendation.
Add a disclaimer that these are estimates.
IMPORTANT: Use only basic ASCII characters in your response.
Do not use em dashes (use -- instead), curly quotes (use straight quotes),
or any special Unicode characters. Use only standard keyboard characters.
"""


async def run_insurance_agent(member) -> str:
    vehicle = member.vehicles[0] if member.vehicles else None

    profile_text = (
        f"Driver: {member.name}, {member.age}yo {member.gender}, "
        f"{member.marital_status}, {member.city} UT {member.zip_code}\n"
        f"Driving record: {member.accidents} accidents, "
        f"{member.violations} violations in last 5 years\n"
        f"Licensed: {member.license_years} years\n"
    )

    if vehicle:
        profile_text += (
            f"Vehicle: {vehicle.year} {vehicle.make} {vehicle.model}\n"
            f"Mileage: {vehicle.annual_mileage} miles/year\n"
            f"Use: {vehicle.primary_use}\n"
        )

    profile_text += (
        f"Coverage: {member.coverage_type}, "
        f"${member.deductible} deductible, "
        f"{member.liability_limit} liability\n"
    )

    # Search for rates directly via Tavily API
    queries = [
        f"Utah car insurance rates 2024 Geico Progressive State Farm Allstate comparison",
        f"Bear River Mutual Utah car insurance rates 2024 review",
        f"Lemonade Root Insurance Clearcover Metromile Utah rates 2024",
        f"best car insurance Utah {member.zip_code} full coverage monthly cost",
    ]

    search_results = []
    for query in queries:
        result = await tavily_search(query)
        search_results.append(result)

    combined_research = "\n\n---\n\n".join(search_results)

    # Analyze with GPT
    analyst = Agent(
        name="Analyst",
        instructions=ANALYST_PROMPT,
        model="gpt-4o-mini",
    )

    analyst_result = await Runner.run(
        analyst,
        input=(
            f"Driver profile:\n{profile_text}\n\n"
            f"Research data from comparison sites:\n{combined_research}\n\n"
            "Produce a final ranked comparison table and recommendation "
            "for both traditional and AI-powered insurers. "
            "Include Bear River Mutual, Costco CONNECT, Lemonade, Root, "
            "Clearcover and Metromile."
        ),
    )

    # Remove non-ASCII characters that cause encoding errors
    output = analyst_result.final_output
    output = output.encode("utf-8", "ignore").decode("utf-8")
    return output
