# SOLID 原则

> 分类：编程 | 日期：2026-10-12 | 标签：oop, 设计原则

面向对象五大设计原则，共同目标是让代码"高内聚、低耦合、易扩展"。原则不是教条，是重构时的体检表。

## S — 单一职责原则（SRP）

一个类只应因一个原因被修改。

```python
# 反例：报表类既组装数据、又渲染 HTML、又写文件
class Report:
    def render_html(self): ...
    def save_to_file(self): ...

# 正解：按变化方向拆分
class ReportContent: ...   # 只负责数据
class HtmlRenderer: ...    # 只负责渲染
class FileStorage: ...     # 只负责持久化
```

## O — 开闭原则（OCP）

对扩展开放、对修改关闭：加新行为时新增代码，而不是改老代码。

```python
from abc import ABC, abstractmethod

class Discount(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...

class VipDiscount(Discount):
    def apply(self, price): return price * 0.8

# 新需求：新增一个类即可，不碰已有逻辑
class BlackFridayDiscount(Discount):
    def apply(self, price): return price * 0.5
```

## L — 里氏替换原则（LSP）

任何父类出现的地方，子类都必须能无缝替换，且不破坏调用方的预期。

经典反例：让"正方形"继承"长方形"——正方形重写 `set_width` 时必须同时改 height，违反了长方形的使用约定。判断标准：子类不应加强前置条件、不应削弱后置条件、不应抛出父类不会抛的异常。

## I — 接口隔离原则（ISP）

不要强迫实现者依赖它用不到的方法；接口要小而专。

```java
// 反例：机器人被迫实现 eat()
interface Worker {
    void work();
    void eat();
}

// 正解：按角色拆分接口
interface Workable { void work(); }
interface Eatable  { void eat(); }
```

## D — 依赖倒置原则（DIP)

高层模块不依赖低层模块，两者都依赖抽象（接口）；细节依赖抽象。Spring 的依赖注入（DI）就是这条原则的工程化落地。

```python
class NotificationService:
    def __init__(self, channel: MessageChannel):  # 依赖抽象接口
        self.channel = channel

# 换短信 / 邮件 / 推送，只需换注入的实现类，服务代码一行不改
```

## 我的理解

用"疼不疼"来检验：加个需求要改一堆类（违反 OCP）；子类一继承就要重写父类行为（违反 LSP）；实现接口时一堆空方法（违反 ISP）；new 具体类 new 得到处都是（违反 DIP）；一个类改 UI 又改数据库（违反 SRP）。设计时先写最简单的实现，闻到坏味道再往原则上靠，不要一开始就过度抽象。
