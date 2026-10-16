# Python 装饰器

> 分类：编程 | 日期：2026-10-12 | 标签：python, 进阶

## 核心原理

装饰器本质上是一个"接收函数、返回新函数"的高阶函数，`@decorator` 只是语法糖：

```python
@my_decorator
def func():
    pass

# 完全等价于
func = my_decorator(func)
```

理解装饰器的关键是**闭包**：内层函数可以引用外层函数作用域的变量，且这些变量在装饰完成后依然存活。

## 最小示例：计时装饰器

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        cost = time.perf_counter() - start
        print(f"{func.__name__} 耗时 {cost:.4f}s")
        return result
    return wrapper

@timer
def slow_add(a, b):
    time.sleep(0.2)
    return a + b
```

注意 `wrapper` 用 `*args, **kwargs` 透传参数，这样能装饰任意签名的函数，也不会丢返回值。

## 为什么需要 functools.wraps

被装饰后，函数的 `__name__`、`__doc__` 等元信息会变成 wrapper 的，调试和生成文档时会"认不出"原函数。标准解法：

```python
from functools import wraps

def timer(func):
    @wraps(func)  # 把原函数的元信息拷贝到 wrapper 上
    def wrapper(*args, **kwargs):
        ...
    return wrapper
```

`wraps` 本身也是一个装饰器（基于 `functools.partial` 实现），源码很短，值得读一遍。

## 带参数的装饰器

再多包一层闭包：先接收参数、返回真正的装饰器（三层结构）：

```python
def retry(times=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if i == times - 1:
                        raise
        return wrapper
    return decorator

@retry(times=5)
def fetch_data(): ...
```

## 常见用途

- 日志 / 计时 / 性能埋点
- 缓存：标准库 `functools.lru_cache`、`functools.cache`
- 权限校验：Web 框架里的 `@login_required`
- 注册分发：Flask 的 `@app.route` 本质是把函数登记进路由表，并没有包装函数
- 重试、限流、参数校验

## 易错点

1. 装饰器在**函数定义时（导入时）立即执行**，而不是每次调用时执行。
2. 类也可以做装饰器（实现 `__call__`）；装饰器也能装饰类本身（返回新类）。
3. 忘写 `functools.wraps` 是最常见失误，症状是 `__name__` 变成 `wrapper`、文档字符串丢失。
4. 想按第一个参数类型分发，用 `functools.singledispatch`，别自己造轮子。

## 我的理解

装饰器 = "不改原函数代码，往调用链上插一层逻辑"。写之前先在纸上画清楚层次：普通装饰器两层（decorator → wrapper），带参数的装饰器三层（factory → decorator → wrapper）。层次画对，基本不会写错。
