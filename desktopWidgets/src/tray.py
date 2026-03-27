"""
tray.py — 系统托盘
"""

import os
import subprocess
import logging

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter, QPainterPath, QFont
from PySide6.QtCore import Qt, Signal, QObject

logger = logging.getLogger(__name__)


def _make_default_icon(size: int = 64) -> QIcon:
    """生成默认托盘图标（深色圆形 + 白色"热"字）。"""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)

    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    path = QPainterPath()
    path.addEllipse(2, 2, size - 4, size - 4)
    p.fillPath(path, QColor(233, 69, 96))

    p.setPen(QColor(255, 255, 255))
    font = QFont("Microsoft YaHei", int(size * 0.38), QFont.Weight.Bold)
    p.setFont(font)
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "热")
    p.end()

    return QIcon(pix)


class TrayIcon(QObject):
    """系统托盘图标及菜单。"""

    action_show = Signal()  # 显示/隐藏主窗口
    action_refresh = Signal()  # 立即刷新
    action_open_dir = Signal()  # 打开工作目录
    action_open_cfg = Signal()  # 打开配置文件
    action_quit = Signal()  # 退出

    def __init__(self, cfg: dict, work_dir: str):
        super().__init__()
        tray_cfg = cfg.get("tray", {})

        # 图标
        icon_path = tray_cfg.get("icon", "")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(work_dir, icon_path)
        print(f"图标路径：{icon_path}")
        if os.path.exists(icon_path) and os.path.isfile(icon_path):
            print(f"加载自定义图标：{icon_path}")
            icon = QIcon(icon_path)
        else:
            print("加载默认图标")
            icon = _make_default_icon()

        tooltip = tray_cfg.get("tooltip", "DailyAPI")

        self._tray = QSystemTrayIcon(icon)
        self._tray.setToolTip(tooltip)
        self._work_dir = work_dir

        self._build_menu()
        self._tray.show()
        self._tray.activated.connect(self._on_activated)

    # ── 菜单构建 ──────────────────────────────
    def _build_menu(self):
        menu = QMenu()
        menu.setStyleSheet(
            """
            QMenu {
                background: #1a1a2e;
                color: #f0f0f0;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 6px;
                padding: 4px;
                font-family: "Microsoft YaHei";
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: rgba(233,69,96,0.55);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255,255,255,0.1);
                margin: 4px 0;
            }
        """
        )

        act_show = menu.addAction("显示 / 隐藏")
        act_refresh = menu.addAction("立即刷新")
        menu.addSeparator()
        act_dir = menu.addAction("打开工作目录")
        act_cfg = menu.addAction("打开配置文件")
        menu.addSeparator()
        act_quit = menu.addAction("退出")

        act_show.triggered.connect(self.action_show)
        act_refresh.triggered.connect(self.action_refresh)
        act_dir.triggered.connect(self.action_open_dir)
        act_cfg.triggered.connect(self.action_open_cfg)
        act_quit.triggered.connect(self.action_quit)

        self._tray.setContextMenu(menu)

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.action_show.emit()

    def show_message(
        self, title: str, msg: str, icon=QSystemTrayIcon.MessageIcon.Information
    ):
        self._tray.showMessage(title, msg, icon, 3000)
