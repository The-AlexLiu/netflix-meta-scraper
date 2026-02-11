# Netflix Meta Scraper (高级版) 🎬

![Project Banner](https://img.shields.io/badge/Status-Stable-success) ![License](https://img.shields.io/badge/License-MIT-blue) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB)

一个高保真、自动化的工具，用于抓取 **Netflix "New to Watch"** 栏目的元数据和电影海报。本项目拥有**高级 Web 界面**，融合了电影级美学设计、实时进度跟踪和智能日期过滤功能。

## ✨ 核心功能

- **🎥 高级 Web UI**：令人惊叹的 Netflix 风格深色模式界面，配备毛玻璃特效 (Glassmorphism) 和丝滑的交互动画。
- **📅 智能日期过滤**：支持仅抓取特定日期范围内的内容（例如 `2026/02/09 - 2026/02/15`）。爬虫会在遇到不再范围内的日期时自动停止，节省时间。
- **⚡ 实时反馈系统**：终端日志实时流式传输到浏览器，配备可视化进度条和运行状态呼吸灯。
- **📦 智能净画导出**：一键下载 Zip 压缩包，系统会自动过滤，**仅包含**您当前筛选结果的图片和数据。告别文件混乱！
- **🛡️ 强力抓取内核**：基于 Playwright 构建，能够可靠处理动态加载内容和反爬策略。

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+ (用于前端运行)

### 安装步骤

1.  **克隆仓库**

    ```bash
    git clone https://github.com/The-AlexLiu/netflix-meta-scraper.git
    cd netflix-meta-scraper
    ```

2.  **安装后端依赖**

    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **安装前端依赖**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

### 使用方法

#### 方法 1: 高级 Web 界面 (推荐)

1.  **启动后端 API**

    ```bash
    python3 app.py
    ```

    _服务器运行在 http://localhost:8000_

2.  **启动前端 UI** (打开新的终端窗口)

    ```bash
    cd frontend
    npm run dev
    ```

    _UI 界面运行在 http://localhost:5173_

3.  **打开浏览器**：访问 `http://localhost:5173`。
4.  **配置与运行**：设置开始/结束日期，点击闪电图标 **INITIATE** 按钮开始抓取。
5.  **导出数据**：抓取完成后，点击 **"Download All"** 下载打包好的纯净数据。

#### 方法 2: 命令行模式 (高级)

您也可以直接通过命令行运行爬虫：

```bash
python3 netflix_scraper.py --start 2026/02/09 --end 2026/02/15
```

## 📂 输出文件结构

工具将生成以下文件：

- `images/`: 高清电影海报 (文件名格式：`Titles-{UUID}.jpg`)。
- `netflix_records.csv`: 结构化的元数据 (标题, 上映日期, 文件名, 观看链接)。
- `netflix_scraper_export.zip`: 通过 Web UI 生成的纯净数据压缩包。

## 🛠️ 技术栈

- **后端**: FastAPI, Python, Playwright
- **前端**: React, Vite, Tailwind CSS v4, Framer Motion
- **设计**: "UI/UX Pro Max" 设计系统 (Cinematic Dark Mode)

## 📄 许可证

MIT License. 仅供教育和个人学习使用。
