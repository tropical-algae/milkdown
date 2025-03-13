from datetime import datetime, timezone
import re

from milkdown.app.models.model_verify import VerifyRequest
from milkdown.common.config import settings
from milkdown.common.logging import logger


def match_version(pattern: str, version: str) -> bool:
    """匹配给定的版本号模式

    Args:
        pattern (str): 包含 `X` 的版本号模式（如 "1.X.0.X"）
        version (str): 待匹配的版本号（如 "1.2.0.3"）

    Returns:
        bool: 是否匹配
    """

    regex_pattern = pattern.replace("X", r"\d+")
    regex_pattern = rf"^{regex_pattern}$"

    return bool(re.match(regex_pattern, version))


def match_timestamp(timestamp: int, max_allowed_diff: int = 300):
    """校验客户端时间戳

    Args:
        timestamp (int): 客户端传来的时间戳（秒）
        max_allowed_diff (int, optional): 最大允许的时间差（秒），Defaults to 300.

    Returns:
        _type_: 是否通过校验
    """
    
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    time_diff = abs(current_timestamp - timestamp)
    return time_diff <= max_allowed_diff


def verify_client_info(data: VerifyRequest) -> bool | None:
    try:
        versify_result = [
            match_version(pattern=pattern, version=data.version)
            for pattern in settings.VALID_CLIENT_VERSION
        ]
        versify_result.append(
            match_timestamp(
                timestamp=data.timestamp, 
                max_allowed_diff=settings.VALID_TIMESTAMP_DIFF
            )
        )
        return all(versify_result)
    except Exception as err:
        logger.error(f"Verify client ERROR: {err}")
        return None
