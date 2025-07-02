"""
GiveMeSetuPlugin v0.2
多源图片获取插件，支持Lolicon API和NextCloud，适配多平台发送

原始版本: v0.1 by Hanschase
当前版本: v0.2 by ydzat

主要更新:
- 添加NextCloud支持
- 多平台适配（QQ卡片模式 + Discord直接发送）
- 改进消息解析逻辑
- 模块化重构
- 统一配置管理
"""

from mirai import MessageChain
from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类
from pkg.platform.types import *
from .get_image import get_image
from .nextcloud_client import NextCloudClient
from .message_parser import MessageParser
from .platform_sender import PlatformSender
from .config import Config
import re
import asyncio

# 注册插件
@register(name="GiveMeSetuPlugin", description="多源图片获取插件，支持Lolicon API和NextCloud，适配多平台发送", version="0.2", author="ydzat (基于Hanschase v0.1)")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        super().__init__(host)  # 调用父类初始化
        self.plugin_config = Config()  # 使用不同的名称避免冲突
        self.message_parser = MessageParser()
        self.nextcloud_client = NextCloudClient()
        self.platform_sender = PlatformSender()

    # 异步初始化
    async def initialize(self):
        # 验证配置
        if not self.plugin_config.validate_config():
            self.ap.logger.warning("配置验证失败，部分功能可能不可用")
        
        # 测试NextCloud连接
        try:
            if await self.nextcloud_client.test_connection():
                self.ap.logger.info("NextCloud连接测试成功")
            else:
                self.ap.logger.warning("NextCloud连接测试失败，cloud模式不可用")
        except Exception as e:
            self.ap.logger.warning(f"NextCloud连接测试异常: {e}")

    @handler(PersonMessageReceived)
    @handler(GroupMessageReceived)
    async def message_received(self, ctx: EventContext):
        msg = str(ctx.event.message_chain).strip()
        
        # 解析命令
        parse_result = self.message_parser.parse_command(msg)
        
        if not parse_result['is_valid']:
            return  # 不是有效的命令，忽略
        
        ctx.prevent_default()
        
        source = parse_result['source']
        tags = parse_result['tags']
        r18_flag = parse_result['r18']
        
        self.ap.logger.info(f"接收到命令 - 源:{source}, 标签:{tags}, R18:{r18_flag}")
        
        # 获取图片
        image_info = None
        retry_count = 0
        max_retries = self.plugin_config.MAX_RETRY_COUNT
        
        while retry_count < max_retries and image_info is None:
            try:
                if source == 'auto':
                    # 自动模式：按优先级尝试
                    image_info = await self._get_image_auto(tags, r18_flag)
                elif source == 'lolicon':
                    # Lolicon API
                    image_info = await get_image(tags, r18_flag)
                elif source == 'cloud':
                    # NextCloud
                    if tags:
                        self.ap.logger.info("NextCloud模式忽略标签参数")
                    image_info = await self.nextcloud_client.get_random_image()
                else:
                    await self.platform_sender.send_error_message(ctx, f"未知的图片源: {source}")
                    return
                
                break  # 成功获取，跳出重试循环
                
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                
                self.ap.logger.error(f"获取图片失败 (尝试 {retry_count}/{max_retries}): {error_msg}")
                
                if error_msg == "404" and retry_count < max_retries:
                    # 404错误继续重试
                    continue
                elif retry_count >= max_retries:
                    # 达到最大重试次数
                    await self.platform_sender.send_error_message(ctx, f"获取图片失败，已重试{max_retries}次: {error_msg}")
                    return
                else:
                    # 其他错误直接返回
                    await self.platform_sender.send_error_message(ctx, f"获取图片失败: {error_msg}")
                    return
        
        # 发送图片
        if image_info:
            self.ap.logger.info(f"正在发送图片: {image_info.get('source', 'unknown')}")
            try:
                await self.platform_sender.send_image(ctx, image_info)
                self.ap.logger.info("图片发送成功")
            except Exception as e:
                self.ap.logger.error(f"图片发送失败: {e}")
                await self.platform_sender.send_error_message(ctx, f"图片发送失败: {str(e)}")
        else:
            await self.platform_sender.send_error_message(ctx, "获取图片失败，请稍后重试")
    
    async def _get_image_auto(self, tags, r18_flag):
        """自动模式：按配置的优先级尝试不同的源"""
        for source in self.plugin_config.AUTO_SOURCE_PRIORITY:
            try:
                if source == 'lolicon':
                    return await get_image(tags, r18_flag)
                elif source == 'cloud':
                    if tags:
                        self.ap.logger.info("自动模式切换到NextCloud，忽略标签")
                    return await self.nextcloud_client.get_random_image()
            except Exception as e:
                self.ap.logger.warning(f"自动模式中{source}源失败: {e}")
                continue
        
        # 所有源都失败
        raise Exception("所有图片源都不可用")

    # 插件卸载时触发
    def __del__(self):
        pass
