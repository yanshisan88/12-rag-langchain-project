# Campus RAG System —— 校园知识库智能问答系统

基于 **RAG（检索增强生成）** 技术打造的校园生活知识库问答系统。系统以校园文档（宿舍管理、食堂、图书馆、奖学金、选课、校园卡等）作为知识库，用户上传 Markdown / 文本文档后，系统自动完成文档解析、切分、向量化并写入向量数据库；当用户提问时，先通过向量检索召回最相关的文档片段，再交由大语言模型（LLM）基于这些上下文生成准确、可追溯来源的回答。

它不是一个"背题库"的聊天机器人，而是把**检索（Retrieval）+ 生成（Generation）**组合在一起，让大模型的回答"有据可依"，有效减少幻觉（编造信息），并且每条回答都能给出引用的文档来源。

---

## ✨ 功能特性

- **📄 文档知识库管理**
  - 支持上传 `.md` / `.txt` 文档，自动解析、切分、向量化入库
  - 文档状态机：`pending → indexing → ready | error`，全程可追踪
  - 文档列表 / 删除（删除需管理员权限）

- **🤖 智能问答（RAG）**
  - 基于检索增强生成，回答严格限定在文档上下文范围内
  - 回答附带**来源引用**（章节、小节、相似度评分、原文片段）
  - 上下文不足时如实说明"文档中没有相关信息"，拒绝编造

- **💬 多轮会话管理**
  - 会话（Session）与消息（Message）持久化，支持多轮对话历史
  - 自动为"新对话"生成标题（取首条问题前 10 字）
  - 会话列表 / 详情 / 删除

- **⚡ 流式输出（SSE）**
  - 基于 Server-Sent Events 实现 token 级流式返回，前端打字机效果
  - 三种事件：`token`（文本片段）、`source`（来源）、`done`（结束）

- **🔐 用户认证与权限**
  - 邮箱注册 / 登录，密码使用 bcrypt 加密
  - JWT 双令牌（access token + refresh token），支持令牌刷新
  - 角色权限：`student`（学生）/ `admin`（管理员）

- **🔌 MCP Server 集成**
  - 将知识库问答能力暴露为 MCP（Model Context Protocol）工具
  - 提供 `rag_query`（知识库提问）、`list_documents`（列出文档）两个工具

- **🧠 多 LLM 提供商可切换**
  - 支持 DeepSeek / OpenAI / Ollama，通过环境变量一键切换

---

## 🧱 技术栈

| 分类 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 高性能异步 Web 框架 |
| ORM | SQLAlchemy 2.0（async） | 异步数据库访问 |
| 关系型数据库 | PostgreSQL | 存储用户、会话、消息、文档元数据 |
| 向量数据库 | Qdrant | 存储文档向量，进行相似度检索 |
| RAG 编排 | LangChain | 组织加载、切分、嵌入、检索、生成全链路 |
| 嵌入模型 | BAAI/bge-base-zh | 中文语义向量模型（768 维） |
| LLM | DeepSeek / OpenAI / Ollama | 可配置的语言模型 |
| 认证 | python-jose (JWT) + bcrypt | 令牌鉴权与密码加密 |
| 流式 | sse-starlette | SSE 协议流式响应 |
| MCP | mcp (FastMCP) | 暴露 MCP 工具 |
| 包管理 | uv | 依赖管理与虚拟环境 |

---

## 📁 项目结构

```
12-rag-langchain-project/
├── data/                              # 上传文档落盘目录
├── scripts/
│   └── init_admin.py                  # 初始化管理员账号脚本
├── src/                               # 源代码根目录
│   ├── config.py                      # 配置管理（pydantic-settings 读取 .env）
│   ├── main.py                        # FastAPI 应用入口
│   ├── deps.py                        # 依赖注入：获取当前用户 / 管理员
│   ├── api/                           # 路由层（控制器）
│   │   ├── auth.py                    # 认证接口
│   │   ├── chat.py                    # 会话 & 问答接口（含 SSE 流式）
│   │   ├── document.py                # 文档管理接口
│   │   └── system.py                  # 系统接口（预留）
│   ├── services/                      # 业务逻辑层
│   │   ├── chat.py                    # 会话 / 问答业务逻辑
│   │   └── document.py                # 文档上传 / 删除业务逻辑
│   ├── rag/                           # RAG 核心链路
│   │   ├── loader.py                  # 文档加载
│   │   ├── splitter.py                # 文档切分
│   │   ├── embedding.py               # 向量嵌入模型
│   │   ├── store.py                   # 向量存储（Qdrant）
│   │   ├── retriever.py               # 向量检索
│   │   ├── llm.py                     # LLM 工厂
│   │   └── generation.py              # 生成回答（prompt | llm | parser）
│   ├── db/                            # 数据库层
│   │   ├── models.py                  # ORM 模型（User/Session/Message/Document/Chunk）
│   │   ├── sessions_async.py          # 异步引擎与会话
│   │   └── sessions_sync.py           # 同步引擎与会话
│   ├── schemas/                       # Pydantic 请求 / 响应模型
│   ├── utils/                         # 工具
│   │   ├── jwt.py                     # JWT 令牌
│   │   └── password.py                # 密码加密
│   └── 12_rag_langchain_project/      # 包入口
├── mcp_server.py                      # MCP Server（暴露 RAG 工具）
├── .env.example                       # 环境变量示例
├── pyproject.toml                     # 项目配置与依赖
└── uv.lock                            # 依赖锁定文件
```

---

## 🚀 快速开始

### 1. 环境准备

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip
- PostgreSQL（本地或 Docker）
- Qdrant（本地或 Docker）

> 使用 Docker 快速启动 PostgreSQL 与 Qdrant：
>
> ```bash
> # PostgreSQL
> docker run -d --name pg -p 5432:5432 \
>   -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
>   -e POSTGRES_DB=campus_rag postgres:16
>
> # Qdrant
> docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
> ```

### 2. 安装依赖

```bash
cd 12-rag-langchain-project
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少配置数据库、Qdrant、JWT 密钥以及 LLM 提供商（详见下方「配置项说明」）。

### 4. 初始化数据库 & 管理员

```bash
PYTHONPATH=src uv run python -m scripts.init_admin
```

> 脚本会自动建表，并创建默认管理员账号（`admin@campu.com`，密码请查看脚本）。

### 5. 启动服务

```bash
PYTHONPATH=src uv run uvicorn main:app --reload
```

启动后访问：

- 接口文档（Swagger UI）：http://localhost:8000/docs
- 根路径：http://localhost:8000/ → `{"message": "Hello"}`

### 6. 上传文档

通过接口 `POST /api/v1/documents/upload` 上传一份 Markdown 文档（示例见 `data/` 目录），系统会自动完成切分、向量化入库。

### 7. 开始问答

创建会话 → 提问 → 获取回答与来源引用。也可直接调用流式接口获得打字机效果。

---

## 🔄 实现流程详解

下面是本系统的完整实现流程，从底层数据模型到 RAG 链路再到接口层，逐层说明。

### 总体架构

系统采用经典的分层架构，数据流如下：

```
                    ┌──────────────────────────────────────────┐
   上传文档          │                FastAPI 应用                │
  (md/txt) ───────► │  api 路由 → services 业务 → rag 链路        │
                    └───────────────┬──────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
   │ PostgreSQL   │          │   Qdrant    │          │  本地磁盘    │
   │ 用户/会话/    │          │  向量数据    │          │  上传文档    │
   │ 消息/文档     │          │  (检索)      │          │  (落盘)     │
   └─────────────┘          └─────────────┘          └─────────────┘
```

- **PostgreSQL**：存结构化数据（用户、会话、消息、文档元数据、chunk 元数据）
- **Qdrant**：存文档向量，负责相似度检索
- **本地磁盘**：保存上传的原始文档文件

### 1. 配置管理（`src/config.py`）

继承 `pydantic_settings.BaseSettings`，启动时自动从项目根目录的 `.env` 读取配置，将分散的环境变量统一收口为 `setting` 单例，供全项目引用。

关键点：

- `env_file` 指向 `.env`，`extra="ignore"` 忽略未定义配置项
- `DATABASE_URL` 通过 `@property` 动态拼接（`postgresql+asyncpg://...`）
- 覆盖数据库、Qdrant、JWT、LLM 提供商、RAG 参数（chunk 大小、top_k 等）所有配置

### 2. 数据库层（`src/db/`）

**ORM 模型（`models.py`）** 定义了 5 张表：

| 表 | 说明 | 关键字段 |
|----|------|---------|
| `users` | 用户 | email、password_hash、role（student/admin）、is_active |
| `sessions` | 会话 | user_id、title、created_at |
| `messages` | 消息 | session_id、role（user/assistant）、content、sources（JSONB） |
| `documents` | 文档 | filename、file_path、status、chunk_count |
| `chunks` | 分块 | document_id、content、qdrant_id、extra_meta（JSONB） |

实体关系：

```
User 1 ── n Session 1 ── n Message
User 1 ── n Document 1 ── n Chunk
```

均通过 `relationship` + `cascade="all, delete-orphan"` 实现级联删除。

**会话管理（`sessions_async.py`）**：

- `create_async_engine` 创建异步引擎，`async_sessionmaker` 创建会话工厂
- `get_session()` 作为 FastAPI 依赖，`yield` 会话、`finally` 关闭
- `init_db()` 在应用生命周期（lifespan）中调用 `Base.metadata.create_all` 自动建表
- `close_db()` 在应用关闭时释放连接

### 3. 认证鉴权（`src/utils/`、`src/deps.py`、`src/api/auth.py`）

**密码加密（`utils/password.py`）**：使用 bcrypt 对密码加盐哈希，`verify_password` 校验明文与密文。

**JWT（`utils/jwt.py`）**：使用 python-jose 生成双令牌：

- `create_access_token`：`type=access`，默认 30 分钟过期
- `create_refresh_token`：`type=refresh`，默认 7 天过期
- `verify_token`：解码并校验，失败抛出 `ValueError`

**依赖注入（`deps.py`）**：

- `get_current_user`：通过 `HTTPBearer` 取 token → 校验 `type=access` → 查库 → 校验 `is_active`
- `get_admin_user`：在 `get_current_user` 基础上校验 `role=admin`

**认证接口（`api/auth.py`）**：`register`（邮箱去重、密码长度校验）、`login`（校验密码与状态、签发双令牌）、`refresh`（用 refresh token 换新 access token）、`me`（返回当前用户信息）。

### 4. RAG 核心链路（`src/rag/`）

这是系统的核心，分为「离线写入」与「在线查询」两条链路。

#### 4.1 文档加载（`loader.py`）

使用 LangChain 的 `TextLoader` 以 UTF-8 读取本地文件，返回文档纯文本内容（`page_content`）。

#### 4.2 文档切分（`splitter.py`）

采用**两级切分**策略，兼顾语义与长度：

1. **按标题切分**：`MarkdownHeaderTextSplitter` 按 `##`（章节）和 `###`（小节）切分，将标题信息写入每个 chunk 的 `metadata`（`chapter` / `section`），为来源追溯提供结构化信息。
2. **按长度切分**：`RecursiveCharacterTextSplitter` 再按 `chunk_size` / `chunk_overlap` 切分，分隔符按优先级（`\n\n → \n → 。！？， → 空格 → 空串`）递归尝试，尽量在句子边界切断。

#### 4.3 向量嵌入（`embedding.py`）

- 使用 `HuggingFaceEmbeddings` 加载中文嵌入模型 `BAAI/bge-base-zh`（768 维）
- 通过 `HF_ENDPOINT` 环境变量指向 `hf-mirror.com` 镜像，方便国内下载
- `@lru_cache` 缓存模型实例，避免重复加载
- `normalize_embeddings=True` 归一化，保证余弦相似度计算效果

#### 4.4 向量存储（`store.py`）

- `get_qdrant_client`：创建 Qdrant 客户端
- `get_vector_store`：若集合不存在则自动创建（`Distance.COSINE` + 768 维），返回 `QdrantVectorStore`
- `store_document`：加载 → 切分 → 写入 Qdrant，返回 `qdrant_ids`、`chunk_count`、`chunks`
- `delete_document_points`：按 `qdrant_id` 删除指定向量点

#### 4.5 向量检索（`retriever.py`）

- `similarity_search_with_score` 按 `RETRIEVER_TOP_K` 召回最相似的 k 个文档片段
- 拼接 `docs_text` 作为上下文
- 构造 `sources` 列表（原文前 30 字、相似度 score、所属 chapter/section）

#### 4.6 LLM 工厂（`llm.py`）

根据 `LLM_PROVIDER` 返回对应模型实例：

- `deepseek` → `ChatDeepSeek`
- `openai` → `ChatOpenAI`
- 其他 → `ChatOllama`

#### 4.7 生成回答（`generation.py`）

核心链路 `ask_question(question, history)`：

1. 获取 LLM
2. `retrieve(question)` 检索出上下文与来源
3. 构建 `ChatPromptTemplate`（`SYSTEM_PROMPT` + 可选的 `chat_history` + 用户输入）
4. 组装 LangChain 链：`prompt | llm | StrOutputParser()`
5. `chain.ainvoke(...)` 异步生成答案
6. 返回 `{answer, sources}`

其中 `SYSTEM_PROMPT` 强制模型：仅基于上下文回答、上下文不足时如实说明、中文回答、涉及数字/时间/地点引用原文——这是抑制幻觉的关键。

### 5. 文档管理业务（`src/services/document.py`）

**上传流程（`upload_document`）**，按注释所示的 6 步：

1. 保存文件到本地磁盘（文件名加 UUID 前缀防冲突）
2. 写 `documents` 表记录（状态 `indexing`）
3. 调用 `store_document` 切分并写入 Qdrant
4. 将每个 chunk 的元数据（含 `qdrant_id`）写入 `chunks` 表
5. 更新文档状态为 `ready` 并记录 `chunk_count`
6. 任一步异常则置状态为 `error` 并回抛

**删除流程（`delete_document`）**：

1. 查询该文档所有 chunk 的 `qdrant_id`
2. 从 Qdrant 删除对应向量点
3. 删除本地磁盘文件
4. 删除 `documents` 表记录（级联删除 chunks）

### 6. 会话与问答业务（`src/services/chat.py`）

`process_question` 处理一次完整的问答：

1. 先持久化用户消息到 `messages` 表
2. 读取该会话的历史消息（去掉刚写入的最后一条）
3. 将历史消息转换为 LLM 所需的 `{role, content}` 格式
4. 调用 `ask_question(question, history)` 完成检索 + 生成
5. 持久化 AI 回答与来源
6. 若会话标题仍是"新对话"，取问题前 10 字作为标题

### 7. 流式输出（`src/api/chat.py` 的 `chat_stream`）

- 复用检索与生成链路，但改用 `chain.astream(...)` 逐 token 迭代
- 通过 `EventSourceResponse` 将异步生成器包装为 SSE 响应
- 依次推送 `token`（文本片段）、`source`（来源）、`done`（结束）三类事件
- 使用 `asyncio.ensure_future` 后台异步保存用户消息与 AI 消息，避免阻塞流式响应

### 8. MCP Server（`mcp_server.py`）

使用 `FastMCP` 将系统能力暴露为 MCP 工具，可被支持 MCP 的客户端（如 Claude Desktop）调用：

- `rag_query(question)`：向知识库提问，返回带来源的回答
- `list_documents`：列出知识库中的文档

### 9. 管理员初始化（`scripts/init_admin.py`）

独立脚本，流程为：建表 → 检查管理员邮箱是否已存在 → 不存在则创建 `role=admin` 的账号。可重复执行，幂等。

---

## 🔌 API 接口一览

所有接口前缀为 `/api/v1`。

### 认证 `/api/v1/auth`

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/register` | 注册 | 无 |
| POST | `/login` | 登录，返回双令牌 | 无 |
| POST | `/refresh` | 刷新 access token | refresh token |
| GET | `/me` | 获取当前用户信息 | access token |

### 会话与问答 `/api/v1/chat`

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/sessions` | 创建会话 | access token |
| GET | `/sessions` | 会话列表 | access token |
| GET | `/sessions/{id}` | 会话消息详情 | access token |
| DELETE | `/sessions/{id}` | 删除会话 | access token |
| POST | ``（即 `/api/v1/chat`） | 普通问答（一次性返回） | access token |
| POST | `/stream` | 流式问答（SSE） | access token |

### 文档 `/api/v1/documents`

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | `/upload` | 上传文档（.md / .txt，≤10MB） | access token |
| GET | `` | 文档列表 | access token |
| DELETE | `/{id}` | 删除文档 | admin |

---

## ⚙️ 配置项说明

配置位于项目根目录 `.env` 文件（参考 `.env.example`）：

| 变量 | 说明 |
|------|------|
| `APP_NAME` / `DEBUG` | 应用名称 / 调试模式 |
| `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME` | PostgreSQL 连接配置 |
| `QDRANT_HOST` / `QDRANT_PORT` / `QDRANT_COLLECTION` | Qdrant 连接配置 |
| `JWT_SECRET_KEY` / `JWT_ALGORITHM` | JWT 签名密钥与算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` / `REFRESH_TOKEN_EXPIRE_DAYS` | 令牌有效期 |
| `LLM_PROVIDER` | LLM 提供商：`ollama` / `openai` / `deepseek` |
| `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` / `DEEPSEEK_MODEL` | DeepSeek 配置 |
| `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` | OpenAI 配置 |
| `OLLAMA_BASE_URL` / `OLLAMA_MODEL` | Ollama 配置 |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | 切分参数 |
| `RETRIEVER_TOP_K` | 检索召回数量 |
| `SHOW_SOURCE` | 是否返回来源 |

---

## 📌 说明

- 嵌入模型 `bge-base-zh` 首次运行时需下载（已配置 hf-mirror.com 镜像），可离线时替换为本地模型路径。
- 生产环境务必修改 `JWT_SECRET_KEY` 与默认管理员密码。
- 上传文档目前限制 `.md` / `.txt` 格式、单文件 10MB 以内。
