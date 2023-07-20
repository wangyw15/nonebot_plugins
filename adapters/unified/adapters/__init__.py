from nonebot.adapters import Message as BaseMessage
from nonebot.matcher import current_matcher
from types import MappingProxyType

from .. import message

# 不同适配器
try:
    import nonebot.adapters.onebot.v11 as onebot_v11_module
except ModuleNotFoundError:
    onebot_v11_module = None
try:
    import nonebot.adapters.onebot.v12 as onebot_v12_module
except ModuleNotFoundError:
    onebot_v12_module = None
try:
    import nonebot.adapters.mirai2 as mirai2_module
except ModuleNotFoundError:
    mirai2_module = None
try:
    import nonebot.adapters.qqguild as qq_guild_module
except ModuleNotFoundError:
    qq_guild_module = None
try:
    import nonebot.adapters.kaiheila as kook_module
except ModuleNotFoundError:
    kook_module = None
try:
    import nonebot.adapters.console as console_module
except ModuleNotFoundError:
    console_module = None


SupportedAdapters = MappingProxyType({
    'OneBotV11': 'onebot_v11',
    'OneBotV12': 'onebot_v12',
    'Mirai2': 'mirai2',
    'QQGuild': 'qq_guild',
    'Kook': 'kook',
    'Console': 'console'
})


class AdapterInterface():
    @classmethod
    async def generate_message(cls, msg: message.Message):
        """
        通用消息转特定平台消息

        :param msg: 通用消息对象

        :return: 特定平台消息对象
        """
        final_msg: str = ''  # 在 console 有莫名其妙的问题，所以改为 str
        for seg in msg:
            if seg.type == message.MessageSegmentTypes.TEXT:
                final_msg += seg.data['text']
            elif seg.type == message.MessageSegmentTypes.IMAGE:
                final_msg += f'\n{str(seg)}\n'
            elif seg.type == message.MessageSegmentTypes.AT:
                final_msg += f'@{seg.data["user_id"]}'
        return final_msg.strip()

    @classmethod
    async def parse_message(cls, msg: BaseMessage) -> message.Message:
        """
        特定平台的消息解析为通用消息

        :param msg: 消息对象

        :return: 通用消息对象
        """
        return message.Message(msg.extract_plain_text())

    @classmethod
    async def send(cls, msg: message.Message) -> None:
        """
        发送消息

        :param msg: 消息对象
        """
        await current_matcher.get().send(await cls.generate_message(msg))

    @classmethod
    async def finish(cls, msg: message.Message) -> None:
        """
        发送消息并结束会话

        :param msg: 消息对象
        """
        await current_matcher.get().finish(await cls.generate_message(msg))


__all__ = ['SupportedAdapters',
           'AdapterInterface',
           'onebot_v11_module',
           'onebot_v12_module',
           'mirai2_module',
           'kook_module',
           'console_module',
           'qq_guild_module'
           ]
