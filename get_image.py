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
        return [pid,title,author, img_url]
    except Exception as e:
        raise e
