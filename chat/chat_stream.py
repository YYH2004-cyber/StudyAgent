# chat_stream.py
# 流式问答：逐段拿增量，打字机效果的来源
from typing import Iterable  # 只用来做类型标注：chat_stream 返回"字符串生成器"

from api.api import client, DEFAULT_MODEL


def chat_stream(messages: list[dict], model: str = DEFAULT_MODEL, **kwargs) -> Iterable[str]:
    """流式调用，yield 文本增量。"""
    # 有 yield 这个函数就是生成器：调用时不执行，for 循环消费时才逐块产出
    stream = client.chat.completions.create(
        model=model, messages=messages, stream=True, **kwargs
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content  # delta 里只有本次新增的内容
        if delta:  # 过滤掉 content 为 None 的块（如只带角色信息的首块）
            yield delta


if __name__ == "__main__":
    # 冒烟测试：for 循环消费生成器，逐段打印
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "用一句话解释什么是协程"},
    ]
    for piece in chat_stream(messages):
        print(piece, end="", flush=True)
    print()
