from nonebot import get_driver, on_command, on_regex
from nonebot.adapters import Message, Event, Bot
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule
from pydantic import BaseModel, validator
import requests

from ..universal_adapters import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name='Steam助手',
    description='现在只能根据 appid 查询信息',
    usage='/<steam|sbeam|蒸汽|蒸汽平台> <appid>',
    config=None
)

# config
class SteamConfig(BaseModel):
    aio_proxy: str = ''
    steam_region: str = 'cn'
    steam_language: str = 'zh-cn'
    
    @validator('aio_proxy')
    def aio_proxy_validator(cls, v):
        if not isinstance(v, str):
            raise ValueError('aio_proxy must be a str')
        return v
    
    @validator('steam_region')
    def steam_region_validator(cls, v):
        if (not isinstance(v, str)) or (not v):
            raise ValueError('steam_region must be a str')
        return v
    
    @validator('steam_language')
    def steam_language_validator(cls, v):
        if (not isinstance(v, str)) or (not v):
            raise ValueError('steam_language must be a str')
        return v

config = SteamConfig.parse_obj(get_driver().config)

# fetch app info from appid
def fetch_app_info(appid: int) -> dict | None:
    if config.aio_proxy:
        proxy = {'https': config.aio_proxy, 'http': config.aio_proxy}
    else:
        proxy = {}
    resp = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={appid}&l={config.steam_language}&cc={config.steam_region}', 
                        proxies=proxy,
                        headers={'Accept-Language': config.steam_language})
    if resp.ok and resp.status_code == 200:
        return resp.json()
    return None

def fetch_data(url: str) -> bytes | None:
    resp = requests.get(url)
    if resp.ok and resp.status_code == 200:
        return resp.content
    return None

def generate_message(app_info: dict) -> str:
    name: str = app_info['name']
    appid: int = app_info['steam_appid']
    desc: str = app_info['short_description']
    coming_soon: bool = app_info['release_date']['coming_soon']
    release_date: str = app_info['release_date']['date']
    developers: list[str] = app_info['developers']
    publishers: list[str] = app_info['publishers']
    genres: list[str] = [x['description'] for x in app_info['genres']]
    categories: list[str] = [x['description'] for x in app_info['categories']]
    initial_price: str = app_info['price_overview']['initial_formatted']
    final_price:str = app_info['price_overview']['final_formatted']
    discount_percentage: int = app_info['price_overview']['discount_percent']

    ret = f"""
名称: {name}
发布时间: {'待发售' if coming_soon else release_date}
开发商: {', '.join(developers)}
发行商: {', '.join(publishers)}
类型: {', '.join(genres)}
分类: {', '.join(categories)}
简介: {desc}
    """.strip()

    if discount_percentage != 0:
        ret += f'\n原价: {initial_price}\n现价: {final_price}\n折扣: {discount_percentage}%'
    else:
        ret += f'\n价格: {final_price}'

    ret += f'\n链接: https://store.steampowered.com/app/{appid}'
    return ret

steam = on_command('steam', aliases={'sbeam', '蒸汽', '蒸汽平台'}, block=True)
@steam.handle()
async def _(bot: Bot, args: Message = CommandArg()):
    if msg := args.extract_plain_text():
        if msg.isdigit():
            if appinfo := fetch_app_info(msg):
                if appinfo.get(msg, {}).get('success', False):
                    appinfo = appinfo[msg]['data']
                    header_img = appinfo['header_image']
                    bg_img = appinfo['background_raw']

                    header_img_msg = await get_image_message_from_url(bot, header_img)
                    text_msg = generate_message(appinfo)
                    bg_img_msg = await get_image_message_from_url(bot, bg_img)
                    if is_onebot_v11(bot) or is_onebot_v12(bot) or is_mirai2(bot):
                        await steam.finish(header_img_msg + '\n' + text_msg + '\n' + bg_img_msg)
                    elif is_kook(bot):
                        await steam.send(header_img_msg)
                        await steam.send(text_msg)
                        await steam.finish(bg_img_msg)
                    else:
                        await steam.finish(text_msg)
                else:
                    await steam.finish('未找到该游戏')
            else:
                await steam.finish('请求失败')
        else:
            await steam.finish('请输入正确的游戏ID')
