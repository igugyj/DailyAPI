"""
main.py — 热搜助手入口 & 应用控制器
"""

import sys
import os
import json
import logging
import subprocess
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PySide6.QtGui import QIcon

from widget  import HotSearchCard, CollapsedButton
from fetcher import DataFetcher
from tray    import TrayIcon

# ─── 工作目录 ────────────────────────────────────────────────
WORK_DIR   = Path(__file__).parent.resolve()
CONFIG_PATH = WORK_DIR / "config.json"

# ─── 配置加载 ─────────────────────────────────────────────────
def load_config() -> dict:
    print(f"工作目录: {WORK_DIR}")
    if not CONFIG_PATH.exists():
        print(f"[警告] 配置文件不存在: {CONFIG_PATH}，使用默认配置。")
        return {}
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"[错误] 读取配置失败: {exc}")
        return {}


# ─── 日志初始化 ───────────────────────────────────────────────
def setup_logging(cfg: dict):
    log_cfg = cfg.get("logging", {})
    if not log_cfg.get("enabled", False):
        logging.disable(logging.CRITICAL)
        return
    log_file = WORK_DIR / log_cfg.get("file", "error.log")
    logging.basicConfig(
        filename=str(log_file),
        level=logging.ERROR,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding="utf-8",
    )


# ─── 应用控制器 ───────────────────────────────────────────────
class AppController:
    """负责调度刷新、折叠/展开动画、托盘事件。"""

    ANIM_DURATION = 280   # ms

    def __init__(self, app: QApplication, cfg: dict):
        self.app  = app
        self.cfg  = cfg
        self._is_collapsed = False

        # 主卡片
        self.card = HotSearchCard(cfg)
        self.card.show()

        # 折叠按钮（初始隐藏）
        self.collapsed_btn = CollapsedButton(cfg)
        self.collapsed_btn.hide()
        self.collapsed_btn.clicked.connect(self.expand)

        # 托盘
        self.tray = TrayIcon(cfg, str(WORK_DIR))
        self.tray.action_show.connect(self._toggle_visibility)
        self.tray.action_refresh.connect(self.refresh_now)
        self.tray.action_open_dir.connect(self._open_work_dir)
        self.tray.action_open_cfg.connect(self._open_config)
        self.tray.action_quit.connect(self._quit)

        # 刷新定时器
        interval_sec = cfg.get("refresh_interval", 600)
        self._timer = QTimer()
        self._timer.setInterval(interval_sec * 1000)
        self._timer.timeout.connect(self.refresh_now)
        self._timer.start()

        # 立即拉一次数据
        self.refresh_now()

    # ── 折叠 / 展开 ──────────────────────────────────────────
    def collapse(self):
        if self._is_collapsed:
            return
        self._is_collapsed = True

        # 把折叠按钮放到卡片的左上角附近
        pos = self.card.pos()
        self.collapsed_btn.move(pos)
        self.collapsed_btn.show()

        # 淡出 + 收缩动画
        self._anim = QPropertyAnimation(self.card, b"geometry")
        self._anim.setDuration(self.ANIM_DURATION)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        geo = self.card.geometry()
        target = QRect(geo.x(), geo.y(),
                       self.collapsed_btn.width(),
                       self.collapsed_btn.height())
        self._anim.setStartValue(geo)
        self._anim.setEndValue(target)
        self._anim.finished.connect(self.card.hide)
        self._anim.start()

    def expand(self):
        if not self._is_collapsed:
            return
        self._is_collapsed = False

        win_cfg = self.cfg.get("window", {})
        w = win_cfg.get("width",  320)
        h = win_cfg.get("height", 520)

        pos = self.collapsed_btn.pos()
        self.card.setGeometry(pos.x(), pos.y(), self.collapsed_btn.width(),
                              self.collapsed_btn.height())
        self.card.show()
        self.collapsed_btn.hide()

        # 展开动画
        self._anim = QPropertyAnimation(self.card, b"geometry")
        self._anim.setDuration(self.ANIM_DURATION)
        self._anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._anim.setEndValue(QRect(pos.x(), pos.y(), w, h))
        self._anim.start()

    # ── 刷新数据 ──────────────────────────────────────────────
    def refresh_now(self):
        self.card.set_status("正在刷新...")
        self._fetcher = DataFetcher(
            api_base=self.cfg.get("api_base", "http://127.0.0.1:6688"),
            platforms=self.cfg.get("platforms", {}),
        )
        self._fetcher.finished.connect(self._on_data_ready)
        self._fetcher.error.connect(self._on_fetch_error)
        self._fetcher.start()

    def _on_data_ready(self, data: dict):
        self.card.update_data(data)

    def _on_fetch_error(self, msg: str):
        self.card.set_status("获取失败，请检查 API")
        logging.getLogger(__name__).error(msg)

    # ── 可见性切换 ────────────────────────────────────────────
    def _toggle_visibility(self):
        if self._is_collapsed:
            self.expand()
        elif self.card.isVisible():
            self.card.hide()
        else:
            self.card.show()

    # ── 托盘动作 ─────────────────────────────────────────────
    def _open_work_dir(self):
        try:
            if sys.platform == "win32":
                os.startfile(str(WORK_DIR))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(WORK_DIR)])
            else:
                subprocess.Popen(["xdg-open", str(WORK_DIR)])
        except Exception as exc:
            logging.getLogger(__name__).error(f"打开工作目录失败: {exc}")

    def _open_config(self):
        try:
            if sys.platform == "win32":
                os.startfile(str(CONFIG_PATH))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(CONFIG_PATH)])
            else:
                subprocess.Popen(["xdg-open", str(CONFIG_PATH)])
        except Exception as exc:
            logging.getLogger(__name__).error(f"打开配置文件失败: {exc}")

    def _quit(self):
        self.app.quit()


# ─── 双击卡片标题区域折叠 ─────────────────────────────────────
def _patch_card_double_click(card: HotSearchCard, controller: AppController):
    """给 Header 区域绑定双击折叠。"""
    original = card._header.mouseDoubleClickEvent

    def on_dbl(event):
        controller.collapse()

    card._header.mouseDoubleClickEvent = on_dbl


# ─── 主程序 ───────────────────────────────────────────────────
def main():
    # 高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        __import__("PySide6.QtCore", fromlist=["Qt"])
        .Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("热搜助手")

    cfg = load_config()
    setup_logging(cfg)

    controller = AppController(app, cfg)
    _patch_card_double_click(controller.card, controller)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
