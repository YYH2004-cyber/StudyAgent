# chat.py
# 同步问答：发一整条请求，等完整回复
from api.api import client, DEFAULT_MODEL


def chat(messages: list[dict], model: str = DEFAULT_MODEL, **kwargs) -> str:
    """非流式调用，返回完整字符串。"""
    # **kwargs 透传：temperature、max_tokens 等参数不用在这里逐个声明，原样传给 SDK
    resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
    # 回答路径固定：choices[0].message.content
    return resp.choices[0].message.content


if __name__ == "__main__":
    # 冒烟测试
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "用一句话解释什么是协程"},
    ]
    answer = chat(messages)
    print(answer)
