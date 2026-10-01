"""
Builds the HTML caption for auto-posted episodes.

Template (fixed, parse_mode=HTML):

<blockquote><b>{title en | title native}</b></blockquote>
<b>◇──◇──◇──◇──◇──◇──◇──◇</b>
<b>✦</b> <i>Genres:</i> <code>{genres}</code>
<b>✦</b> <i>Episode:</i> <code>{episode}</code>
<b>✦</b> <i>Audio:</i> <code>{audio}</code>
<b>✦</b> <i>Subtitle:</i> <code>{subtitle}</code>
<b>◇──◇──◇──◇──◇──◇──◇──◇</b>
<blockquote expandable><b>‣ ᴏᴠᴇʀᴠɪᴇᴡ :</b> <i>{overview}</i><a href="{link}">𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈</a></blockquote>

Telegram photo captions cap out at 1024 characters, so the overview is
trimmed twice: first to ~150 words, then (if still too long once the rest
of the template is accounted for) by characters, to guarantee the whole
caption fits.
"""

TELEGRAM_CAPTION_LIMIT = 1024
OVERVIEW_WORD_LIMIT = 150

LANG_NAMES = {
    "eng": "English", "jpn": "Japanese", "spa": "Spanish", "por": "Portuguese",
    "fre": "French", "fra": "French", "ger": "German", "deu": "German",
    "ita": "Italian", "ara": "Arabic", "hin": "Hindi", "ind": "Indonesian",
    "may": "Malay", "msa": "Malay", "tha": "Thai", "vie": "Vietnamese",
    "chi": "Chinese", "zho": "Chinese", "kor": "Korean", "rus": "Russian",
    "und": "Unknown", "tgl": "Tagalog", "tam": "Tamil", "tel": "Telugu",
    "mal": "Malayalam", "ben": "Bengali",
}


def _lang_name(code: str) -> str:
    if not code:
        return "Unknown"
    key = code.lower()[:3]
    return LANG_NAMES.get(key, code.title())


def format_audio(audio_langs) -> str:
    if not audio_langs:
        return "N/A"
    names = []
    for c in audio_langs:
        n = _lang_name(c)
        if n not in names:
            names.append(n)
    return ", ".join(names)


def format_subs(sub_langs) -> str:
    if not sub_langs:
        return "N/A"
    names = {_lang_name(c) for c in sub_langs}
    if len(names) == 1:
        return names.pop()
    return "Multi-Subs"


def _overview_text(al_data: dict) -> str:
    if not al_data:
        return "No overview available."
    desc = (al_data.get("description") or "").strip()
    if not desc:
        return "No overview available."
    words = desc.split()
    if len(words) > OVERVIEW_WORD_LIMIT:
        desc = " ".join(words[:OVERVIEW_WORD_LIMIT]) + " ...."
    return desc


def build_caption(al_data: dict, group: dict, audio_langs, sub_langs) -> str:
    fallback_title = group.get("title", "Unknown")

    if al_data:
        title_block = al_data.get("title") or {}
        title_en = title_block.get("english") or title_block.get("romaji") or fallback_title
        title_native = title_block.get("native") or title_en
        genres = ", ".join(al_data.get("genres") or []) or "N/A"
        anilist_id = al_data.get("id")
        link = f"https://anilist.co/anime/{anilist_id}" if anilist_id else None
    else:
        title_en = title_native = fallback_title
        genres = "N/A"
        link = None

    header = f"{title_en} | {title_native}" if title_en != title_native else title_en
    more_info = f'<a href="{link}">𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈</a>' if link else ""
    audio_str = format_audio(audio_langs)
    sub_str = format_subs(sub_langs)
    episode = group.get("episode", "?")

    def _render(overview: str) -> str:
        return (
            f"<blockquote><b>{header}</b></blockquote>\n"
            f"<b>◇──◇──◇──◇──◇──◇──◇──◇</b>\n"
            f"<b>✦</b> <i>Genres:</i> <code>{genres}</code>\n"
            f"<b>✦</b> <i>Episode:</i> <code>{episode}</code>\n"
            f"<b>✦</b> <i>Audio:</i> <code>{audio_str}</code>\n"
            f"<b>✦</b> <i>Subtitle:</i> <code>{sub_str}</code>\n"
            f"<b>◇──◇──◇──◇──◇──◇──◇──◇</b>\n"
            f"<blockquote expandable><b>‣ ᴏᴠᴇʀᴠɪᴇᴡ :</b> <i>{overview}</i>{more_info}</blockquote>"
        )

    overview = _overview_text(al_data)
    caption = _render(overview)

    if len(caption) > TELEGRAM_CAPTION_LIMIT:
        overhead = len(caption) - len(overview)
        available = max(0, TELEGRAM_CAPTION_LIMIT - overhead - 5)
        trimmed = overview[:available].rsplit(" ", 1)[0].rstrip(".") + " ...."
        caption = _render(trimmed)

    return caption
