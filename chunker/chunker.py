# chunker.py —— 阶段2：文本切分
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """滑动窗口切分：每块约 chunk_size 个字符，相邻块重叠 overlap 个字符。

    为什么要重叠：硬切可能把一个完整语义（比如一个定义）切成两半，
    重叠保证关键信息大概率完整出现在至少一个块里。
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size          # 本块的右边界（可能超出文末，切片会自动截断）
        chunks.append(text[start:end])    # 取 [start, end) 这一段作为一块
        start += chunk_size - overlap     # 下一步只前进 chunk_size - overlap，留下重叠区
    return chunks