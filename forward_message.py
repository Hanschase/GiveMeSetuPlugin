import json
import aiohttp
import os

class forward_message():
    def __init__(self, host:str, port: int):
        self.url = f"http://{host}:{port}"

    async def send(self, group_id:str, img_info:list):
        image = self.get_media_path(img_info[3])
        message_data = {
            "group_id": group_id,
            "user_id": "1900487324",
            "messages": [
                {
                    "type": "node",
                    "data": {
                        "user_id": "3870128501",
                        "nickname": "BOT",
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
            "prompt": "冲就完事儿了",
            "summary": "一天就知道冲冲冲",
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
