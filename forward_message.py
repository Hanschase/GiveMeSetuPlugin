import json
import aiohttp
import os
from .config import Config

class forward_message():
    def __init__(self, host:str = None, port: int = None):
        self.config = Config()
        self.host = host or self.config.NAPCAT_HOST
        self.port = port or self.config.NAPCAT_PORT
        self.url = f"http://{self.host}:{self.port}"

    async def send(self, group_id:str, img_info:list):
        image = self.get_media_path(self.config.TEMP_IMAGE_NAME)
        message_data = {
            "group_id": group_id,
            "user_id": self.config.FORWARD_USER_ID,
            "messages": [
                {
                    "type": "node",
                    "data": {
                        "user_id": self.config.BOT_QQ,
                        "nickname": self.config.BOT_NICKNAME,
                        "content": [
                            {
                                "type": "text",
                                "data": {
                                    "text": f"pid:{img_info[0]}\ntitle:{img_info[1]}\nauthor:{img_info[2]}"
                                }
                            },
                            {
                                "type": "image",
                                "data": {
                                    "file": image,
                                }
                            }
                        ]
                    }
                }
            ],
            "news": [
                {
                    "text": f"pid:{img_info[0]}"
                }
            ],
            "prompt": self.config.CARD_MESSAGE_CONFIG["prompt"],
            "summary": self.config.CARD_MESSAGE_CONFIG["summary"],
            "source": img_info[1]
        }
        headers = {
            'Content-Type': 'application/json'
        }
        payload = json.dumps(message_data)
        async with aiohttp.ClientSession(self.url, headers=headers) as session:
            async with session.post("/send_forward_msg", data=payload) as response:
                await response.json()
                print(response)

    def get_media_path(self, media_path):
        """
        获取媒体的本地绝对路径或网络路径
        """
        if media_path:
            if media_path.startswith('http'):
                return media_path
            elif os.path.isfile(media_path):
                abspath = os.path.abspath(os.path.join(os.getcwd(), media_path)).replace('\\', '\\\\')
                return f"file:///{abspath}"
        return ''