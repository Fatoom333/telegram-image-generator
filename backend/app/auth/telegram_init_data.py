import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qsl


@dataclass(frozen=True)
class TelegramMiniAppUser:
    telegram_id: int
    username: str | None
    first_name: str | None


class TelegramInitDataError(Exception):
    pass


class TelegramInitDataExpiredError(TelegramInitDataError):
    pass


class TelegramInitDataHashError(TelegramInitDataError):
    pass


class TelegramInitDataUserError(TelegramInitDataError):
    pass


def validate_telegram_init_data(
    init_data: str,
    bot_token: str,
    max_age: timedelta = timedelta(hours=24),
) -> TelegramMiniAppUser:
    parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = parsed_data.pop("hash", None)

    if received_hash is None:
        raise TelegramInitDataHashError("Telegram init data hash is missing")

    auth_date_raw = parsed_data.get("auth_date")

    if auth_date_raw is None:
        raise TelegramInitDataExpiredError("Telegram auth_date is missing")

    try:
        auth_date = datetime.fromtimestamp(int(auth_date_raw), tz=UTC)
    except ValueError as error:
        raise TelegramInitDataExpiredError("Telegram auth_date is invalid") from error

    if datetime.now(tz=UTC) - auth_date > max_age:
        raise TelegramInitDataExpiredError("Telegram init data is expired")

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramInitDataHashError("Telegram init data hash is invalid")

    user_raw = parsed_data.get("user")

    if user_raw is None:
        raise TelegramInitDataUserError("Telegram user is missing")

    try:
        user_data = json.loads(user_raw)
    except json.JSONDecodeError as error:
        raise TelegramInitDataUserError("Telegram user is invalid") from error

    telegram_id = user_data.get("id")

    if not isinstance(telegram_id, int):
        raise TelegramInitDataUserError("Telegram user id is invalid")

    username = user_data.get("username")
    first_name = user_data.get("first_name")

    return TelegramMiniAppUser(
        telegram_id=telegram_id,
        username=username if isinstance(username, str) else None,
        first_name=first_name if isinstance(first_name, str) else None,
    )
