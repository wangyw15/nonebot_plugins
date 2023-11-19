import random
import difflib
from typing import Annotated

from nonebot import on_shell_command
from nonebot.adapters import MessageSegment
from nonebot.params import ShellCommandArgv
from nonebot.plugin import PluginMetadata

from . import bangdream
from adapters import unified

# TODO 记得改
__plugin_meta__ = PluginMetadata(
    name='Bang Dream',
    description='邦邦功能',
    usage='还在做',
    config=None
)

_bangdream_handler = on_shell_command('bangdream', aliases={'bang', '邦邦', '邦'}, block=True)


# TODO 模拟抽卡、查卡、点歌、签到主题、活动助手等
@_bangdream_handler.handle()
async def _(args: Annotated[list[str | MessageSegment], ShellCommandArgv()]):
    if len(args) == 0:
        await _bangdream_handler.finish('想要什么喵？')
    if args[0].lower() in ['comic', 'comics', '漫画', '小漫画']:
        comics = await bangdream.get_comic_list()
        if len(args) == 1:  # 随机所有小漫画
            comic_id = random.choice(list(comics.keys()))
        elif len(args) == 2 and args[1] in ['四格']:  # 随机四格
            comic_id = random.choice([i for i in comics if len(i) == 4 and i.startswith('1')])
        elif len(args) == 2 and args[1] in ['单格']:  # 随机单格
            comic_id = random.choice([i for i in comics if len(i) == 3])
        else:  # 搜素漫画
            keyword = ' '.join(args[1:]).strip()
            comic_id = None
            if keyword.isdigit():  # 指定id
                comic_id = keyword
            else:  # 搜索名字
                best_match = 0.0
                for _comic_id, comic in comics.items():
                    for _title in comic['title']:
                        ratio = difflib.SequenceMatcher(None, keyword, str(_title)).quick_ratio()
                        if ratio > best_match:
                            best_match = ratio
                            comic_id = _comic_id
            if comic_id not in comics:
                await _bangdream_handler.finish('没有找到这个漫画喵')
        # 发送漫画
        title, _ = bangdream.get_content_by_language(comics[comic_id]['title'])
        if unified.Detector.can_send_image():
            content, _ = await bangdream.get_comic(comic_id)
            await _bangdream_handler.finish(unified.MessageSegment.text(title) +
                                            unified.MessageSegment.image(content))
        else:
            await _bangdream_handler.finish(f'{title}\nhttps://bestdori.com/info/comics/{comic_id}')

