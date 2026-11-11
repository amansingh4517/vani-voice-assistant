"""Browser and internet lookups."""

import urllib.parse
import urllib.request
import re

from vani.tools.core import error, run, tool

_SEARCH_ENGINES = {
    "google": "https://www.google.com/search?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
    "bing": "https://www.bing.com/search?q=",
    "youtube": "https://www.youtube.com/results?search_query=",
    "maps": "https://www.google.com/maps/search/",
    "wikipedia": "https://en.wikipedia.org/w/index.php?search=",
    "github": "https://github.com/search?q=",
}


@tool
def open_url(url: str) -> str:
    """Open a website in the default browser. Adds https:// if missing."""
    url = url.strip()
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url
    return run(["open", url]).message(f"Opened {url}.")


@tool
def web_search(query: str, engine: str = "google") -> str:
    """Search the web in the browser. engine can be: google, duckduckgo, bing, youtube, maps, wikipedia, github."""
    base = _SEARCH_ENGINES.get(engine.lower().strip(), _SEARCH_ENGINES["google"])
    res = run(["open", base + urllib.parse.quote_plus(query)])
    return res.message(f"Searching {engine} for '{query}'.")


@tool
def search_on_youtube(query: str) -> str:
    """Search YouTube and open the search results page. Use this ONLY when the user asks to search YouTube or browse videos/tutorials. To play music or songs, use play_song instead."""
    res = run(["open", _SEARCH_ENGINES["youtube"] + urllib.parse.quote_plus(query)])
    return res.message(f"Showing YouTube results for '{query}'.")


@tool
def get_weather(city: str = "") -> str:
    """Get the current weather for a city. Leave city empty to use the current location."""
    fmt = "%l:+%C,+%t+(feels+like+%f),+humidity+%h,+wind+%w"
    url = f"https://wttr.in/{urllib.parse.quote(city.strip())}?format={fmt}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception as e:
        return error(f"could not fetch weather ({e}).")


@tool
def play_on_youtube(query: str) -> str:
    """Play a specific song or video directly on YouTube."""
    try:
        # Automatically searches and opens the top matching video
        pywhatkit.playonyt(query)
        
        # Since pywhatkit opens the browser itself, we just return a success message
        # (Assuming your 'run' or a dummy object handles the response text)
        return run([]).message(f"Playing '{query}' on YouTube.")
    
    except Exception as e:
        return error(f"Could not play video on YouTube ({e}).")
