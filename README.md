# Netflix Meta-Scraper 🎬

A powerful Python tool to scrape movie posters (450x630), release dates, and synopses from the [Netflix Newsroom](https://about.netflix.com/zh_cn/new-to-watch).

[English](#english) | [中文说明](#chinese)

---

<a name="chinese"></a>

## 中文说明

### 功能特点

- **高清海报抓取**：自动下载 450x630 比例的高清海报图片。
- **全元数据提取**：包括 影片标题、精准上线日期、内容简述 以及 官方观看链接。
- **自动化交互**：基于 Playwright 模拟浏览器操作，支持分页抓取和延迟加载处理。
- **结构化输出**：自动生成 `netflix_records.csv` 表格，方便数据分析和管理。
- **断点续传/去重**：支持本地去重，避免重复下载相同影片的信息。

### 安装步骤

1. **安装依赖环境**：
   ```bash
   pip install -r requirements.txt
   ```
2. **安装浏览器驱动**：
   ```bash
   playwright install chromium
   ```

### 使用指南

直接运行主程序脚本：

```bash
python3 netflix_scraper.py
```

抓取完成后，可在 `images/` 目录下查看海报，在 `netflix_records.csv` 中查看详细信息。

---

<a name="english"></a>

## English Description

### Features

- **High-Res Poster Scraper**: Automatically downloads 450x630 HD movie posters.
- **Full Metadata Extraction**: Captures Title, Release Date, Synopsis, and Watch URLs.
- **Browser Automation**: Uses Playwright to handle infinite scroll, dynamic loading (hover), and pagination.
- **Export to CSV**: Generates `netflix_records.csv` for easy data consumption.
- **Deduplication**: Skips already processed items to save time and bandwidth.

### Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Install Chromium**:
   ```bash
   playwright install chromium
   ```

### Usage

Run the script:

```bash
python3 netflix_scraper.py
```

Find your results in the `images/` folder and `netflix_records.csv` file.

---

### License

MIT License. Feel free to use and contribute!
