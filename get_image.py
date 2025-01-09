import httpx
import sys
import asyncio
import json
import re

async def get_json(keyword: str,r18_flag: int = 0):
    url = "https://api.lolicon.app/setu/v2"
    params = {
        "keyword": keyword,
        "num": 1,
        "r18": r18_flag,
        "size": "regular",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        return response

async def download_image(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 404:
            raise Exception(404)
        content = response.content
        import aiofiles
        async with aiofiles.open("temp.jpg", 'wb') as f:
            await f.write(content)

async def get_image(keyword: str, r18_flag: int = 0):
    img = await get_json(keyword, r18_flag)
    img = img.json()
    if img["data"] == []:
        raise Exception("输入了未知的tag")
    pid = img["data"][0]["pid"]
    title = img["data"][0]["title"]
    author = img["data"][0]["author"]
    img_url = img["data"][0]["urls"]["regular"]
    try:
        await download_image(img_url)
        return [pid,title,author]
    except Exception as e:
        raise e

async def main():
    msg = "setu 公主连接".strip()
    r18_flag = 0
    if re.search(r'setu|涩图|色图', msg, re.IGNORECASE):
        msg = msg.split(" ")
        keyword = msg[1]
        if 'r' in msg[0] or 'R' in msg[0]:
            r18_flag = 1
        try:
            img_info = await get_image(keyword, r18_flag)
        except Exception as e:
            print(e)
            return
        img_info = await get_image(keyword, r18_flag)
        print(msg)
        print(keyword, r18_flag)
        print(img_info)
if __name__ == "__main__":
    asyncio.run(main())
    pass