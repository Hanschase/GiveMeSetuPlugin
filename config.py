"""
GiveMeSetuPlugin 配置管理模块
统一管理所有配置项，便于维护和扩展
"""

class Config:
    # ==================== Lolicon API 配置 ====================
    # Lolicon API地址
    LOLICON_API_URL = "https://api.lolicon.app/setu/v2"
    
    # 默认请求参数
    LOLICON_DEFAULT_PARAMS = {
        "num": 1,
        "size": "regular",  # regular, original, small
    }
    
    # API请求超时时间(秒)
    LOLICON_TIMEOUT = 30
    
    # ==================== NextCloud 配置 ====================
    # NextCloud服务器地址
    NEXTCLOUD_URL = "https://your-nextcloud-domain.com"
    
    # NextCloud用户名
    NEXTCLOUD_USERNAME = "your_username"
    
    # NextCloud应用专用密码（推荐使用应用密码而非账户密码）
    NEXTCLOUD_PASSWORD = "your_app_password"
    
    # NextCloud图片文件夹路径
    NEXTCLOUD_FOLDER = "/Pictures/Setu"
    
    # NextCloud WebDAV路径
    NEXTCLOUD_WEBDAV_PATH = "/remote.php/dav/files/{username}"
    
    # 连接超时时间(秒)
    NEXTCLOUD_TIMEOUT = 30
    
    # ==================== 消息转发配置 ====================
    # Napcat服务器地址
    NAPCAT_HOST = "127.0.0.1"
    
    # Napcat服务器端口
    NAPCAT_PORT = 3000
    
    # 发送消息的用户ID(用于卡片消息显示)
    FORWARD_USER_ID = "1900487324"
    
    # BOT昵称(用于卡片消息显示)
    BOT_NICKNAME = "BOT"
    
    # BOT的QQ号(用于卡片消息显示)
    BOT_QQ = "3870128501"
    
    # 卡片消息配置
    CARD_MESSAGE_CONFIG = {
        "prompt": "冲就完事儿了",
        "summary": "一天就知道冲冲冲"
    }
    
    # ==================== 图片处理配置 ====================
    # 支持的图片格式
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    
    # 临时图片文件名（使用绝对路径）
    import os
    TEMP_IMAGE_NAME = os.path.abspath("temp.jpg")
    
    # 图片下载超时时间(秒)
    IMAGE_DOWNLOAD_TIMEOUT = 60
    
    # 最大图片文件大小(MB)
    MAX_IMAGE_SIZE = 50
    
    # ==================== 应用行为配置 ====================
    # 默认图片源 (auto, lolicon, cloud)
    DEFAULT_SOURCE = "auto"
    
    # 自动模式下的源选择策略
    AUTO_SOURCE_PRIORITY = ["lolicon", "cloud"]
    
    # 错误重试次数
    MAX_RETRY_COUNT = 3
    
    # R18内容开关 (0: 关闭, 1: 开启, 2: 随机)
    DEFAULT_R18_FLAG = 0
    
    # 启用详细日志
    ENABLE_DEBUG_LOG = True
    
    # NextCloud文件列表缓存时间(秒)
    NEXTCLOUD_CACHE_DURATION = 300  # 5分钟
    
    # 临时文件清理间隔(秒)
    TEMP_FILE_CLEANUP_INTERVAL = 3600  # 1小时
    
    # ==================== 平台检测配置 ====================
    # 支持卡片消息的平台列表
    CARD_SUPPORTED_PLATFORMS = ["qq", "onebot"]
    
    # 平台类型映射
    PLATFORM_TYPE_MAPPING = {
        "onebot": "qq",
        "qq": "qq", 
        "discord": "discord",
        "telegram": "telegram",
        "lark": "lark",
        "wecom": "wecom",
        "slack": "slack",
        "unknown": "default"
    }
    
    # 不同平台的消息格式
    PLATFORM_MESSAGE_FORMATS = {
        "qq": "card",      # 卡片模式
        "discord": "text", # 纯文本模式
        "telegram": "text",
        "default": "text"
    }
    
    @classmethod
    def get_nextcloud_webdav_url(cls) -> str:
        """获取完整的NextCloud WebDAV URL"""
        webdav_path = cls.NEXTCLOUD_WEBDAV_PATH.format(username=cls.NEXTCLOUD_USERNAME)
        return f"{cls.NEXTCLOUD_URL.rstrip('/')}{webdav_path}"
    
    @classmethod
    def get_napcat_url(cls) -> str:
        """获取完整的Napcat API URL"""
        return f"http://{cls.NAPCAT_HOST}:{cls.NAPCAT_PORT}"
    
    @classmethod
    def is_platform_support_card(cls, platform: str) -> bool:
        """检查平台是否支持卡片消息"""
        return platform.lower() in cls.CARD_SUPPORTED_PLATFORMS
    
    @classmethod
    def get_platform_message_format(cls, platform: str) -> str:
        """获取平台的消息格式"""
        return cls.PLATFORM_MESSAGE_FORMATS.get(platform.lower(), cls.PLATFORM_MESSAGE_FORMATS["default"])
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置完整性"""
        required_configs = [
            'NEXTCLOUD_URL', 'NEXTCLOUD_USERNAME', 'NEXTCLOUD_PASSWORD',
            'NAPCAT_HOST', 'NAPCAT_PORT'
        ]
        return all(hasattr(cls, config) and getattr(cls, config) for config in required_configs)
