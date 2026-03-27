"""
fetcher.py — 后台数据拉取线程
"""

import logging
import requests
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class DataFetcher(QThread):
    """在后台线程中拉取各平台热搜数据，完成后通过信号通知主线程。"""

    finished = Signal(dict)   # {platform_key: api_response_dict}
    error    = Signal(str)    # 错误描述

    def __init__(self, api_base: str, platforms: dict, timeout: int = 10):
        """
        :param api_base:  API 基础地址，如 "http://127.0.0.1:6688"
        :param platforms: config["platforms"] 字典
        :param timeout:   单次请求超时秒数
        """
        super().__init__()
        self.api_base  = api_base.rstrip("/")
        self.platforms = platforms
        self.timeout   = timeout

    def run(self):
        results: dict = {}
        errors:  list = []

        for key, info in self.platforms.items():
            url = self.api_base + info["endpoint"]
            try:
                resp = requests.get(url, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                results[key] = data
            except requests.exceptions.RequestException as exc:
                msg = f"[{key}] 请求失败: {exc}"
                logger.error(msg)
                errors.append(msg)
            except Exception as exc:
                msg = f"[{key}] 解析失败: {exc}"
                logger.error(msg)
                errors.append(msg)

        if results:
            self.finished.emit(results)
        else:
            self.error.emit("\n".join(errors) if errors else "所有平台数据获取失败")
