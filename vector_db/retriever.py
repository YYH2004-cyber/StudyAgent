from pathlib import Path

# 项目根目录（本文件的上一级）。和 index.py 一样用 __file__ 定位，
# 保证无论从哪个目录启动，chroma_db 和模型路径都指向项目内的固定位置
ROOT_DIR = Path(__file__).resolve().parent.parent

import chromadb
from chromadb.utils import embedding_functions

print("正在加载本地 bge-m3 模型（约需十几秒到一分钟）……")
# 持久化客户端：指向阶段 3 建好的向量库目录，重启后数据仍在
client = chromadb.PersistentClient(path=str(ROOT_DIR / "chroma_db"))
# 加载与入库时相同的 embedding 模型（必须一致，否则查询向量和库内向量不在同一空间）
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=str(ROOT_DIR / "bge-m3"),  # 和 index.py 相同的本地模型路径，不联网
    device="cuda",  # 和入库时一致用 GPU 编码，CPU 会慢到像卡死
    normalize_embeddings=True,  # 归一化后，内积 == 余弦相似度
)
# 打开已有的 collection，并显式传入同一个 embedding 函数用于自动向量化查询文本
collection = client.get_collection(name="notes_docs", embedding_function=embedder)


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """语义检索：把查询文本向量化，在库里找余弦相似度最高的 top_k 个片段。"""
    # Chroma 会用 collection 绑定的 embedder 自动把 query 向量化，再返回最近的 top_k 条
    result = collection.query(query_texts=[query], n_results=top_k)
    return [
        {
            "text": doc,            # 命中的原文片段（切块入库的内容）
            "source": meta["source"],  # 来源文件路径，方便最终回答时标注出处
            "score": 1 - dist,  # Chroma 返回距离，转为相似度
        }
        # 三个列表按下标配对：documents[i]、metadatas[i]、distances[i] 描述同一条结果
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


# 直接运行本脚本时做一个冒烟测试：拿一个业务问题跑检索，人工检查命中率
if __name__ == "__main__":
    for hit in retrieve("狭义相对论是什么"):
        # 输出相似度分数、来源文件和片段前 100 字，快速验证检索效果
        print(f"[{hit['score']:.3f}] {hit['source']}\n{hit['text'][:100]}...\n")