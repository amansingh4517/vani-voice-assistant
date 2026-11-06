"""Music playback (Apple Music and Spotify)."""

from .core import error, quote, run_script, tool

_COMMANDS = {"play": "play", "pause": "pause", "play_pause": "playpause",
             "toggle": "playpause", "next": "next track", "skip": "next track",
             "previous": "previous track", "back": "previous track"}


def _player(app: str) -> str:
    return "Spotify" if app.lower().strip() == "spotify" else "Music"


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
