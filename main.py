from mirai import MessageChain
from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from pkg.platform.types import *
from plugins.GiveMeSetuPlugin.get_image import get_image
import re
from plugins.GiveMeSetuPlugin.forward_message import forward_message

# 注册插件
@register(name="GiveMeSetuPlugin", description="功能正如其名，让她给，她不得不给！", version="0.2", author="Hanschase")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.forward_message = forward_message(host="127.0.0.1", port=3000)


    # 异步初始化
    async def initialize(self):
        pass

    @handler(PersonMessageReceived)
    @handler(GroupMessageReceived)
    async def message_received(self, ctx: EventContext):
        msg = str(ctx.event.message_chain).strip()
        #msg = ctx.event.text_message.strip()
        if re.search(r'setu|涩图|色图', msg, re.IGNORECASE):
            ctx.prevent_default()
            msg = msg.split(" ")
            if len(msg)==1 or len(msg)>2:
                keyword = ""
            else:
                keyword = msg[1]
            r18_flag = 1 if 'r' in msg[0].lower() else 0
            self.ap.logger.info(f"接收到关键词{keyword}")
            loop_flag = 3# 重定向次数
            while loop_flag:
                try:
                    img_info = await get_image(keyword, r18_flag)
                    self.ap.logger.info(f"Image info：{img_info}")
                    loop_flag = 0
                except Exception as e:
                    print(str(e))
                    if str(e) == "404":
                        self.ap.logger.error("未查询到图片，正在进行重定向")
                        loop_flag -= 1
                    else:
                        await ctx.send_message(ctx.event.launcher_type, str(ctx.event.launcher_id),MessageChain([f"发生了一个错误：{e}"]))
                        self.ap.logger.error(e)
                        return
            self.ap.logger.info(f"正在发送图片...")
            #await ctx.send_message(ctx.event.launcher_type, str(ctx.event.launcher_id),MessageChain(["已获取图片，正在发送...（没发送出来就是被风控了）"]))
            # await ctx.send_message(ctx.event.launcher_type, str(ctx.event.launcher_id), MessageChain([f"pid:{img_info[0]}\n",
            #                                                                                     f"title:{img_info[1]}\n",
            #                                                                                     f"author:{img_info[2]}\n",
            #                                                                                    Image(path="temp.png")]))
            await self.forward_message.send(str(ctx.event.launcher_id), img_info)

    # 插件卸载时触发
    def __del__(self):
        pass
