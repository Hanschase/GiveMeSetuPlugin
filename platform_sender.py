"""
平台适配发送模块
根据不同平台采用不同的发送方式
"""

from typing import Dict, Any
from pkg.platform.types.message import MessageChain, Image, Plain
from pkg.plugin.context import EventContext
from .config import Config
from .forward_message import forward_message


class PlatformSender:
    def __init__(self, forward_message_host: str = None, forward_message_port: int = None):
        """初始化平台发送器"""
        self.config = Config()
        self.forward_message_client = forward_message(
            host=forward_message_host or self.config.NAPCAT_HOST,
            port=forward_message_port or self.config.NAPCAT_PORT
        )
    
    async def send_image(self, ctx: EventContext, image_info: Dict[str, Any]):
        """根据平台类型发送图片"""
        platform = self.detect_platform(ctx)
        message_format = self.config.get_platform_message_format(platform)
        
        if message_format == "card":
            await self._send_card_message(ctx, image_info)
        else:
            await self._send_text_message(ctx, image_info)
    
    def detect_platform(self, ctx: EventContext) -> str:
        """检测消息平台类型"""
        # 通过适配器类名检测平台类型
        adapter_class_name = ctx.event.query.adapter.__class__.__name__
        
        # 将适配器类名映射到平台类型
        adapter_name_mapping = {
            "AiocqhttpAdapter": "onebot",
            "NakuruAdapter": "onebot", 
            "OfficialAdapter": "qq",
            "QQOfficialAdapter": "qq",
            "DiscordAdapter": "discord",
            "TelegramAdapter": "telegram",
            "LarkAdapter": "lark",
            "WecomAdapter": "wecom",
            "SlackAdapter": "slack"
        }
        
        adapter_type = adapter_name_mapping.get(adapter_class_name, "unknown")
        return self.config.PLATFORM_TYPE_MAPPING.get(adapter_type, "default")
    
    async def _send_card_message(self, ctx: EventContext, image_info: Dict[str, Any]):
        """发送卡片消息（QQ平台）"""
        try:
            if image_info['source'] == 'lolicon':
                # Lolicon来源，使用现有的卡片格式
                lolicon_info = [
                    image_info['pid'],
                    image_info['title'], 
                    image_info['author']
                ]
                await self.forward_message_client.send(str(ctx.event.launcher_id), lolicon_info)
            else:
                # NextCloud来源，使用简化的卡片格式
                await self._send_nextcloud_card(ctx, image_info)
        except Exception as e:
            # 卡片发送失败，降级为文本发送
            await self._send_text_message(ctx, image_info)
    
    async def _send_nextcloud_card(self, ctx: EventContext, image_info: Dict[str, Any]):
        """发送NextCloud图片的卡片消息"""
        # 使用forward_message的send方法，但传入特殊格式的数据
        nextcloud_info = [
            "NextCloud",  # 作为pid使用
            image_info['filename'],  # 作为title使用
            "Local Storage"  # 作为author使用
        ]
        await self.forward_message_client.send(str(ctx.event.launcher_id), nextcloud_info)
    
    async def _send_text_message(self, ctx: EventContext, image_info: Dict[str, Any]):
        """发送文本消息（Discord等平台）"""
        try:
            if image_info['source'] == 'lolicon':
                # Lolicon来源的文本格式
                text_content = f"""🎨 图片信息
📝 标题: {image_info['title']}
👤 作者: {image_info['author']}
🆔 PID: {image_info['pid']}
🏷️ 标签: {', '.join(image_info['tags']) if image_info['tags'] else '无'}
📦 来源: Lolicon API"""
            else:
                # NextCloud来源的文本格式
                text_content = f"""🎨 图片信息
📁 文件名: {image_info['filename']}
📦 来源: NextCloud"""
            
            # 清理和处理图片路径
            image_path = image_info['image_path']
            # 确保路径不包含空字节
            if '\x00' in image_path:
                image_path = image_path.replace('\x00', '')
            
            # 转换为绝对路径
            import os
            image_path = os.path.abspath(image_path)
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise Exception(f"图片文件不存在: {image_path}")
            
            # 发送文本和图片
            message_chain = MessageChain([
                Plain(text=text_content),
                Image(path=image_path)
            ])
            
            await ctx.send_message(
                ctx.event.launcher_type, 
                str(ctx.event.launcher_id),
                message_chain
            )
            
        except Exception as e:
            # 发送失败，只发送错误信息
            await ctx.send_message(
                ctx.event.launcher_type,
                str(ctx.event.launcher_id),
                MessageChain([Plain(text=f"图片发送失败: {str(e)}")])
            )
    
    async def send_error_message(self, ctx: EventContext, error_msg: str):
        """发送错误消息"""
        try:
            await ctx.send_message(
                ctx.event.launcher_type,
                str(ctx.event.launcher_id),
                MessageChain([Plain(text=f"❌ {error_msg}")])
            )
        except Exception:
            # 如果连错误消息都发送失败，就不做任何处理
            pass
    
    async def send_help_message(self, ctx: EventContext, help_text: str):
        """发送帮助消息"""
        try:
            await ctx.send_message(
                ctx.event.launcher_type,
                str(ctx.event.launcher_id),
                MessageChain([Plain(text=help_text)])
            )
        except Exception:
            pass
