#(©) PythonBotz

from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URI, DB_NAME

dbclient = AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']

# Auto-upload / poster feature collections
anime_map = database['anime_map']
pending_groups = database['pending_groups']


async def present_user(user_id: int):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

async def add_user(user_id: int):
    await user_data.insert_one({'_id': user_id})
    return

async def full_userbase():
    user_docs = user_data.find()
    user_ids = []
    async for doc in user_docs:
        user_ids.append(doc['_id'])
    return user_ids

async def del_user(user_id: int):
    await user_data.delete_one({'_id': user_id})
    return


# ──────────────────────────────────────────────────────────────────────────
# /setanime title → AniList / TMDB / poster mapping
# ──────────────────────────────────────────────────────────────────────────

async def set_anime_mapping(normalized_title: str, title: str, anilist_id: int,
                             tmdb_id: int = None, tmdb_season: int = None):
    await anime_map.update_one(
        {'_id': normalized_title},
        {'$set': {
            'title': title,
            'anilist_id': int(anilist_id),
            'tmdb_id': int(tmdb_id) if tmdb_id else None,
            'tmdb_season': int(tmdb_season) if tmdb_season else None,
        }},
        upsert=True,
    )


async def get_anime_mapping(normalized_title: str):
    return await anime_map.find_one({'_id': normalized_title})


async def delete_anime_mapping(normalized_title: str):
    result = await anime_map.delete_one({'_id': normalized_title})
    return result.deleted_count > 0


async def list_anime_mappings():
    docs = anime_map.find().sort('title', 1)
    return [doc async for doc in docs]


async def set_anime_poster(normalized_title: str, poster_format: str, file_id: str):
    await anime_map.update_one(
        {'_id': normalized_title},
        {'$set': {'poster_format': poster_format, 'poster_file_id': file_id}},
        upsert=True,
    )


# ──────────────────────────────────────────────────────────────────────────
# Pending quality groups for the CHECK_CHANNEL auto-upload watcher
# ──────────────────────────────────────────────────────────────────────────

def _group_id(normalized_title: str, episode_key: str) -> str:
    return f"{normalized_title}|{episode_key}"


async def upsert_pending_file(title: str, normalized_title: str, episode_key: str,
                               season: int, episode: int, quality: str, tag: str,
                               chat_id: int, message_id: int):
    doc_id = _group_id(normalized_title, episode_key)
    await pending_groups.update_one(
        {'_id': doc_id},
        {
            '$set': {
                'title': title,
                'normalized_title': normalized_title,
                'episode_key': episode_key,
                'season': season,
                'episode': episode,
                f'qualities.{quality}': {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'tag': tag,
                },
            },
            '$setOnInsert': {'created_at': datetime.now(timezone.utc)},
        },
        upsert=True,
    )


async def get_pending_group(normalized_title: str, episode_key: str):
    return await pending_groups.find_one({'_id': _group_id(normalized_title, episode_key)})


async def delete_pending_group(normalized_title: str, episode_key: str):
    await pending_groups.delete_one({'_id': _group_id(normalized_title, episode_key)})


async def list_pending_groups():
    docs = pending_groups.find().sort('created_at', 1)
    return [doc async for doc in docs]
