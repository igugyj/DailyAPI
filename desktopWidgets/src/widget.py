"""
widget.py — 热搜卡片主界面
"""

import logging
import webbrowser
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QApplication,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QPoint,
    QSize,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPainterPath,
    QFont,
    QCursor,
    QPixmap,
    QMouseEvent,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  热搜条目控件
# ─────────────────────────────────────────────
class ItemWidget(QFrame):
    """单条热搜条目：序号 + 标题 + 热度，点击打开链接。"""

    def __init__(
        self,
        rank: int,
        title: str,
        desc: str,
        url: str,
        hot: int,
        theme: dict,
        parent=None,
    ):
        super().__init__(parent)
        self.url = url
        self.theme = theme

        self.setToolTip(f"<b>{title}</b><br><small>{desc}</small>" if desc else title)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self.setObjectName("ItemWidget")

        # 排名颜色
        if rank == 1:
            rank_color = theme.get("rank1_color", "#ff4444")
        elif rank == 2:
            rank_color = theme.get("rank2_color", "#ff8800")
        elif rank == 3:
            rank_color = theme.get("rank3_color", "#ffbb00")
        else:
            rank_color = theme.get("rank_default_color", "rgba(255,255,255,0.35)")

        font_family = theme.get("font_family", "Microsoft YaHei")

        # 排名标签
        rank_label = QLabel(str(rank))
        rank_label.setFixedWidth(22)
        rank_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_label.setStyleSheet(
            f"""
            QLabel {{
                color: {rank_color};
                font-family: {font_family};
                font-size: 11px;
                font-weight: bold;
                background: transparent;
            }}
        """
        )

        # 标题
        title_label = QLabel(title)
        title_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        title_label.setWordWrap(False)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                color: {theme.get("title_color", "#f0f0f0")};
                font-family: {font_family};
                font-size: {theme.get("font_size_item", 12)}px;
                background: transparent;
            }}
        """
        )

        # 热度
        hot_str = self._fmt_hot(hot)
        hot_label = QLabel(hot_str)
        hot_label.setFixedWidth(46)
        hot_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        hot_label.setStyleSheet(
            f"""
            QLabel {{
                color: {theme.get("hot_color", "rgba(255,255,255,0.45)")};
                font-family: {font_family};
                font-size: {theme.get("font_size_hot", 10)}px;
                background: transparent;
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 8, 0)
        layout.setSpacing(6)
        layout.addWidget(rank_label)
        layout.addWidget(title_label)
        layout.addWidget(hot_label)

        self._set_normal_style()

    # ── 样式 ─────────────────────────────────
    def _set_normal_style(self):
        self.setStyleSheet(
            """
            ItemWidget {
                background: transparent;
                border: none;
            }
        """
        )

    def _set_hover_style(self):
        hover_bg = self.theme.get("item_hover_bg", "rgba(255,255,255,0.07)")
        self.setStyleSheet(
            f"""
            ItemWidget {{
                background: {hover_bg};
                border-radius: 6px;
            }}
        """
        )

    # ── 交互 ─────────────────────────────────
    def enterEvent(self, event):
        self._set_hover_style()

    def leaveEvent(self, event):
        self._set_normal_style()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.url:
            webbrowser.open(self.url)

    # ── 工具方法 ─────────────────────────────
    @staticmethod
    def _fmt_hot(hot: int) -> str:
        if not hot:
            return ""
        if hot >= 100_000_000:
            return f"{hot/100_000_000:.1f}亿"
        if hot >= 10_000:
            return f"{hot/10_000:.1f}w"
        return str(hot)


# ─────────────────────────────────────────────
#  分隔线
# ─────────────────────────────────────────────
class Separator(QFrame):
    def __init__(self, color: str = "rgba(255,255,255,0.06)", parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background: {color}; border: none;")


# ─────────────────────────────────────────────
#  折叠小按钮
# ─────────────────────────────────────────────
class CollapsedButton(QWidget):
    """折叠后显示的小圆形按钮，点击展开主界面。"""

    clicked = Signal()

    def __init__(self, cfg: dict, parent=None):
        super().__init__(parent)
        btn_cfg = cfg.get("collapsed_button", {})
        w = btn_cfg.get("width", 48)
        h = btn_cfg.get("height", 48)
        bg = btn_cfg.get("bg_color", "20, 20, 35")
        alpha = btn_cfg.get("bg_alpha", 220)
        self._radius = btn_cfg.get("radius", 24)
        self._bg = QColor(*(int(x) for x in bg.split(",")), alpha)

        self.setFixedSize(w, h)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._drag_pos: QPoint | None = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(2, 2, self.width() - 4, self.height() - 4)
        p.fillPath(path, self._bg)
        # 绘制简单"H"图标
        p.setPen(QColor(255, 255, 255, 180))
        font = QFont("Microsoft YaHei", 11, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "热")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            # 没有移动 → 认为是点击
            if self._drag_pos is not None:
                delta = (
                    event.globalPosition().toPoint()
                    - self._drag_pos
                    - self.frameGeometry().topLeft()
                )
                # if abs(delta.x()) < 5 and abs(delta.y()) < 5:
                #     self.clicked.emit()
            self._drag_pos = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.clicked.emit()
        event.accept()


# ─────────────────────────────────────────────
#  主热搜卡片
# ─────────────────────────────────────────────
class HotSearchCard(QWidget):
    """热搜主卡片：平台 Tab + 可滚动列表。"""

    request_refresh = Signal()  # 通知外部立即刷新

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg
        self.theme = cfg.get("theme", {})
        self.platforms = cfg.get("platforms", {})

        # 当前选中平台
        self._platform_keys = list(self.platforms.keys())
        self._current_platform = self._platform_keys[0] if self._platform_keys else ""
        self._data: dict = {}  # {key: api_response}
        self._tab_labels: dict = {}  # {key: QLabel}

        self._drag_pos: QPoint | None = None

        # 背景颜色
        bg_rgb = self.theme.get("bg_color", "20, 20, 35")
        bg_alpha = self.theme.get("bg_alpha", 210)
        self._bg_color = QColor(*(int(x) for x in bg_rgb.split(",")), bg_alpha)

        hdr_rgb = self.theme.get("header_color", "25, 25, 45")
        hdr_alpha = self.theme.get("header_alpha", 230)
        self._hdr_color = QColor(*(int(x) for x in hdr_rgb.split(",")), hdr_alpha)

        self._radius = self.theme.get("card_radius", 14)

        # 窗口属性
        win_cfg = cfg.get("window", {})
        self.setFixedSize(win_cfg.get("width", 320), win_cfg.get("height", 520))
        self.move(win_cfg.get("x", 80), win_cfg.get("y", 120))
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnBottomHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(win_cfg.get("opacity", 0.92))
        self.setWindowTitle("热搜助手")

        self._build_ui()

    # ═══════════════════════════════════════
    #  构建界面
    # ═══════════════════════════════════════
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 顶栏 ─────────────────────────────
        self._header = QWidget()
        self._header.setFixedHeight(48)
        self._header.setObjectName("Header")
        header_layout = QVBoxLayout(self._header)
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(0)

        # 平台 Tab 行
        tab_row = QHBoxLayout()
        tab_row.setSpacing(4)
        font_family = self.theme.get("font_family", "Microsoft YaHei")
        tab_size = self.theme.get("font_size_tab", 12)

        for key, info in self.platforms.items():
            lbl = QLabel(info["name"])
            lbl.setFont(QFont(font_family, tab_size, QFont.Weight.Bold))
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setContentsMargins(6, 0, 6, 0)
            lbl.mousePressEvent = lambda e, k=key: self._switch_platform(k)
            self._tab_labels[key] = lbl
            tab_row.addWidget(lbl)

        tab_row.addStretch()

        # 更新时间标签
        self._time_label = QLabel("")
        self._time_label.setFont(QFont(font_family, 9))
        self._time_label.setStyleSheet("color: rgba(255,255,255,0.3);")
        tab_row.addWidget(self._time_label)

        header_layout.addStretch()
        header_layout.addLayout(tab_row)
        header_layout.addStretch()

        root.addWidget(self._header)
        root.addWidget(Separator(self.theme.get("sep_color", "rgba(255,255,255,0.06)")))

        # ── 滚动区域 ─────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setStyleSheet(
            """
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255,255,255,0.25);
                border-radius: 2px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height: 0; }
        """
        )

        self._list_container = QWidget()
        self._list_container.setObjectName("ListContainer")
        self._list_container.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(8, 6, 8, 6)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch()

        self._scroll.setWidget(self._list_container)
        root.addWidget(self._scroll)

        # 底部状态条
        self._status_bar = QLabel("正在加载...")
        self._status_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_bar.setFixedHeight(24)
        self._status_bar.setFont(QFont(self.theme.get("font_family", ""), 9))
        self._status_bar.setStyleSheet(
            "color: rgba(255,255,255,0.3); background: transparent;"
        )
        root.addWidget(self._status_bar)

        self._refresh_tab_styles()

    # ═══════════════════════════════════════
    #  数据更新
    # ═══════════════════════════════════════
    def update_data(self, data: dict):
        """接收 DataFetcher 返回的全量数据并刷新界面。"""
        self._data = data
        self._render_current()
        now = datetime.now().strftime("%H:%M")
        self._time_label.setText(f"更新于 {now}")
        self._status_bar.setText("")

    def set_status(self, msg: str):
        self._status_bar.setText(msg)

    def _switch_platform(self, key: str):
        if key == self._current_platform:
            return
        self._current_platform = key
        self._refresh_tab_styles()
        self._render_current()
        self._scroll.verticalScrollBar().setValue(0)

    def _render_current(self):
        """清空列表，渲染当前平台数据。"""
        # 移除旧条目（保留最后的 stretch）
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        raw = self._data.get(self._current_platform)
        if not raw:
            placeholder = QLabel("暂无数据")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            placeholder.setStyleSheet("color: rgba(255,255,255,0.3); font-size: 13px;")
            self._list_layout.insertWidget(0, placeholder)
            return

        items = raw.get("data", [])
        sep_color = self.theme.get("sep_color", "rgba(255,255,255,0.06)")

        for i, item in enumerate(items):
            title = item.get("title", "")
            desc = item.get("desc", "")
            url = item.get("url") or item.get("mobileUrl", "")
            hot = item.get("hot", 0)

            w = ItemWidget(i + 1, title, desc, url, hot, self.theme)
            self._list_layout.insertWidget(i * 2, w)
            if i < len(items) - 1:
                self._list_layout.insertWidget(i * 2 + 1, Separator(sep_color))

    def _refresh_tab_styles(self):
        active = self.theme.get("active_tab_color", "#e94560")
        inactive = self.theme.get("inactive_tab_color", "rgba(255,255,255,0.45)")
        for key, lbl in self._tab_labels.items():
            if key == self._current_platform:
                lbl.setStyleSheet(f"color: {active}; background: transparent;")
            else:
                lbl.setStyleSheet(f"color: {inactive}; background: transparent;")

    # ═══════════════════════════════════════
    #  绘制半透明圆角背景
    # ═══════════════════════════════════════
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        r = self._radius
        w, h = self.width(), self.height()
        hdr_h = self._header.height() + 1  # +1 for separator

        # 整体背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, r, r)
        p.fillPath(path, self._bg_color)

        # 顶栏背景（略深）
        hdr_path = QPainterPath()
        hdr_path.addRoundedRect(0, 0, w, hdr_h, r, r)
        # 补矩形去掉下半圆角
        hdr_path.addRect(0, r, w, hdr_h - r)
        p.fillPath(hdr_path, self._hdr_color)

    # ═══════════════════════════════════════
    #  拖拽
    # ═══════════════════════════════════════
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None
