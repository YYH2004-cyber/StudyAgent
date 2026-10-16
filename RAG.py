from chat.chat import chat  # 沿用 02 篇的 chat 封装，底层连接由 api.py 统一配置（本机 Ollama）
from vector_db.retriever import retrieve  # 上一节写好的检索器：输入问题，返回最相关的文本块


# 系统提示词：给模型设定"角色 + 纪律"，这是 RAG 不胡编的关键
SYSTEM_PROMPT = """\
你是一个知识库助手。严格按以下规则回答：

1. 只能基于给定的「参考资料」回答和之前的对话历史回答
2. 如果参考资料里没有相关信息，直接说"在现有资料中未找到相关信息"，不要编造
3. 回答末尾用 [来源：文件名] 的格式标出每条信息的出处
4. 回答要简洁，优先使用要点列举
"""


def answer(question: str, 
           history: list[dict] | None = None,   # None = 不带历史(命令行单问场景)
           top_k: int = 5,
           temperature: float = 0.7) -> str:  # top_k：检索多少个相关块，默认 5 个
    # 第 1 步：检索 —— 把问题变成向量，去知识库里找最相关的 top_k 个文本块
    hits = retrieve(question, top_k=top_k)

    # 第 2 步：拼参考资料 —— 每个块前标注来源文件名，用分隔线隔开
    # 这样模型回答时才能标出 "[来源：xxx]" 的出处
    context = "\n\n---\n\n".join(
        f"[来源：{h['source']}]\n{h['text']}" for h in hits
    )

    # 第 3 步：组装用户提示词 —— 参考资料 + 用户问题，一起发给模型
    user_prompt = f"""\
    参考资料：
     {context}
     问题：{question}
     """
    # 第 4 步：调用 LLM 生成回答
    # temperature 由调用方传入（界面滑块），不传时用函数默认值
    return chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},  # 角色设定和纪律
             *(history or []),   # 星号解包历史;None 和空列表都在这里兜成"没有历史"
            {"role": "user", "content": user_prompt},      # 检索到的资料 + 问题
        ],
        temperature=temperature,
    )


# 直接运行本文件时，用一个真实问题测试整条 RAG 链路
if __name__ == "__main__":
    q = "什么是 HTTP协议？"
    print(f"问：{q}\n答：{answer(q)}")