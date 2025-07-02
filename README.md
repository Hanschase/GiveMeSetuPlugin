# GiveMeSetuPlugin

基于 LangBot 的多源图片获取插件，支持从 Lolicon API 和 NextCloud 获取图片，具备多平台适配能力。

## 特性

- 🌍 **多平台支持**：支持 QQ（卡片模式）、Discord（直接发送）等平台
- � **多图片源**：支持 Lolicon API 和 NextCloud 两种图片源
- � **智能解析**：精确匹配关键词，支持参数解析
- 🔄 **自动降级**：API 失败时自动切换到备用源
- ⚙️ **配置化**：所有参数都可以在配置文件中修改
- 🛡️ **错误处理**：完善的重试机制和友好的错误提示

## 版本信息

- **当前版本**：v0.2 by ydzat
- **原始版本**：v0.1 by Hanschase

### 主要更新
- 添加 NextCloud 支持
- 多平台适配（QQ 卡片模式 + Discord 直接发送）
- 改进消息解析逻辑
- 模块化重构
- 统一配置管理

## 安装

### 前置要求

1. 已安装并配置 [LangBot](https://github.com/RockChinQ/LangBot) 主程序
2. 如果使用 QQ 平台，需要配置 NapCat 适配器
3. 如果使用 NextCloud 源，需要有 NextCloud 服务器访问权限

### 插件安装

使用管理员账号向机器人发送命令：

```
!plugin get https://github.com/Hanschase/GiveMeSetuPlugin
```

### 依赖安装

插件会自动安装以下依赖：
```
httpx>=0.24.0
aiofiles>=23.0.0
aiohttp>=3.8.0
webdav4>=0.9.0
```

## 配置

### 基础配置

编辑 `plugins/GiveMeSetuPlugin/config.py` 文件：

#### NextCloud 配置（如果使用）
```python
# NextCloud 服务器地址
NEXTCLOUD_URL = "https://your-nextcloud-domain.com"

# NextCloud 用户名
NEXTCLOUD_USERNAME = "your_username"

# NextCloud 应用专用密码（推荐使用应用密码）
NEXTCLOUD_PASSWORD = "your_app_password"

# NextCloud 图片文件夹路径
NEXTCLOUD_FOLDER = "/Pictures/Setu"
```

#### QQ 平台配置（如果使用）
```python
# NapCat 服务器配置
NAPCAT_HOST = "127.0.0.1"
NAPCAT_PORT = 3000

# BOT 信息（用于卡片消息显示）
BOT_QQ = "your_bot_qq_number"
FORWARD_USER_ID = "sender_qq_number"
BOT_NICKNAME = "BOT"
```

### 高级配置

```python
# 默认图片源 (auto, lolicon, cloud)
DEFAULT_SOURCE = "auto"

# 自动模式下的源选择策略
AUTO_SOURCE_PRIORITY = ["lolicon", "cloud"]

# 错误重试次数
MAX_RETRY_COUNT = 3

# R18 内容开关 (0: 关闭, 1: 开启, 2: 随机)
DEFAULT_R18_FLAG = 0
```

## 使用方法

### 命令格式

```
色图|涩图 [-s [lolicon|cloud]] [tag,...]
```

### 参数说明

- **关键词**：`色图` 或 `涩图`（必须在消息开头）
- **`-s lolicon`**：从 Lolicon API 获取图片（默认）
- **`-s cloud`**：从 NextCloud 随机获取图片
- **`tag`**：图片标签（仅对 lolicon 有效，cloud 模式下忽略 tag）

### 使用示例

```
涩图                      # 从默认源随机获取图片
涩图 莉音                 # 从 Lolicon API 获取标签为"莉音"的图片
涩图 -s lolicon 莉音      # 明确指定从 Lolicon API 获取
涩图 -s cloud             # 从 NextCloud 随机获取图片
涩图 -s cloud 莉音        # 从 NextCloud 获取（忽略 tag）
```

## 平台特性

### QQ 平台
- **发送方式**：卡片模式
- **显示内容**：图片作者、标题、标签等详细信息
- **特殊要求**：需要配置 NapCat HTTP 服务器

![QQ 卡片效果](https://github.com/user-attachments/assets/6952b2e1-c022-4ce0-9eaa-d1a1604cfe9c)

### Discord 平台
- **发送方式**：直接发送图片文件
- **显示内容**：简化的文本信息 + 图片附件
- **特殊要求**：Bot 需要有发送消息和附件的权限

### 其他平台
- **发送方式**：纯文本模式
- **自动适配**：插件会自动检测平台类型并选择合适的发送方式

## 图片源说明

### Lolicon API
- **特点**：支持标签搜索，图片质量高
- **优势**：标签丰富，搜索精确
- **限制**：依赖网络连接，可能有频率限制

### NextCloud
- **特点**：从个人云盘随机获取
- **优势**：完全可控，无网络依赖
- **限制**：需要自建 NextCloud 服务器，不支持标签搜索

### 自动模式
- **工作原理**：按优先级顺序尝试不同源
- **默认策略**：先尝试 Lolicon，失败后尝试 NextCloud
- **可配置**：可在配置文件中自定义优先级

## 故障排除

### 常见问题

#### 1. 插件无响应
- 检查关键词是否正确（必须是 `色图` 或 `涩图` 开头）
- 查看 LangBot 日志获取详细错误信息
- 确认插件已正确加载

#### 2. QQ 平台图片无法发送
- 确认 NapCat HTTP 服务器已启动
- 检查 NAPCAT_HOST 和 NAPCAT_PORT 配置
- 验证端口是否被占用

![NapCat 配置示例](https://github.com/user-attachments/assets/0a5e68b4-ec3e-416c-96e9-da5f2a94b007)

#### 3. NextCloud 连接失败
- 检查 NEXTCLOUD_URL 是否正确
- 确认用户名和密码正确
- 建议使用应用专用密码而非账户密码
- 检查文件夹路径是否存在

#### 4. Discord 平台无响应
- 确认 Bot 具有发送消息和附件的权限
- 检查频道权限设置
- 查看控制台日志获取详细错误

### 调试模式

启用详细日志：
```python
ENABLE_DEBUG_LOG = True
```

## 安全建议

### NextCloud 安全
- 使用应用专用密码而非账户密码
- 定期轮换密码和访问令牌
- 限制应用权限范围

### 配置安全
- 敏感配置信息建议使用环境变量
- 定期检查配置文件权限
- 避免在公共代码仓库中提交敏感信息

## 开发信息

### 项目结构
```
GiveMeSetuPlugin/
├── main.py              # 主插件文件
├── message_parser.py    # 消息解析模块
├── get_image.py         # Lolicon API 图片获取
├── nextcloud_client.py  # NextCloud 客户端
├── platform_sender.py  # 平台适配发送模块
├── forward_message.py   # QQ 卡片消息发送
├── config.py           # 配置管理
└── requirements.txt     # 依赖包
```

### 贡献
欢迎提交 Issue 和 Pull Request 来改进插件功能。

## 更新日志

### v0.2
- ✅ 添加 NextCloud 支持
- ✅ 多平台适配（QQ 卡片模式 + Discord 直接发送）
- ✅ 改进消息解析逻辑
- ✅ 模块化重构
- ✅ 统一配置管理
- ✅ 完善错误处理和重试机制
- ✅ 支持自动源切换

### v0.1
- 🎉 初始版本发布 by Hanschase
- ✅ 基础 Lolicon API 支持
- ✅ QQ 平台卡片消息发送

## 许可证

请参考项目 LICENSE 文件。
