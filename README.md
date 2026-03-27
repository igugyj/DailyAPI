# DailyAPI

DailyAPI 是一个聚合了多平台实时热搜的桌面应用项目。它由两部分组成：

- **dailyhot-api**：基于 [dailyhot-api](https://github.com/kuole-o/dailyhot-api) 修改的 Node.js 服务端，提供哔哩哔哩、微博、知乎、贴吧等多个平台的热搜数据接口。
- **desktopWidgets**：基于 PySide6 的 Windows 桌面小部件，以卡片形式展示热搜列表，支持自动刷新、折叠、拖拽、托盘等便捷功能。

## 特性

- 服务端响应快速，支持 RSS / JSON 模式，内置缓存。
- 客户端界面简约，常驻桌面底层，不遮挡其他窗口。
- 多平台聚合，点击顶部标签可切换榜单。
- 悬停预览完整标题与简介，点击条目直接跳转原文。
- 可配置刷新间隔、窗口样式、颜色主题等。
- 支持系统托盘，右键菜单可立即刷新、打开工作目录、编辑配置或退出程序。

## 目录结构

```
DailyAPI/
├── dailyhot-api/          # Node.js 服务端
│   ├── .env.example       # 环境变量示例
│   ├── package.json
│   └── ...
├── desktopWidgets/        # Python 客户端
│   ├── src/
│   │   ├── main.py        # 入口与控制器
│   │   ├── widget.py      # 主卡片与折叠按钮
│   │   ├── fetcher.py     # 后台数据拉取线程
│   │   ├── tray.py        # 系统托盘
│   │   ├── config.json    # 客户端配置文件
│   │   └── ...
│   ├── requirements.txt   # Python 依赖
│   └── ...
├── setup.bat              # 环境配置脚本（安装依赖）
├── start.bat              # 后台启动脚本（无窗口）
└── README.md
```

## 环境要求

- Node.js 16+ 与 npm / pnpm
- Python 3.11+ （推荐）
- Windows 10 / 11 （客户端为 Windows 桌面应用）

## 配置步骤

**推荐使用环境配置脚本+启动脚本**

### 环境配置脚本

首次使用或更新依赖后，可运行 `setup.bat` 自动安装所需依赖（需已安装 Node.js、Python 和 git）：

![](setup.bat)

---

### 1. 安装服务端依赖

进入 `dailyhot-api` 目录，安装依赖：

```bash
git clone https://github.com/kuole-o/dailyhot-api.git
cd dailyhot-api
npm install
```

复制 `.env.example` 为 `.env` 并根据需要修改（如缓存时间、端口等）。
默认服务端口为 `6688`，如有冲突可修改 `.env` 中的 `PORT` 变量。

### 2. 安装客户端依赖

在项目根目录下，创建 Python 虚拟环境（可选但推荐）：

```bash
cd desktopWidgets
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

若不想使用虚拟环境，也可全局安装依赖（不推荐）。

### 3. 配置客户端

编辑 `desktopWidgets/src/config.json`，主要配置项：

- `api_base`：服务端地址，默认为 `http://127.0.0.1:6688`，需与服务端实际地址一致。
- `refresh_interval`：自动刷新间隔（秒）。
- `platforms`：平台列表，`key` 需与服务端路由对应。
- `theme`：颜色、字体、圆角等样式。
- 其他窗口、托盘等选项见文件内注释。

## 启动项目

### 方式一：手动启动

1. 在 `dailyhot-api` 目录下运行：

   ```bash
   npm run dev
   ```

   或编译后运行：

   ```bash
   npm run build && npm run start
   ```

2. 在 `desktopWidgets` 目录下，激活虚拟环境后运行：

   ```bash
   python src/main.py
   ```

### 方式二：使用启动脚本（推荐）

项目提供了 `start.bat`，双击后会在后台同时启动服务端和客户端，**无任何命令行窗口**。

![](start.bat)

## 客户端操作说明

| 操作             | 效果                |
| ---------------- | ------------------- |
| 左键按住卡片拖动 | 移动卡片位置        |
| 双击顶部标题栏   | 折叠为小圆形按钮    |
| 点击折叠小按钮   | 展开主卡片          |
| 鼠标滚轮         | 滚动热搜列表        |
| 点击平台标签     | 切换平台榜单        |
| 点击热搜条目     | 浏览器打开对应页面  |
| 鼠标悬停条目     | 显示完整标题 + 简介 |
| 右键托盘图标     | 弹出托盘菜单        |
| 点击托盘图标     | 显示 / 隐藏主卡片   |

## 配置文件示例

`desktopWidgets/src/config.json` 部分内容：

```json
{
  "window": {
    "width": 320,
    "height": 520,
    "x": 80,
    "y": 120,
    "opacity": 0.92
  },
  "refresh_interval": 600,
  "api_base": "http://127.0.0.1:6688",
  "platforms": {
    "bilibili": { "name": "哔哩哔哩", "endpoint": "/bilibili" },
    "tieba": { "name": "贴吧", "endpoint": "/tieba" },
    "weibo": { "name": "微博", "endpoint": "/weibo" },
    "zhihu": { "name": "知乎", "endpoint": "/zhihu" }
  }
}
```

完整配置项请参考文件内注释。

## 许可证

本项目整体采用 MIT 许可证。
服务端部分基于 [kuole-o/dailyhot-api](https://github.com/kuole-o/dailyhot-api) 修改，其原始许可证为 MIT。
客户端部分代码同样使用 MIT 许可证。详情请参阅各子目录下的 `LICENSE` 文件（如有）。

## 致谢

- [DailyHotApi](https://github.com/kuole-o/dailyhot-api) 提供了强大的聚合接口支持。
- [PySide6](https://wiki.qt.io/Qt_for_Python) 提供了优秀的 GUI 框架。
