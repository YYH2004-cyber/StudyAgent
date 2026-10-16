# api.py
# 模型配置：全项目唯一碰连接配置的地方，其他模块都从这里 import client
from openai import OpenAI

# 模块加载时创建一次客户端，之后所有调用复用同一个连接配置
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)
DEFAULT_MODEL = "qwen2.5:7b"  # 不指定 model 参数时走这个默认值
