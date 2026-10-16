import streamlit as st
from RAG import answer
# 复用 retriever 里已建好的 collection 查询库状态：RAG 顶层 import 时它已经
# 加载过了（连带十几秒的 bge-m3 模型加载），这里拿到的是同一个对象，零额外开销
from vector_db.retriever import collection

st.set_page_config(page_title="问答助手", page_icon="🤖")

st.title("🤖 问答助手")
# caption 是小号灰字副标题，说明这个页面是干嘛的
st.caption("基于本地知识库的 RAG 问答 · 先检索相关笔记片段，再交给本地模型生成回答")

# 侧边栏放模型参数——放在 with 里，这个组件就渲染到侧边栏而不是主区域
with st.sidebar:
    # header + divider 把侧边栏分成"参数"和"知识库"两组，不再是一个滑块孤零零挂着
    st.header("⚙️ 模型参数")
    # 滑块每拖一下都会触发全脚本重跑，temperature 的最新值会自动带回来
    temperature = st.slider("回答随机性", 0.0, 1.0, 0.7)   # (最小, 最大, 默认值)

    st.divider()

    st.header("📚 知识库状态")
    # count() 只查元数据不碰向量，开销极小；
    # get() 把所有块的 source 字段拉出来去重，得到"收录了几篇文档"——
    # demo 规模（几百个块）完全没问题，库大了就别这么全量拉
    n_docs = len({m["source"] for m in collection.get(include=["metadatas"])["metadatas"]})
    st.metric(label="已索引片段", value=collection.count())   # 大数字卡片，比一行文字醒目
    st.caption(f"来自 notes/ 下 {n_docs} 篇文档")

# 用 session_state 保存对话历史：顶层普通变量每次重跑都会归零，
# 不存进 session_state 的话，用户每发一句话，之前的历史就全丢了
if "messages" not in st.session_state:
    st.session_state.messages = []

# 空状态欢迎：还没有任何对话时显示引导卡片，别让用户面对光秃秃的输入框
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🦜"):
        st.write("你好！我会先从你的笔记里检索相关片段，再基于片段内容回答。")
        st.caption("点击问题直接提问，或在底部输入框输入：")
        # 示例问题按钮：key 必须全局唯一，所以带上问题文本做前缀。
        # 点击只负责把问题暂存进 session_state，真正走 RAG 链路的是下面的统一入口
        for q in ("什么是 HTTP 协议？", "狭义相对论是什么？"):
            if st.button(q, key=f"demo:{q}"):
                st.session_state.pending_prompt = q

# 先把已有历史渲染出来——这一步在每次重跑时都会执行，
# 作用是"复现"之前所有轮次的气泡；历史在下面是追加进列表的，
# 但渲染永远靠这个循环从 session_state 里读，而不是靠临时 st.write
for msg in st.session_state.messages:
    with st.chat_message(
        msg["role"],
        # 助手气泡统一用鹦鹉头像；user 传 None 用默认图标
        avatar="🦜" if msg["role"] == "assistant" else None,
    ):
        st.write(msg["content"])

# 底部输入框。海象运算符 := ：赋值的同时判断真值——
# 用户按回车才返回输入内容并触发重跑；没输入时返回 None
prompt = st.chat_input("请输入你的问题")
# 两个提问入口在这里汇合：示例按钮没有"输入框内容"可用，
# 靠上面暂存的 pending_prompt 补位。
# 用 pop 而不是 [...] 取：取出的同时删掉，避免下次重跑时它还残留、把同一个问题重复发一遍
if prompt is None and "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    # 先存进历史、再渲染：顺序很重要。存了之后即使后续代码报错，
    # 下一次重跑时这条消息也不会丢（渲染靠上面的循环兜底）
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)   # 立刻显示用户这条消息，不用等模型返回

    with st.spinner("思考中..."):   # 包住耗时操作显示加载动画，避免用户以为卡死了
        # 完整 RAG 链路：检索知识库相关片段 + 交给 LLM 生成回答
        reply = answer(
            prompt, 
            history=st.session_state.messages[:-1],            
            temperature=temperature)

    with st.chat_message("assistant", avatar="🦜"):
        st.write(reply)
    # 回复也要存回历史：否则下次用户提问触发重跑时，
    # 上面那个渲染循环里没有这条回复，界面上它就"消失"了
    st.session_state.messages.append({"role": "assistant", "content": reply})
