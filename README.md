<div align="center">

# 🤖 ModelPick-AI

**轻量级终端AI模型智能推荐引擎**
**Lightweight Terminal AI Model Intelligent Recommendation Engine**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Models: 56+](https://img.shields.io/badge/Models-56%2B-orange.svg)](data/models.json)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero_Runtime-success.svg)]()
[![Tests: 38](https://img.shields.io/badge/Tests-38%20Passed-brightgreen.svg)](tests/)
[![Cross Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

**[简体中文](#-简体中文) | [繁體中文](#-繁體中文) | [English](#-english)**

</div>

---

## 🇨🇳 简体中文

### 🎉 项目介绍

**ModelPick-AI** 是一款零外部API依赖的轻量级终端AI模型智能推荐引擎。它能够自动检测你的硬件配置（CPU、GPU、内存、磁盘），从内置的 **56+ 主流开源大语言模型数据库** 中，智能推荐最适合你机器运行的本地AI模型。

**💡 灵感来源**：随着本地大语言模型生态的爆发式增长，开发者面临"模型太多、不知道选哪个"的痛点。ModelPick-AI 正是为解决这一问题而生——一个命令，告诉你"你的电脑能跑什么模型、哪个最好、怎么跑起来"。

**🌟 自研差异化亮点**：
- **国产模型全覆盖**：内置通义千问、智谱GLM、DeepSeek、百川、MiniCPM、InternLM等国产模型，适配国内开发者需求
- **中英文双语基准测试**：同时支持 MMLU/C-Eval/CMMLU/GAOKAO-Bench 等中英文基准，推荐更精准
- **场景化智能推荐**：不只是按硬件匹配，还按使用场景（编程、对话、写作、数学、多模态）推荐最合适的模型
- **完全离线运行**：所有模型数据内置，无需联网即可完成推荐
- **多平台一键安装**：自动生成 Ollama / ModelScope / HuggingFace 的安装命令

---

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **硬件自动检测** | 自动检测 CPU（型号/架构/核心数）、GPU（NVIDIA/AMD/Apple Silicon/Intel）、内存、磁盘空间 |
| 🧠 **智能推荐引擎** | 综合兼容性评分（40%）+ 性能基准评分（60%）的加权算法，精准推荐 |
| 🇨🇳 **国产模型支持** | 通义千问(Qwen)全系列、智谱(GLM)、DeepSeek、百川、MiniCPM、InternLM、Yi 等 |
| 🌍 **国际模型支持** | Llama 3.x、Mistral、Phi-3、Gemma 2、CodeLlama、Falcon、Zephyr 等 |
| 🎯 **场景化推荐** | 编程助手、知识问答、文案写作、数学推理、多模态、对话聊天 6 大场景 |
| 📊 **双语基准测试** | MMLU、HumanEval、GSM8K（英文）+ C-Eval、CMMLU、GAOKAO-Bench（中文） |
| 🖥️ **美观TUI界面** | 基于 Rich 库的精美终端界面，表格、面板、进度条一应俱全 |
| 📤 **多格式导出** | 支持 JSON / Markdown / CSV 三种格式导出推荐结果 |
| 📡 **一键安装命令** | 自动生成 Ollama / ModelScope / HuggingFace 安装命令 |
| 🔌 **零运行时依赖** | 仅需 Rich + Click，无 ML 框架、无 GPU 驱动依赖 |
| 📱 **跨平台兼容** | 完美支持 Windows / macOS / Linux 三大平台 |
| 📦 **完全离线可用** | 内置 56+ 模型完整数据库，断网也能用 |

---

### 🚀 快速开始

#### 环境要求

- **Python** >= 3.8
- **操作系统**：Windows / macOS / Linux
- **依赖**：Rich、Click（自动安装）

#### 安装

```bash
# 克隆仓库 / Clone the repository
git clone https://github.com/gitstq/ModelPick-AI.git
cd ModelPick-AI

# 安装依赖 / Install dependencies
pip install -r requirements.txt

# 可选：以开发模式安装（获得 modelpick 命令） / Optional: install in dev mode
pip install -e .
```

#### 一键运行

```bash
# 默认运行：检测硬件 + 推荐 Top 10 模型
modelpick

# 或使用模块方式运行 / Or run as module
python -m modelpick_ai
```

---

### 📖 详细使用指南

#### 1. 硬件检测

```bash
# 检测当前硬件配置
modelpick detect
```

输出示例：
```
╭──────────────────────────── CPU ────────────────────────────╮
│ 型号: Apple M2 Pro                                          │
│ 架构: arm64                                                 │
│ 核心数: 10                                                  │
╰────────────────────────────────────────────────────────────╯
╭──────────────────────────── GPU ────────────────────────────╮
│ 型号: Apple M2 Pro GPU                                     │
│ 显存: 16.0 GB                                              │
╰────────────────────────────────────────────────────────────╯
```

#### 2. 智能推荐

```bash
# 默认推荐 Top 10
modelpick recommend

# 按场景推荐（编程/对话/写作/数学/多模态/推理）
modelpick recommend --scene coding

# 限制最大参数量（B）
modelpick recommend --max-params 7

# 指定显示数量
modelpick recommend --top 5

# 组合使用
modelpick recommend --scene math --max-params 14 --top 3
```

#### 3. 模型搜索

```bash
# 按关键词搜索模型
modelpick search qwen
modelpick search deepseek
modelpick search llama
```

#### 4. 模型详情

```bash
# 查看模型详细信息
modelpick detail qwen2.5-7b
modelpick detail deepseek-v3
```

#### 5. 模型列表

```bash
# 列出所有模型
modelpick list

# 按场景过滤
modelpick list --scene coding
modelpick list --scene multimodal
```

#### 6. 基准测试排行榜

```bash
# 查看基准测试排行榜
modelpick benchmark
```

#### 7. 结果导出

```bash
# 导出为 JSON
modelpick export --format json

# 导出为 Markdown
modelpick export --format markdown

# 导出为 CSV
modelpick export --format csv

# 导出到指定文件
modelpick export --format json --output results.json
```

---

### 💡 设计思路与迭代规划

#### 设计理念
- **零门槛**：无需任何 ML 知识，一个命令即可获得专业级模型推荐
- **离线优先**：所有数据内置，不依赖任何外部 API，保护用户隐私
- **场景驱动**：不同场景需要不同模型，不只是"谁的分数高就推荐谁"
- **国产优先**：为中文开发者优化，内置国产模型和中文基准测试

#### 技术选型
- **Python**：开发者生态最成熟，跨平台兼容性最好
- **Rich**：Python 终端 UI 的事实标准，表格/面板/进度条开箱即用
- **Click**：Python CLI 框架的最佳实践，命令组织清晰优雅
- **JSON 数据库**：轻量、可读、易维护，无需数据库引擎

#### 后续迭代计划
- [ ] 🔄 自动检测已安装的 Ollama 模型
- [ ] 📊 实测基准模式（下载模型后自动跑 benchmark）
- [ ] 🌐 模型在线数据更新（可选联网模式）
- [ ] 🎨 交互式 TUI 选择界面
- [ ] 📱 Docker 镜像发布
- [ ] 🇯🇵 日语/韩语界面支持

---

### 📦 安装与部署

#### pip 安装（推荐）

```bash
pip install -e .
```

#### 直接运行

```bash
git clone https://github.com/gitstq/ModelPick-AI.git
cd ModelPick-AI
pip install -r requirements.txt
python -m modelpick_ai
```

#### 兼容环境

| 环境 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Python | 3.8 | 3.10+ |
| Windows | 10 | 11 |
| macOS | 10.15 | 12+ |
| Linux | Ubuntu 20.04 | Ubuntu 22.04+ |

---

### 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: 添加你的特性"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

**提交规范**：
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

### 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

## 🇹🇼 繁體中文

### 🎉 專案介紹

**ModelPick-AI** 是一款零外部 API 依賴的輕量級終端 AI 模型智慧推薦引擎。它能夠自動檢測你的硬體配置（CPU、GPU、記憶體、磁碟），從內建的 **56+ 主流開源大語言模型資料庫** 中，智慧推薦最適合你機器運行的本地 AI 模型。

**💡 靈感來源**：隨著本地大語言模型生態的爆發式增長，開發者面臨「模型太多、不知道選哪個」的痛點。ModelPick-AI 正是為解決這一問題而生——一個命令，告訴你「你的電腦能跑什麼模型、哪個最好、怎麼跑起來」。

**🌟 自研差異化亮點**：
- **國產模型全覆蓋**：內建通義千問、智譜 GLM、DeepSeek、百川、MiniCPM、InternLM 等國產模型，適配國內開發者需求
- **中英文雙語基準測試**：同時支援 MMLU/C-Eval/CMMLU/GAOKAO-Bench 等中英文基準，推薦更精準
- **場景化智慧推薦**：不只是按硬體匹配，還按使用場景（程式設計、對話、寫作、數學、多模態）推薦最合適的模型
- **完全離線運行**：所有模型資料內建，無需聯網即可完成推薦
- **多平台一鍵安裝**：自動生成 Ollama / ModelScope / HuggingFace 的安裝命令

---

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **硬體自動檢測** | 自動檢測 CPU（型號/架構/核心數）、GPU（NVIDIA/AMD/Apple Silicon/Intel）、記憶體、磁碟空間 |
| 🧠 **智慧推薦引擎** | 綜合相容性評分（40%）+ 效能基準評分（60%）的加權演算法，精準推薦 |
| 🇨🇳 **國產模型支援** | 通義千問(Qwen)全系列、智譜(GLM)、DeepSeek、百川、MiniCPM、InternLM、Yi 等 |
| 🌍 **國際模型支援** | Llama 3.x、Mistral、Phi-3、Gemma 2、CodeLlama、Falcon、Zephyr 等 |
| 🎯 **場景化推薦** | 程式設計助手、知識問答、文案寫作、數學推理、多模態、對話聊天 6 大場景 |
| 📊 **雙語基準測試** | MMLU、HumanEval、GSM8K（英文）+ C-Eval、CMMLU、GAOKAO-Bench（中文） |
| 🖥️ **美觀 TUI 介面** | 基於 Rich 函式庫的精美終端介面，表格、面板、進度條一應俱全 |
| 📤 **多格式匯出** | 支援 JSON / Markdown / CSV 三種格式匯出推薦結果 |
| 📡 **一鍵安裝命令** | 自動生成 Ollama / ModelScope / HuggingFace 安裝命令 |
| 🔌 **零運行時依賴** | 僅需 Rich + Click，無 ML 框架、無 GPU 驅動依賴 |
| 📱 **跨平台相容** | 完美支援 Windows / macOS / Linux 三大平台 |
| 📦 **完全離線可用** | 內建 56+ 模型完整資料庫，斷網也能用 |

---

### 🚀 快速開始

#### 環境要求

- **Python** >= 3.8
- **作業系統**：Windows / macOS / Linux
- **依賴**：Rich、Click（自動安裝）

#### 安裝

```bash
# 克隆倉庫 / Clone the repository
git clone https://github.com/gitstq/ModelPick-AI.git
cd ModelPick-AI

# 安裝依賴 / Install dependencies
pip install -r requirements.txt

# 可選：以開發模式安裝（獲得 modelpick 命令）
pip install -e .
```

#### 一鍵運行

```bash
# 預設運行：檢測硬體 + 推薦 Top 10 模型
modelpick

# 或使用模組方式運行
python -m modelpick_ai
```

---

### 📖 詳細使用指南

#### 1. 硬體檢測

```bash
# 檢測當前硬體配置
modelpick detect
```

#### 2. 智慧推薦

```bash
# 預設推薦 Top 10
modelpick recommend

# 按場景推薦（程式設計/對話/寫作/數學/多模態/推理）
modelpick recommend --scene coding

# 限制最大參數量（B）
modelpick recommend --max-params 7

# 指定顯示數量
modelpick recommend --top 5

# 組合使用
modelpick recommend --scene math --max-params 14 --top 3
```

#### 3. 模型搜尋

```bash
# 按關鍵字搜尋模型
modelpick search qwen
modelpick search deepseek
modelpick search llama
```

#### 4. 模型詳情

```bash
# 查看模型詳細資訊
modelpick detail qwen2.5-7b
modelpick detail deepseek-v3
```

#### 5. 模型列表

```bash
# 列出所有模型
modelpick list

# 按場景過濾
modelpick list --scene coding
modelpick list --scene multimodal
```

#### 6. 基準測試排行榜

```bash
# 查看基準測試排行榜
modelpick benchmark
```

#### 7. 結果匯出

```bash
# 匯出為 JSON
modelpick export --format json

# 匯出為 Markdown
modelpick export --format markdown

# 匯出為 CSV
modelpick export --format csv

# 匯出到指定檔案
modelpick export --format json --output results.json
```

---

### 💡 設計思路與迭代規劃

#### 設計理念
- **零門檻**：無需任何 ML 知識，一個命令即可獲得專業級模型推薦
- **離線優先**：所有資料內建，不依賴任何外部 API，保護使用者隱私
- **場景驅動**：不同場景需要不同模型，不只是「誰的分數高就推薦誰」
- **國產優先**：為中文開發者優化，內建國產模型和中文基準測試

#### 後續迭代計畫
- [ ] 🔄 自動檢測已安裝的 Ollama 模型
- [ ] 📊 實測基準模式（下載模型後自動跑 benchmark）
- [ ] 🌐 模型線上資料更新（可選聯網模式）
- [ ] 🎨 互動式 TUI 選擇介面
- [ ] 📱 Docker 映像檔發布
- [ ] 🇯🇵 日語/韓語介面支援

---

### 📦 安裝與部署

#### 相容環境

| 環境 | 最低版本 | 推薦版本 |
|------|---------|---------|
| Python | 3.8 | 3.10+ |
| Windows | 10 | 11 |
| macOS | 10.15 | 12+ |
| Linux | Ubuntu 20.04 | Ubuntu 22.04+ |

---

### 🤝 貢獻指南

歡迎貢獻！請遵循以下步驟：

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m "feat: 新增你的特性"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

**提交規範**：
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具相關

---

### 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

## 🇬🇧 English

### 🎉 Project Introduction

**ModelPick-AI** is a lightweight terminal AI model intelligent recommendation engine with zero external API dependencies. It automatically detects your hardware configuration (CPU, GPU, RAM, Disk) and intelligently recommends the best local AI models to run on your machine from a built-in database of **56+ mainstream open-source LLMs**.

**💡 Inspiration**: With the explosive growth of the local LLM ecosystem, developers face the pain point of "too many models, don't know which to choose." ModelPick-AI was born to solve this problem — one command tells you "what models your computer can run, which is best, and how to get started."

**🌟 Differentiation Highlights**:
- **Full Chinese Model Coverage**: Built-in support for Qwen, GLM, DeepSeek, Baichuan, MiniCPM, InternLM, and more
- **Bilingual Benchmarks**: Supports both MMLU/C-Eval/CMMLU/GAOKAO-Bench (Chinese) and MMLU/HumanEval/GSM8K (English)
- **Scenario-Based Recommendations**: Not just hardware matching — recommends models based on use cases (coding, chat, writing, math, multimodal)
- **Fully Offline**: All model data is built-in; no internet required
- **One-Click Install Commands**: Auto-generates Ollama / ModelScope / HuggingFace install commands

---

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Auto Hardware Detection** | Detects CPU (model/arch/cores), GPU (NVIDIA/AMD/Apple Silicon/Intel), RAM, and Disk space |
| 🧠 **Smart Recommendation Engine** | Weighted algorithm combining compatibility score (40%) + performance benchmark score (60%) |
| 🇨🇳 **Chinese Model Support** | Qwen full series, GLM, DeepSeek, Baichuan, MiniCPM, InternLM, Yi, and more |
| 🌍 **International Model Support** | Llama 3.x, Mistral, Phi-3, Gemma 2, CodeLlama, Falcon, Zephyr, and more |
| 🎯 **Scenario-Based Recommendations** | 6 scenarios: Coding, Chat, Writing, Math, Multimodal, Reasoning |
| 📊 **Bilingual Benchmarks** | MMLU, HumanEval, GSM8K (EN) + C-Eval, CMMLU, GAOKAO-Bench (CN) |
| 🖥️ **Beautiful TUI Interface** | Rich-powered terminal UI with tables, panels, and progress bars |
| 📤 **Multi-Format Export** | Export results in JSON / Markdown / CSV formats |
| 📡 **One-Click Install Commands** | Auto-generates Ollama / ModelScope / HuggingFace install commands |
| 🔌 **Zero Runtime Dependencies** | Only requires Rich + Click — no ML frameworks, no GPU driver dependencies |
| 📱 **Cross-Platform** | Full support for Windows / macOS / Linux |
| 📦 **Fully Offline Capable** | Built-in database of 56+ models — works without internet |

---

### 🚀 Quick Start

#### Requirements

- **Python** >= 3.8
- **OS**: Windows / macOS / Linux
- **Dependencies**: Rich, Click (auto-installed)

#### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/ModelPick-AI.git
cd ModelPick-AI

# Install dependencies
pip install -r requirements.txt

# Optional: install in dev mode (gets the `modelpick` command)
pip install -e .
```

#### Run

```bash
# Default: detect hardware + recommend Top 10 models
modelpick

# Or run as module
python -m modelpick_ai
```

---

### 📖 Detailed Usage Guide

#### 1. Hardware Detection

```bash
# Detect current hardware configuration
modelpick detect
```

#### 2. Smart Recommendations

```bash
# Default: recommend Top 10
modelpick recommend

# By scenario (coding/chat/writing/math/multimodal/reasoning)
modelpick recommend --scene coding

# Limit max parameter count (in Billions)
modelpick recommend --max-params 7

# Specify number of results
modelpick recommend --top 5

# Combine options
modelpick recommend --scene math --max-params 14 --top 3
```

#### 3. Model Search

```bash
# Search models by keyword
modelpick search qwen
modelpick search deepseek
modelpick search llama
```

#### 4. Model Details

```bash
# View detailed model information
modelpick detail qwen2.5-7b
modelpick detail deepseek-v3
```

#### 5. Model List

```bash
# List all models
modelpick list

# Filter by scenario
modelpick list --scene coding
modelpick list --scene multimodal
```

#### 6. Benchmark Leaderboard

```bash
# View benchmark leaderboard
modelpick benchmark
```

#### 7. Export Results

```bash
# Export as JSON
modelpick export --format json

# Export as Markdown
modelpick export --format markdown

# Export as CSV
modelpick export --format csv

# Export to specific file
modelpick export --format json --output results.json
```

---

### 💡 Design Philosophy & Roadmap

#### Design Principles
- **Zero Barrier**: No ML knowledge required — one command for professional-grade recommendations
- **Offline First**: All data built-in, no external API dependencies, privacy-preserving
- **Scenario-Driven**: Different scenarios need different models — not just "highest score wins"
- **Chinese-First**: Optimized for Chinese developers with domestic models and Chinese benchmarks

#### Technology Choices
- **Python**: Most mature developer ecosystem, best cross-platform compatibility
- **Rich**: De facto standard for Python terminal UIs — tables, panels, progress bars out of the box
- **Click**: Best practice for Python CLI frameworks — clean, elegant command organization
- **JSON Database**: Lightweight, readable, easy to maintain — no database engine needed

#### Roadmap
- [ ] 🔄 Auto-detect installed Ollama models
- [ ] 📊 Live benchmark mode (auto-run benchmarks after model download)
- [ ] 🌐 Online model data updates (optional connected mode)
- [ ] 🎨 Interactive TUI selection interface
- [ ] 📱 Docker image release
- [ ] 🇯🇵 Japanese / Korean UI support

---

### 📦 Installation & Deployment

#### Compatible Environments

| Environment | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.8 | 3.10+ |
| Windows | 10 | 11 |
| macOS | 10.15 | 12+ |
| Linux | Ubuntu 20.04 | Ubuntu 22.04+ |

---

### 🤝 Contributing Guide

Contributions are welcome! Follow these steps:

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Submit a **Pull Request**

**Commit Convention**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tooling related

---

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by [gitstq](https://github.com/gitstq)**

⭐ If you find this project helpful, please give it a star!

</div>
