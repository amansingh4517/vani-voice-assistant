"""Music playback (YouTube Music, YouTube, Apple Music, and Spotify)."""

import re
import urllib.parse
import urllib.request

from vani.tools.core import error, quote, run, run_script, tool

_COMMANDS = {"play": "play", "pause": "pause", "play_pause": "playpause",
             "toggle": "playpause", "next": "next track", "skip": "next track",
             "previous": "previous track", "back": "previous track"}


def _player(app: str) -> str:
    return "Spotify" if app.lower().strip() == "spotify" else "Music"


def _find_youtube_video(query: str) -> tuple[str | None, str | None]:
    """Find the top YouTube video ID and title for a query."""
    try:
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=4) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        m = re.search(r'"videoRenderer":\{"videoId":"([^"]+)".*?"title":\{"runs":\[\{"text":"([^"]+)"\}', html)
        if m:
            return m.group(1), m.group(2)

        ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if ids:
            return ids[0], None
    except Exception:
        pass
    return None, None


@tool
def play_song(query: str, platform: str = "youtube_music") -> str:
    """Play a song or music track directly. Plays on YouTube Music by default unless the user explicitly requests YouTube ('youtube').

    Args:
        query: Name of the song, artist, or music track (e.g. 'Starboy', 'Bohemian Rhapsody').
        platform: 'youtube_music' (default) to play on YouTube Music, or 'youtube' to play on standard YouTube.
    """
    is_yt = platform.lower().strip() in ("youtube", "yt")
    service_name = "YouTube" if is_yt else "YouTube Music"

    video_id, title = _find_youtube_video(query)

    if video_id:
        if is_yt:
            url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            url = f"https://music.youtube.com/watch?v={video_id}"

        run(["open", url])
        label = f"'{title}'" if title else f"'{query}'"
        return f"Playing {label} on {service_name}."
    else:
        # Fallback to direct search URL if video ID could not be resolved
        if is_yt:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
        else:
            url = f"https://music.youtube.com/search?q={urllib.parse.quote_plus(query)}"

        run(["open", url])
        return f"Opened {service_name} for '{query}'."


@tool
def music_control(action: str, app: str = "Music") -> str:
    """Control music playback. action: play, pause, play_pause, next, previous. app: 'Music' (Apple Music) or 'Spotify'."""
    player = _player(app)
    command = _COMMANDS.get(action.lower().strip())
    if not command:
        return error("action must be play, pause, play_pause, next or previous.")
    return run_script(f'tell application "{player}" to {command}').message(f"{player}: {action}.")


@tool
def get_now_playing(app: str = "Music") -> str:
    """Get the song that is currently playing in Apple Music or Spotify."""
    player = _player(app)
    script = (f'if application "{player}" is running then\n'
              f'tell application "{player}"\n'
              'if player state is playing then\n'
              'return (name of current track) & " by " & (artist of current track)\n'
              'else\nreturn "Nothing is playing."\nend if\nend tell\n'
              f'else\nreturn "{player} is not running."\nend if')
    return run_script(script).message()


@tool
def play_song_in_music(query: str) -> str:
    """Play a song or artist from the Apple Music library by name."""
    q = quote(query)
    script = ('tell application "Music"\n'
              f'set found to (every track of library playlist 1 whose name contains "{q}" '
              f'or artist contains "{q}" or album contains "{q}")\n'
              'if (count of found) is 0 then return "NONE"\n'
              'play item 1 of found\n'
              'return (name of item 1 of found) & " by " & (artist of item 1 of found)\n'
              'end tell')
    res = run_script(script, timeout=60)
    if not res.ok:
        return res.message()
    if res.output == "NONE":
        return f"No match for '{query}' in the library."
    return f"Playing {res.output}."
