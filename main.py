from fastmcp import FastMCP
import random

# 1. Initialize the server with a name
mcp = FastMCP("MyPlayground")

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

if __name__ == "__main__":
    mcp.run()