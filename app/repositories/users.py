from typing import cast
from typing import TypedDict

from app import state
from app.constants import Privileges

READ_PARAMS = """\
    `u.id` AS `id`,
    `u.username` AS `username`,
    `u.privileges` AS `privileges`,
    `d.discord_id` AS `discord_id`
"""


class User(TypedDict):
    id: int
    username: str
    privileges: Privileges
    discord_id: int | None


async def fetch_one_from_discord_id(discord_id: int) -> User | None:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM `users` `u`
        INNER JOIN `discord_oauth` `d`
        ON `u.id` = `d.user_id`
        WHERE `d.discord_id` = :discord_id
    """

    params = {"discord_id": discord_id}
    rec = await state.read_database.fetch_one(query, params)

    if rec is None:
        return None

    return cast(User, rec)


async def fetch_all_supporters() -> list[User]:
    query = f"""\
        SELECT {READ_PARAMS}
        FROM `users` `u`
        INNER JOIN `discord_oauth` `d`
        ON `u.id` = `d.user_id`
        WHERE `u.privileges` & {Privileges.USER_DONOR}
    """

    rec = await state.read_database.fetch_all(query)
    return cast(list[User], rec)
