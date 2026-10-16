# StudyAgent · 本地个人知识库问答助手

基于 **RAG（检索增强生成）** 的个人知识库问答 Demo：把 `notes/` 下的 Markdown / PDF 笔切块、向量化存入本地 Chroma 向量库，提问时先检索最相关的笔记片段，再交给本地大模型生成带出处的回答。全程本地运行，数据不出本机。

> 📌 **关于本项目**：这是一个以学习为目的的个人项目——通过从零搭建一个完整的 RAG 应用来学习 LLM 应用开发的各个环节（文档加载、切块、向量化、检索、Prompt 工程、对话界面）。项目持续更新中，后续会逐步补充多轮对话记忆、流式输出、引用来源展示等功能。

## 功能

- 📚 多学科笔记入库（Markdown + PDF），语义检索而非关键词匹配
- 🤖 本地 LLM（Ollama + qwen2.5:7b）生成回答，回答末尾标注 `[来源：文件名]`
- 💬 Streamlit 聊天界面：多轮对话历史、temperature 可调、示例问题一键提问
- 🔒 完全离线：embedding 用本地 bge-m3 模型，LLM 走本机 Ollama

## 项目结构

```
StudyAgent/
├── App.py            # Streamlit 聊天界面（入口）
├── RAG.py            # RAG 链路：检索 → 拼上下文 → 生成回答
├── api/              # Ollama 连接配置（OpenAI 兼容接口）
├── chat/             # LLM 对话封装（普通 + 流式）
├── loader/           # 文档加载（Markdown / PDF）
├── chunker/          # 文本切块
├── vector_db/        # Chroma 向量库：建索引 + 检索器
├── notes/            # 知识库语料（各学科笔记）
├── bge-m3/           # 本地 embedding 模型（体积大，不入库，需自行下载）
└── chroma_db/        # 向量库数据（运行时生成，不入库）
```

## 快速开始

### 1. 准备本地环境

- 安装 [Ollama](https://ollama.com/)，拉取对话模型：

  ```bash
  ollama pull qwen2.5:7b
  ```

- 从 [HuggingFace](https://huggingface.co/BAAI/bge-m3) 或 ModelScope 下载 bge-m3 模型文件，放到项目根目录的 `bge-m3/` 文件夹（或自行修改 `vector_db/` 中代码指向的路径）。

### 2. 安装 Python 依赖

```bash
pip install streamlit chromadb openai pypdf
```

### 3. 建立向量索引（首次运行）

```bash
python vector_db/index.py
```

### 4. 启动问答界面

```bash
streamlit run App.py
```

也可以不走界面，直接命令行测试 RAG 链路：

```bash
python RAG.py
```

## 后续规划

### ✅ 已完成

- [x] **模型调用层**：封装 Ollama 的 OpenAI 兼容接口，普通对话 + 流式输出（`api/`、`chat/`）
- [x] **知识库入库**：Markdown / PDF 加载 → 滑窗切块 → bge-m3 向量化 → Chroma 持久化（`loader/`、`chunker/`、`vector_db/`）
- [x] **RAG 链路**：语义检索 → 拼装带来源的参考资料 → 生成带出处的回答（`RAG.py`）
- [x] **问答界面**：Streamlit 聊天界面，多轮对话记忆、temperature 可调、示例问题（`App.py`）

### 🚧 近期：界面体验收尾

- [ ] **流式输出**：接入已写好的流式接口，回答逐字打出，替代现在的"思考中..."整段等待
- [ ] **引用来源展示**：回答下方用折叠面板展示命中的笔记片段和相似度分数，检索过程透明可查
- [ ] **界面一键重建索引**：笔记更新后在界面上点按钮重建向量库，不用回到命令行

### 📋 中期：检索质量与实用功能

- [ ] **相似度阈值过滤**：得分太低的命中不进入上下文，避免不相关内容"硬凑"干扰回答
- [ ] **指代消解**：多轮追问"它是什么"时改写查询再检索，解决代词导致的检索落空
- [ ] **会话持久化**：对话历史存本地，刷新页面不丢失

### 🎯 远期：进阶方向

- [ ] **RAG 效果评测**：构建小规模问答集，量化检索命中率和回答质量，让优化有据可依
- [ ] **Agent 化**：让模型自主决定是否检索、检索什么，而不是每次提问都固定走一遍检索

## 说明

- 向量库使用 GPU 做 embedding 编码（`vector_db/retriever.py` 中 `device="cuda"`），没有 GPU 的机器请改为 `"cpu"`，但入库和检索会明显变慢。
- 换用自己的语料：把文档放进 `notes/`，重新执行第 3 步建索引即可。
