import random

from canrotbot.libraries import arknights as libarknights
from .. import fortune


async def _generate_arknights_html() -> str:
    rarity = random.choice(list(libarknights.gacha_operators.keys()))
    operator: dict = random.choice(libarknights.gacha_operators[rarity])
    operator_prefab_key = operator["phases"][0]["characterPrefabKey"]
    with (fortune.ASSET_PATH / "template" / "arknights.html").open(
        "r", encoding="utf-8"
    ) as f:
        return f.read().replace("{{resource_key}}", operator_prefab_key)


fortune.register_theme(
    "arknights",
    _generate_arknights_html,
    ["明日方舟", "方舟", "鹰角", "Arknights", "舟游"],
)
