import re

_SMALL_CAPS = str.maketrans({
    "a":"ᴀ", "b":"ʙ", "c":"ᴄ", "d":"ᴅ", "e":"ᴇ", "f":"ꜰ",
    "g":"ɢ", "h":"ʜ", "i":"ɪ", "j":"ᴊ", "k":"ᴋ", "l":"ʟ",
    "m":"ᴍ", "n":"ɴ", "o":"ᴏ", "p":"ᴘ", "q":"ǫ", "r":"ʀ",
    "s":"ꜱ", "t":"ᴛ", "u":"ᴜ", "v":"ᴠ", "w":"ᴡ", "x":"x",
    "y":"ʏ", "z":"ᴢ",
    "A":"ᴀ", "B":"ʙ", "C":"ᴄ", "D":"ᴅ", "E":"ᴇ", "F":"ꜰ",
    "G":"ɢ", "H":"ʜ", "I":"ɪ", "J":"ᴊ", "K":"ᴋ", "L":"ʟ",
    "M":"ᴍ", "N":"ɴ", "O":"ᴏ", "P":"ᴘ", "Q":"ǫ", "R":"ʀ",
    "S":"ꜱ", "T":"ᴛ", "U":"ᴜ", "V":"ᴠ", "W":"ᴡ", "X":"x",
    "Y":"ʏ", "Z":"ᴢ",
})
_PROTECTED = re.compile(r"(<[^>]*>|\{[^{}]*\}|https?://\S+|(?:t\.me|telegram\.me)/\S+|@[A-Za-z0-9_]+|/[A-Za-z0-9_]+)")

def to_small_caps(value):
    """Convert user-facing Latin text while preserving markup and identifiers."""
    if not isinstance(value, str):
        return value
    parts = _PROTECTED.split(value)
    return "".join(part if _PROTECTED.fullmatch(part or "") else part.translate(_SMALL_CAPS) for part in parts)
