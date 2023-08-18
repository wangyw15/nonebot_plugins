import base64

from nonebot import on_command
from nonebot.params import Message, CommandArg
from nonebot.plugin import PluginMetadata
from tencentcloud.aiart.v20221229 import aiart_client, models
from tencentcloud.common import credential

from adapters import unified
from essentials.libraries import config, user, economy

__plugin_meta__ = PluginMetadata(
    name='AI 作画',
    description='使用了腾讯云的 AI 作画',
    usage='/ai <正向提示词>|<反向提示词>|<风格>',
    config=None
)


_tencent_api_secret_id: str = config.get_config('tencent_api_secret_id')
_tencent_api_secret_key: str = config.get_config('tencent_api_secret_key')
if not all([_tencent_api_secret_id, _tencent_api_secret_key]):
    raise ValueError('腾讯云 API 密钥未配置')
_credential = credential.Credential(_tencent_api_secret_id, _tencent_api_secret_key)

_client = aiart_client.AiartClient(_credential, 'ap-shanghai')

_ai_art_handler = on_command('ai', aliases={'AI'}, block=True)


@_ai_art_handler.handle()
async def _(msg: Message = CommandArg()):
    uid = user.get_uid()
    if not uid:
        await _ai_art_handler.finish('未注册用户无法使用 AI 作画')
        return
    if not economy.pay(uid, 100, 'AI 作画'):
        await _ai_art_handler.finish('余额不足')
        return
    await _ai_art_handler.send('谢谢你的100个胡萝卜片喵~正在努力画画呢~')
    if args := msg.extract_plain_text():
        split = args.split('|')
        if len(split) == 3:
            positive = split[0].strip()
            negative = split[1].strip()
            styles = split[2].strip().split(',')
        elif len(split) == 2:
            positive = split[0].strip()
            negative = split[1].strip()
            styles = ['201']
        elif len(split) == 1:
            positive = split[0].strip()
            negative = ''
            styles = ['201']
        else:
            await _ai_art_handler.finish('参数错误')
            return
        # 生成请求
        req = models.TextToImageRequest()
        req.Prompt = positive
        req.NegativePrompt = negative
        req.Styles = styles
        result_config = models.ResultConfig()
        result_config.Resolution = '768:1024'
        req.ResultConfig = result_config
        req.LogoAdd = 0
        req.RspImgType = 'base64'
        # 发送请求
        resp = _client.TextToImage(req)
        await unified.MessageSegment.image(base64.b64decode(resp.ResultImage)).send()
        await _ai_art_handler.finish()

