#实现notes入库功能
import sys
from pathlib import Path

# 把项目根目录加进模块搜索路径，让"直接运行本文件"也能找到 chunker / loader 包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chromadb
from chromadb.utils import embedding_functions
from chunker.chunker import chunk_text
from loader.loader import NOTES_DIR, load_docs
# 项目根目录（本文件的上一级）。和 loader.py 里 NOTES_DIR 一样用 __file__ 定位，
# 保证无论从哪个目录启动，chroma_db 和模型路径都指向项目内的固定位置
ROOT_DIR = Path(__file__).resolve().parent.parent

client = chromadb.PersistentClient(path=str(ROOT_DIR / "chroma_db"))
#设置embedding函数，使用根目录下已下载好的本地 BGE-M3 模型，归一化后内积=余弦相似度
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=str(ROOT_DIR / "bge-m3"),  # 传本地路径，避免按名字联网重新下载
    device="cuda",  # 用 GPU 编码；Chroma 默认是 cpu，几千个块会慢到像卡死
    normalize_embeddings=True,  # 归一化后，内积 = 余弦相似度，便于统一比较
)
#初始化向量数据库
collection = client.get_or_create_collection(
    name="notes_docs",        # 表名
    embedding_function=embedder,  # 注册后，add 时只传文本，Chroma 自动调用它编码
    metadata={"hnsw:space": "cosine"},  # 指定相似度度量用余弦相似度（默认是 L2 距离）
)

#将笔记读入，切块，写入向量数据库
def index_directory():
    """把 notes/ 下所有文档读入、切块、写入向量库。可重复运行：同 id 的旧块被覆盖。"""
    # 第一步：加载。得到 [{"source": "notes/xx.md 的绝对路径", "text": "全文..."}, ...]
    # 不传参数，load_docs 默认就读根目录下的 notes/
    raw_docs = load_docs()

    total_chunks = 0
    for n, doc in enumerate(raw_docs, start=1):
        # 三个列表一一对应，是 collection.upsert 要求的格式：
        #   chunks[i] 的向量、元数据、id 分别是 embedder 编码结果 / metadatas[i] / ids[i]
        chunks, metadatas, ids = [], [], []
        # 转成相对 notes/ 的路径当"身份"：比绝对路径可读，换机器也不失效
        rel = Path(doc["source"]).relative_to(NOTES_DIR).as_posix()
        # 第二步：切块。一篇长文档切成多个小块
        for i, chunk in enumerate(chunk_text(doc["text"])):
            chunks.append(chunk)
            # 元数据记录"这块来自哪个文件、是第几块"，
            # 检索命中后靠 source 告诉用户答案出处；也支持按 source 过滤检索
            metadatas.append({"source": rel, "chunk_index": i})
            # id = 文件相对路径 + 块序号：同一文件重跑时 id 不变，upsert 直接覆盖旧块，
            # 不会像全局计数器那样每次都换一批新 id、add 时撞重复 id 报错
            ids.append(f"{rel}#{i}")

        # 第三步：逐篇入库，而不是攒到最后一起提交——每篇提交完立刻打印进度，
        # 运行时能看到实时进展，不会安静得像卡死。
        # 只传 documents（文本），Chroma 自动调 embedder 逐块编码后存储。
        # 用 upsert 而不是 add：id 已存在时覆盖而不是报错，脚本可以放心重复跑
        collection.upsert(documents=chunks, metadatas=metadatas, ids=ids)
        total_chunks += len(chunks)
        print(f"[{n}/{len(raw_docs)}] {rel} -> {len(chunks)} 块（累计 {total_chunks}）")

    print(f"完成：已索引 {len(raw_docs)} 篇文档，共 {total_chunks} 个块")


# 直接运行本脚本时执行索引；upsert 保证了重复运行是安全的
if __name__ == "__main__":
    index_directory()
