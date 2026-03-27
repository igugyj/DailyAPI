# 热搜助手

一个轻量级 Windows 桌面热搜卡片，聚合 **哔哩哔哩 / 百度贴吧 / 微博 / 知乎** 四大平台实时热搜，样式简约，常驻桌面底层。

---

## 功能一览

| 功能 | 说明 |
|------|------|
| 多平台聚合 | 点击顶部标签切换平台榜单 |
| 实时热搜 | 每 10 分钟自动刷新（可配置） |
| 悬停预览 | 鼠标停留在条目上显示完整标题 + 简介 |
| 一键跳转 | 点击条目直接在浏览器打开对应页面 |
| 折叠收纳 | 双击顶部标题栏折叠为小圆形按钮，点击还原 |
| 自由拖拽 | 左键按住卡片/折叠按钮可拖到任意位置 |
| 半透明背景 | 无边框，底置桌面，不遮挡其他窗口 |
| 系统托盘 | 右键托盘可立即刷新 / 打开工作目录 / 编辑配置 / 退出 |
| 完全可配置 | 所有颜色、尺寸、刷新间隔均在 `config.json` 中调整 |
| 错误日志 | 默认关闭，可在配置中开启，仅记录错误 |

---

## 项目结构

```
hotsearch/
├── main.py          # 入口 & 应用控制器
├── widget.py        # 主卡片 & 折叠按钮
├── fetcher.py       # 后台数据拉取线程
├── tray.py          # 系统托盘
├── config.json      # 样式与行为配置
├── requirements.txt
└── README.md
```

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

> 推荐 Python 3.11+，Windows 10/11。

### 2. 启动后端 API

项目依赖本地 API 服务（默认 `http://127.0.0.1:6688`）提供热搜数据，  
请确保 API 服务已运行，并根据实际地址修改 `config.json` 中的 `api_base`。

API 响应格式示例：

```json
{
  "code": 200,
  "name": "weibo",
  "title": "微博",
  "data": [
    {
      "title": "热搜标题",
      "desc": "简介描述",
      "url": "https://...",
      "hot": 1234567
    }
  ]
}
```

### 3. 运行

```bash
python main.py
```

---

## 配置文件 `config.json`

```jsonc
{
    // 窗口初始位置与尺寸
    "window": {
        "width": 320,
        "height": 520,
        "x": 80,
        "y": 120,
        "opacity": 0.92         // 整体透明度 0.0 ~ 1.0
    },

    "refresh_interval": 600,    // 自动刷新间隔（秒），默认 10 分钟

    "api_base": "http://127.0.0.1:6688",  // API 基础地址

    // 各平台端点配置，key 需与 API 返回的 name 字段对应
    "platforms": {
        "bilibili": { "name": "哔哩哔哩", "endpoint": "/bilibili" },
        "tieba":    { "name": "贴吧",     "endpoint": "/tieba" },
        "weibo":    { "name": "微博",     "endpoint": "/weibo" },
        "zhihu":    { "name": "知乎",     "endpoint": "/zhihu" }
    },

    // 主题色彩（CSS 颜色或 "R,G,B" 格式）
    "theme": {
        "bg_color":           "20, 20, 35",      // 卡片背景 RGB
        "bg_alpha":           210,                // 背景透明度 0~255
        "header_color":       "25, 25, 45",       // 顶栏 RGB
        "header_alpha":       230,
        "card_radius":        14,                 // 圆角半径 px
        "active_tab_color":   "#e94560",          // 当前选中平台标签色
        "inactive_tab_color": "rgba(255,255,255,0.45)",
        "item_hover_bg":      "rgba(255,255,255,0.07)",
        "rank1_color":        "#ff4444",          // 前三名排名颜色
        "rank2_color":        "#ff8800",
        "rank3_color":        "#ffbb00",
        "rank_default_color": "rgba(255,255,255,0.35)",
        "title_color":        "#f0f0f0",          // 条目标题文字色
        "hot_color":          "rgba(255,255,255,0.45)", // 热度数字色
        "sep_color":          "rgba(255,255,255,0.06)", // 分隔线色
        "font_family":        "Microsoft YaHei, PingFang SC, sans-serif",
        "font_size_tab":      12,
        "font_size_item":     12,
        "font_size_hot":      10
    },

    // 折叠小按钮外观
    "collapsed_button": {
        "width":    48,
        "height":   48,
        "bg_color": "20, 20, 35",
        "bg_alpha": 220,
        "radius":   24
    },

    // 错误日志（默认关闭）
    "logging": {
        "enabled": false,
        "file": "error.log"
    },

    // 系统托盘
    "tray": {
        "icon":    "",              // 自定义图标路径（png/ico），留空使用默认
        "tooltip": "热搜助手"
    }
}
```

---

## 操作说明

| 操作 | 效果 |
|------|------|
| 左键按住卡片拖动 | 移动卡片位置 |
| 双击顶部标题栏 | 折叠为小圆形按钮 |
| 点击折叠小按钮 | 展开主卡片 |
| 鼠标滚轮 | 滚动热搜列表 |
| 点击平台标签 | 切换平台榜单 |
| 点击热搜条目 | 浏览器打开对应页面 |
| 鼠标悬停条目 | 显示完整标题 + 简介 |
| 右键托盘图标 | 弹出托盘菜单 |
| 点击托盘图标 | 显示 / 隐藏主卡片 |

---

## 常见问题

**Q: 卡片显示"获取失败，请检查 API"？**  
A: 请确认本地 API 服务正在运行，且 `config.json` 中 `api_base` 地址正确。

**Q: 想调整卡片大小？**  
A: 修改 `config.json` 中 `window.width` 和 `window.height`，重启生效。

**Q: 想增减平台？**  
A: 在 `platforms` 中增删条目，`endpoint` 需与 API 路由对应。

**Q: 字体显示不正常？**  
A: 修改 `theme.font_family` 为本地已安装字体名称。

---

## 依赖

- Python 3.11+
- PySide6 >= 6.6.0
- requests >= 2.31.0
