"""
系统语言检测模块，用于首次运行时确定默认界面语言。
返回原始语言代码（如 'zh_CN', 'zh_TW', 'en_US'），不做归一化。
"""

import locale
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def detect_system_language() -> str:
    """
    检测操作系统当前的语言设置，返回原始语言代码（如 'zh_CN', 'zh_TW', 'en_US'）。
    若无法检测，默认返回 'en_US'。

    返回值格式：语言_地区，下划线分隔，例如 'zh_CN', 'zh_TW', 'en_US'。
    """
    lang_code: Optional[str] = None

    # 方法1：getdefaultlocale() 通常返回 (language_code, encoding)
    try:
        default_locale = locale.getdefaultlocale()
        if default_locale and default_locale[0]:
            raw = default_locale[0]
            # 统一将短横线替换为下划线，例如 zh-CN -> zh_CN
            lang_code = raw.replace('-', '_')
            logger.debug(f"detected via getdefaultlocale: {lang_code}")
    except Exception as e:
        logger.warning(f"getdefaultlocale() failed: {e}")

    # 方法2：尝试获取 LC_MESSAGES 类别
    if (not lang_code) and hasattr(locale, 'LC_MESSAGES'):
        try:
            lc_messages = locale.getlocale(locale.LC_MESSAGES)
            if lc_messages and lc_messages[0]:
                raw = lc_messages[0]
                lang_code = raw.replace('-', '_')
                logger.debug(f"detected via LC_MESSAGES: {lang_code}")
        except Exception as e:
            logger.warning(f"LC_MESSAGES detection failed: {e}")

    # 最终回退
    if not lang_code:
        logger.warning("Unable to detect system language, falling back to en_US")
        return "en_US"

    # 不做归一化，直接返回原始代码（例如 zh_CN, zh_TW, en_US, de_DE 等）
    return lang_code