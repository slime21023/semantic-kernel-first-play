# Semantic Kernel Agent Examples 🤖

## 介紹 (Introduction)

這個專案展示了如何使用 Python Semantic Kernel 建立智能代理（Agent）。範例從基本概念開始，逐步深入到更複雜的應用場景。

This project demonstrates how to build intelligent agents using Python Semantic Kernel. Examples progress from basic concepts to more complex use cases.

## 專案結構 (Project Structure)

```
├── examples/                   # 範例程式碼目錄
│   ├── 01_basic_setup.py       # 基本設定與 Kernel 初始化
│   ├── 02_simple_agent.py      # 簡單代理建立
│   ├── 03_plugins.py           # 使用與建立外掛
│   ├── 04_agent_memory.py      # 代理記憶功能
│   ├── 05_orchestration.py     # 代理協作
│   ├── 06_chat_agent.py        # 聊天代理
│   └── utils/                  # 共用工具   
├── .env                       # 環境變數
├── pyproject.toml             # 專案依賴配置
└── README.md                  # 專案說明
```

## 安裝指南 (Installation)

本專案使用 `uv` 進行套件管理。確保你已安裝 Python 3.12+ 和 uv。

```bash
# 初始化虛擬環境
python -m uv venv

# 啟動虛擬環境
# Windows
.venv\Scripts\activate
# MacOS/Linux
source .venv/bin/activate

# 安裝依賴
python -m uv pip install -e .
```

## 準備工作 (Prerequisites)

1. 複製 `.env.example` 到 `.env`：
   ```bash
   cp .env.example .env
   ```

2. 在 `.env` 檔案中設置你的 API 金鑰：
   ```
   GITHUB_TOKEN=your_github_token
   ```

## 運行範例 (Running Examples)

```bash
# 執行基本設置範例
python examples/01_basic_setup.py

# 執行簡單代理範例
python examples/02_simple_agent.py
```

## 學習路徑 (Learning Path)

1. **基本設置** - 了解如何初始化 Semantic Kernel 和設置基本組件
2. **簡單代理** - 創建您的第一個 AI 代理
3. **外掛系統** - 擴展代理功能使用外掛
4. **代理記憶** - 增加記憶功能
5. **協作系統** - 多代理協作
6. **聊天代理** - 創建對話式體驗

## 參考資源 (Resources)

- [Semantic Kernel 官方文件](https://github.com/microsoft/semantic-kernel/tree/main/python)
- [Microsoft AI Agents for Beginners](https://github.com/microsoft/AI-Agents-for-Beginners)
