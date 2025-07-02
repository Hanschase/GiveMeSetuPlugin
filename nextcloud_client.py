"""
NextCloud客户端模块
用于连接NextCloud服务器并获取图片
"""

import aiohttp
import aiofiles
import random
import os
from typing import List, Optional, Dict, Any
from .config import Config
import base64
import xml.etree.ElementTree as ET


class NextCloudClient:
    def __init__(self, base_url: str = None, username: str = None, 
                 password: str = None, folder_path: str = None):
        """初始化NextCloud客户端，优先使用传入参数，否则使用配置文件"""
        self.config = Config()
        self.base_url = base_url or self.config.NEXTCLOUD_URL
        self.username = username or self.config.NEXTCLOUD_USERNAME
        self.password = password or self.config.NEXTCLOUD_PASSWORD
        self.folder_path = folder_path or self.config.NEXTCLOUD_FOLDER
        self.timeout = self.config.NEXTCLOUD_TIMEOUT
        self.supported_formats = self.config.SUPPORTED_FORMATS
        
        # 缓存
        self._image_list_cache = None
        self._cache_timestamp = 0
        
        # WebDAV URL
        self.webdav_url = self._get_webdav_url()
        
        # 认证头
        self.auth_header = self._get_auth_header()
    
    def _get_webdav_url(self) -> str:
        """获取WebDAV URL"""
        webdav_path = self.config.NEXTCLOUD_WEBDAV_PATH.format(username=self.username)
        return f"{self.base_url.rstrip('/')}{webdav_path}{self.folder_path}"
    
    def _get_auth_header(self) -> str:
        """获取认证头"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    async def get_random_image(self) -> Dict[str, Any]:
        """
        从指定文件夹随机获取图片
        返回: {
            'source': 'cloud',
            'filename': str,
            'image_path': str
        }
        """
        try:
            # 获取图片列表
            image_list = await self.list_images()
            
            if not image_list:
                raise Exception("NextCloud文件夹中没有找到图片")
            
            # 随机选择一张图片
            selected_image = random.choice(image_list)
            
            # 下载图片
            image_path = await self._download_image(selected_image['href'])
            
            return {
                'source': 'cloud',
                'filename': selected_image['name'],
                'image_path': image_path
            }
            
        except Exception as e:
            raise Exception(f"NextCloud获取图片失败: {str(e)}")
    
    async def list_images(self) -> List[Dict[str, str]]:
        """
        列出文件夹中的所有图片
        返回图片文件信息列表
        """
        import time
        current_time = time.time()
        
        # 检查缓存是否有效
        if (self._image_list_cache and 
            current_time - self._cache_timestamp < self.config.NEXTCLOUD_CACHE_DURATION):
            return self._image_list_cache
        
        try:
            # WebDAV PROPFIND请求
            headers = {
                'Authorization': self.auth_header,
                'Content-Type': 'application/xml',
                'Depth': '1'
            }
            
            # PROPFIND请求体
            propfind_body = '''<?xml version="1.0" encoding="utf-8" ?>
            <d:propfind xmlns:d="DAV:">
                <d:prop>
                    <d:displayname/>
                    <d:getcontenttype/>
                    <d:resourcetype/>
                </d:prop>
            </d:propfind>'''
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    'PROPFIND', 
                    self.webdav_url,
                    headers=headers,
                    data=propfind_body
                ) as response:
                    
                    if response.status == 404:
                        raise Exception(f"NextCloud文件夹不存在: {self.folder_path}")
                    elif response.status == 401:
                        raise Exception("NextCloud认证失败，请检查用户名和密码")
                    elif response.status != 207:  # WebDAV Multi-Status
                        raise Exception(f"NextCloud请求失败: {response.status}")
                    
                    # 解析响应
                    xml_content = await response.text()
                    image_list = self._parse_webdav_response(xml_content)
                    
                    # 更新缓存
                    self._image_list_cache = image_list
                    self._cache_timestamp = current_time
                    
                    return image_list
                    
        except aiohttp.ClientError as e:
            raise Exception(f"NextCloud连接失败: {str(e)}")
    
    def _parse_webdav_response(self, xml_content: str) -> List[Dict[str, str]]:
        """解析WebDAV响应，提取图片文件信息"""
        image_list = []
        
        try:
            # 解析XML
            root = ET.fromstring(xml_content)
            
            # 查找所有response元素
            for response in root.findall('.//{DAV:}response'):
                # 获取文件路径
                href_elem = response.find('.//{DAV:}href')
                if href_elem is None:
                    continue
                
                href = href_elem.text
                
                # 获取文件名
                displayname_elem = response.find('.//{DAV:}displayname')
                if displayname_elem is None:
                    # 从href中提取文件名
                    filename = href.split('/')[-1]
                else:
                    filename = displayname_elem.text
                
                # 检查是否是文件夹
                resourcetype_elem = response.find('.//{DAV:}resourcetype')
                if resourcetype_elem is not None and resourcetype_elem.find('.//{DAV:}collection') is not None:
                    continue  # 跳过文件夹
                
                # 检查是否是图片文件
                if self._is_image_file(filename):
                    image_list.append({
                        'name': filename,
                        'href': href
                    })
                    
        except ET.ParseError as e:
            raise Exception(f"解析NextCloud响应失败: {str(e)}")
        
        return image_list
    
    async def _download_image(self, file_href: str) -> str:
        """下载图片到本地临时文件"""
        try:
            # 构建完整的下载URL
            download_url = f"{self.base_url.rstrip('/')}{file_href}"
            
            headers = {
                'Authorization': self.auth_header
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.IMAGE_DOWNLOAD_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(download_url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(f"下载图片失败: {response.status}")
                    
                    # 检查文件大小
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.config.MAX_IMAGE_SIZE * 1024 * 1024:
                        raise Exception(f"图片文件过大: {content_length} bytes")
                    
                    # 保存到临时文件
                    temp_path = self.config.TEMP_IMAGE_NAME
                    async with aiofiles.open(temp_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
                    
                    return temp_path
                    
        except aiohttp.ClientError as e:
            raise Exception(f"下载图片失败: {str(e)}")
    
    def _is_image_file(self, filename: str) -> bool:
        """检查文件是否为支持的图片格式"""
        if not filename:
            return False
        return any(filename.lower().endswith(fmt) for fmt in self.supported_formats)
    
    async def test_connection(self) -> bool:
        """测试NextCloud连接"""
        try:
            await self.list_images()
            return True
        except Exception:
            return False
