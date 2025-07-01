from fastmcp import FastMCP

mcp = FastMCP("testserver", json_response=True)

@mcp.tool
def greet() -> str:
    """ 오늘 날씨 조회  """

    return f"[지역: 서울][온도: 25도] 맑음"

@mcp.tool
def hello_world() -> str:
    """ Prints hello world """
    return "hello world"

if __name__ == "__main__":
    mcp.run(host="127.0.0.1", port=3000, transport='http')