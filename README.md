<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LangChain-0.3+-green?logo=langchain" alt="LangChain">
  <img src="https://img.shields.io/badge/DeepSeek-v4--flash-purple" alt="DeepSeek">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

<h1 align="center">🎓 SXIST IES — 山西科技学院智能招生助手</h1>

<p align="center">
  <strong>AI-Powered Admissions Q&A Agent</strong><br>
  基于 LangGraph + DeepSeek 的多轮对话智能体，深度爬取全校 15+ 官方站点
</p>

---

## ✨ 亮点

- **零幻觉数据** — 所有回答均基于官网实时抓取，绝不胡编乱造
- **三级深爬** — 首页 → 子页面 → 教师详情/文章正文，逐级穿透
- **JS SPA 穿透** — 招生站子页面为纯 JS 渲染，独创三层缓存架构绕过
- **多轮记忆** — 基于 InMemorySaver 的对话状态持久化
- **13 学院全覆盖** — 关键词自动匹配对应学院官网，教师研究方向逐个深扒

---

## 🏗️ 架构

```
用户输入 (agent_main.py)
    │
    ▼
┌──────────────────────────────────────────┐
│  Agent (agent_client.py)                 │
│  ┌────────────┐  ┌───────────────────┐   │
│  │ DeepSeek   │  │ InMemorySaver     │   │
│  │ v4-flash   │  │ (多轮记忆)         │   │
│  └────────────┘  └───────────────────┘   │
│       │                                   │
│       ▼                                   │
│  ┌────────────────────────────────────┐   │
│  │ Tool: search_institute_message     │   │
│  │ (agent_tool.py)                    │   │
│  └────────┬───────────────────────────┘   │
└───────────┼───────────────────────────────┘
            │
    ┌───────┴───────┬──────────────┐
    ▼               ▼              ▼
┌────────┐   ┌──────────┐   ┌──────────────┐
│ 主站    │   │ 13个     │   │ 本科招生网    │
│ www.   │   │ 二级学院  │   │ bkzs.        │
│ sxist  │   │ 子站     │   │ sxist        │
└───┬────┘   └────┬─────┘   └──────┬───────┘
    │              │                │
    ▼              ▼                ▼
┌──────────────────────────────────────────┐
│  数据获取三层策略                          │
│  L1: requests 直接抓 (服务端渲染)          │
│  L2: 子链接发现 → 逐页深爬                 │
│  L3: admissions_cache.py (预渲染缓存)      │
└──────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.12+
- DeepSeek API Key

### 安装

```bash
git clone <your-repo-url>
cd SXIST_IES_2026

pip install -r requirements.txt
```

### 第三方依赖清单

| 包名 | 版本要求 | 用途 | 使用位置 |
|------|----------|------|----------|
| `langchain` | ≥0.3 | Agent 编排、`create_agent`、`@tool` 装饰器、`HumanMessage` | `agent_client.py`, `agent_main.py`, `agent_tool.py` |
| `langchain-deepseek` | ≥0.1 | DeepSeek Chat Model 集成 | `agent_client.py` |
| `langgraph` | ≥0.2 | Agent 流式执行、`InMemorySaver` 多轮记忆、`checkpointer` | `agent_client.py`, `agent_main.py` |
| `python-dotenv` | ≥1.0 | `.env` 环境变量加载（API Key） | `agent_client.py` |
| `requests` | ≥2.28 | HTTP 网页抓取，15s 超时兜底 | `agent_tool.py`, `check_urls.py` |
| `beautifulsoup4` | ≥4.12 | HTML 解析，CSS 选择器内容提取 | `agent_tool.py`, `check_urls.py` |

> **标准库依赖（无需安装）**：`os`, `urllib.parse`

> 全部 6 个第三方包，无一冗余。`langchain` 生态三个包各司其职（编排 / 模型 / 图流），`requests` + `bs4` 负责爬取，`python-dotenv` 管理密钥。

### 配置

创建 `.env` 文件：

```env
LLM_API_KEY="sk-your-deepseek-api-key"
LLM_ID="deepseek-v4-flash"
LLM_BASE_URL="https://api.deepseek.com"
```

### 运行

```bash
python agent_main.py
```

```
==================================================
山西科技学院招生智能体
输入 'quit' 或 'exit' 退出对话
==================================================

你: 大数据学院有哪些老师从事自然语言处理研究？
智能体: 根据山西科技学院大数据与计算机科学学院官网公布的"专业教师"信息...

你: 2025年在山东省各专业录取平均分是多少？
智能体: | 计算机科学与技术 | 516.5 | 电气工程及其自动化 | 501.0 | ...
```

---

## 📂 项目结构

```
SXIST_IES_2026/
├── agent_main.py          # 交互式入口，while True 多轮对话
├── agent_client.py        # Agent 初始化：模型 + tool + InMemorySaver
├── agent_tool.py          # 核心工具：15 站点深度爬取 + 招生专项处理
├── admissions_cache.py    # 招生站 JS SPA 预渲染数据缓存
├── test_full.py           # 端到端回归测试
├── .env                   # API Key 配置（不提交）
└── .idea/                 # PyCharm 项目配置
```

### 文件职责

| 文件 | 行数 | 职责 |
|------|------|------|
| `agent_main.py` | ~30 | 交互循环，流式输出过滤 ToolMessage |
| `agent_client.py` | ~40 | ChatDeepSeek 初始化，关闭 thinking mode，tool 注册 |
| `agent_tool.py` | ~280 | 核心爬取引擎：URL 匹配、三级深爬、缓存调度 |
| `admissions_cache.py` | ~250 | 6 个招生子栏目 + 章程全文 + 分省分专业录取分数 |

---

## 🔧 核心设计

### 1. Thinking Mode 关闭

DeepSeek v4-flash 默认启用思考模式，`reasoning_content` 在多轮对话中必须回传。通过 `extra_body` 直接关闭：

```python
ChatDeepSeek(
    model="deepseek-v4-flash",
    extra_body={"thinking": {"type": "disabled"}},  # 关闭思考，省 token 保速度
)
```

### 2. 学院站点自动匹配

```
用户输入 "大数据学院有哪些专业？"
    │
    ├── KEYWORD_MAP["大数据"] → "大数据与计算机科学学院"
    ├── INSTITUTE_URLS["大数据与计算机科学学院"] → "https://dsjxy.sxist.edu.cn/"
    └── _fetch_web_content → 首页 → 子链接(专业设置/学院简介/...) → 逐页深爬
```

### 3. 教师研究方向深度爬取

```
首页 → 发现"专业教师"子页面
    → _discover_teacher_links()
        ├── 匹配 /info/ 路径
        ├── 中文人名检测 (2-4 汉字)
        └── 排除导航词 ("首页""更多"等)
    → 逐页抓取每位教师详情
    → 提取研究方向字段
```

### 4. JS SPA 招生站穿透

```
bkzs.sxist.edu.cn 的 6 个子页面全部是 JS 空壳 (<script>location.href=...)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
               L1: 首页 SSR     L2: 主站文章     L3: 预抓取缓存
               13KB 内容就绪    服务端渲染       录取分数 / 章程全文
```

`admissions_cache.py` 包含 WebFetch 预渲染的完整数据：
- 招生简章（5 年）
- 招生章程（6 年，含全文）
- 招生计划（8 条记录）
- 招生政策（10 条公告）
- 历年录取（2021-2025 分省分专业）
- 专业介绍（10+ 专业详情）
- **2024/2025 年山东省分专业录取分数（最高分/最低分/平均分）**

---

## 🧪 测试

```bash
python test_full.py
```

端到端回归测试覆盖 4 个核心场景：

| # | 查询 | 预期 |
|---|------|------|
| 1 | 大数据学院 NLP 教师 | 列出 6 位教师研究方向，指出无 NLP 专项 |
| 2 | 2025 年山东省招生计划 | 列出 13 个专业 + 28 人总额 |
| 3 | 山东省各专业平均分 | 13 个专业完整分数表（含最高/最低/平均） |
| 4 | 2025 年招生章程 | 九章全文总结（含调档比例/录取规则/奖助办法） |

---

## 🛠️ 技术栈

| 组件 | 选型 | 原因 |
|------|------|------|
| LLM | DeepSeek v4-flash | 高性价比，中文理解强 |
| 框架 | LangGraph + LangChain | Agent 编排 + 工具注册 |
| 记忆 | InMemorySaver | 多轮对话上下文保持 |
| 爬虫 | requests + BeautifulSoup | 轻量级，15s 超时兜底 |
| SPA 穿透 | admissions_cache.py | 预渲染缓存绕过 JS 渲染 |

---

## 📄 License

MIT © 2025

---

<p align="center">
  <sub>Built with ❤️ for Shanxi Institute of Science and Technology</sub>
</p>
