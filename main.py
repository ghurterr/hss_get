# main.py (v4.1)
# A comprehensive, data-first request logging service for Python/FastAPI.
# Corrected to remove legacy Deno artifact check.
# Author: Winston, The Architect (BMad-Method)

import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

def analyze_user_agent(user_agent_string: str | None) -> dict:
    """
    Performs heuristic analysis on the User-Agent header.
    Provides simple boolean flags and preserves the raw user agent.
    """
    ua = (user_agent_string or "").lower()
    result = {
        "raw": user_agent_string or "[No User-Agent Header]",
        "heuristics": {
            "isBrowser": False,
            "isKnownBot": False,
            "isKnownScript": False,
        },
    }

    if not ua:
        return result

    # Check for known scripts/tools (Deno check removed)
    if ua.startswith("curl/") or "okhttp" in ua:
        result["heuristics"]["isKnownScript"] = True
        return result
    
    # Check for known bots
    if "bot" in ua or "spider" in ua or "crawler" in ua:
        result["heuristics"]["isKnownBot"] = True
        return result

    # Check for browsers
    if "mozilla" in ua or "gecko" in ua or "webkit" in ua:
        result["heuristics"]["isBrowser"] = True
        return result
      
    return result

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def log_request_handler(request: Request, full_path: str):
    """
    This single handler captures all requests to any path.
    """
    # --- Information Aggregation ---
    
    try:
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
    except Exception:
        body_str = "[Error reading or decoding body]"

    headers_dict = dict(request.headers)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "client": {
            "ip": headers_dict.get("x-forwarded-for"),
            "geo": {
                "country": headers_dict.get("x-country-code"),
                "region": headers_dict.get("x-region"),
                "city": headers_dict.get("x-city"),
            }
        },
        "request": {
            "url": str(request.url),
            "method": request.method,
            "headers": headers_dict,
            "body": body_str or "[Empty Body]",
        },
        "userAgentAnalysis": analyze_user_agent(headers_dict.get("user-agent")),
    }

    # --- Structured Logging ---
    print(json.dumps(log_entry, indent=2))
    
    # --- Client Response ---
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Log Recorded</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 5em; }
        </style>
    </head>
    <body>
        <h1>Log Recorded</h1>
        <p>Your request has been successfully logged.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
