import json
import random
from typing import Tuple

from essentials.libraries import render_by_browser
from storage import asset
from .bestdori import band_character, card, gacha, util

_assets = asset.AssetManager("bang_dream")


async def gacha10(gacha_id: str, language: str = "cn") -> Tuple[dict[str], str]:
    """
    一发十连

    :params gacha_id: 卡池ID
    :params language: 语言

    :return: 抽卡结果, 语言
    """
    # 获取卡池信息
    data = await gacha.get_gacha_info(gacha_id)

    # 获取权重
    rates: dict[str]
    rates, language = util.get_content_by_language(data["rates"], language)

    # 计算总概率和三星及以上概率
    total_rate = 0
    better_than_three_star_rate = 0
    for k, v in rates.items():
        total_rate += v["rate"]
        if int(k) >= 3:
            better_than_three_star_rate += v["rate"]

    # 卡池内的卡片信息
    cards: dict[str]
    cards, language = util.get_content_by_language(data["details"], language)

    # 抽卡结果
    result_card_ids = []
    result_cards = {}
    # 保底
    three_star_appeared = False

    for i in range(10):
        # 随机概率
        rate = random.randint(1, total_rate * 10) / 10
        # 计算稀有度
        rarity = "1"
        for k, v in rates.items():
            if rate <= v["rate"]:
                rarity = k
                break
            rate -= v["rate"]

        # 保底三星及以上
        three_star_appeared = int(rarity) >= 3 or three_star_appeared
        if i == 9 and not three_star_appeared:
            rarity = "3"
            rate = random.randint(1, better_than_three_star_rate * 10) / 10
            for j in ["3", "4", "5"]:
                if rate <= rates[j]["rate"]:
                    rarity = j
                    break
                rate -= rates[j]["rate"]

        # 随机卡片
        weight = random.randint(1, rates[rarity]["weightTotal"])
        card_id = "1"
        for k, v in cards.items():
            if str(v["rarityIndex"]) != rarity:
                continue
            if weight <= v["weight"]:
                card_id = k
                break
            weight -= v["weight"]
        result_card_ids.append(card_id)

    # 获取卡片信息
    for card_id in result_card_ids:
        result_cards[card_id] = await card.get_card_info(card_id)

    return result_cards, language


async def generate_data_for_image(gacha_data: dict[str]) -> list[dict[str]]:
    result = []
    characters: dict[str] = await band_character.get_character_list()
    for card_id, card_data in gacha_data.items():
        result.append(
            {
                "id": card_id,
                "band": characters[str(card_data["characterId"])]["bandId"],
                "rarity": card_data["rarity"],
                "attribute": card_data["attribute"],
                "resource": card_data["resourceSetName"],
            }
        )
    return result


async def generate_image(gacha_data: dict[str]) -> bytes:
    """
    生成抽卡图片

    :params gacha_data: 抽卡数据

    :return: 图片
    """
    data = await generate_data_for_image(gacha_data)
    generated_html = (
        _assets("gacha.html")
        .read_text()
        .replace("'{{DATA_HERE}}'", json.dumps(data, ensure_ascii=False))
    )

    return await render_by_browser.render_html(
        generated_html, _assets(), viewport={"width": 1920, "height": 1080}
    )


def generate_text(gacha_data: dict[str], language: str = "cn") -> str:
    """
    生成抽卡文字

    :params gacha_data: 抽卡数据
    :params language: 语言

    :return: 文字
    """
    result = ""
    for card_id, card_data in gacha_data.items():
        card_name, language = util.get_content_by_language(
            card_data["prefix"], language
        )
        result += f'{card_data["rarity"]}★ {card_name}\n'
    return result.strip()
