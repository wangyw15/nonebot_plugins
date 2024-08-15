import json
import random
from collections import namedtuple
from typing import Annotated

from libraries.llm.tool import BaseTool

Item = namedtuple("Item", ["name", "weight"])


def parse_items(raw_items: str) -> list[Item]:
    raw_items = raw_items.replace("，", ",").split(",")
    items: list[Item] = []

    # 处理权重
    for raw_item in raw_items:
        raw_item = raw_item.strip()
        if not raw_item:
            continue

        raw_item = raw_item.replace("：", ":")
        weight = 1
        if ":" in raw_item:
            raw_item, weight = raw_item.split(":", 1)
            weight = float(weight)
        items.append(Item(raw_item, weight))

    return items


def dump_items(items: list[Item]) -> str:
    return ",".join(f"{item.name}:{item.weight}" for item in items)


def random_select_from_list(items: list[Item] | list[str]) -> str:
    if isinstance(items[0], str):
        items: list[Item] = [Item(item, 1) for item in items]

    # 计算权重总和
    total_weight = sum(item.weight for item in items)

    # 随机选择
    random_num = random.uniform(0, total_weight)
    for item in items:
        random_num -= item.weight
        if random_num <= 0:
            break
    else:
        raise ValueError("Random select failed")

    return item.name


class RandomSelectTool(BaseTool):
    __tool_name__ = "random_select"
    __description__ = "从列表中随机选择一个项目，列表中的项目以逗号分隔"
    __command__ = False

    async def __call__(
        self, raw_items: Annotated[str, "项目列表，列表中的项目以逗号分隔"]
    ) -> str:
        items = parse_items(raw_items)
        self.items = items
        return json.dumps(
            {"selected": random_select_from_list(items)}, ensure_ascii=False
        )
