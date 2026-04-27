import discord
import os
from dotenv import load_dotenv
from screenshot_engine import generate_screenshot

# 1. 加载环境变量
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. 配置机器人权限
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 3. 存储录制状态
recording_state = {
    "is_active": False,
    "content_buffer": []
}

@client.event
async def on_ready():
    print(f'✅ 机器人 {client.user} 已上线！')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global recording_state

    # --- 逻辑 A: 检测开始指令 #$ ---
    if message.content.startswith("#$ "):
        recording_state["is_active"] = True
        recording_state["content_buffer"] = []
        
        first_content = message.content.replace("#$ ", "").strip()
        if first_content:
            if "#$$" in first_content:
                text = first_content.replace("#$$", "").strip()
                if text:
                    recording_state["content_buffer"].append({"type": "text", "data": text})
            else:
                recording_state["content_buffer"].append({"type": "text", "data": first_content})
        print("🎙️ 录制开始...")
        return

    # --- 逻辑 B: 检测结束指令 #$$ ---
    if "#$$" in message.content:
        if not recording_state["is_active"]:
            return
        
        # 记录结束前的最后一段文字（如果有）
        last_text = message.content.replace("#$$", "").strip()
        if last_text:
            recording_state["content_buffer"].append({"type": "text", "data": last_text})
        
        recording_state["is_active"] = False
        mixed_data = recording_state["content_buffer"]
        
        if not mixed_data:
            await message.channel.send("⚠️ 缓冲区内容为空")
            return

        try:
            # 1. 渲染并发送报纸图片
            print("🚀 正在生成报纸图片...")
            output_files = await generate_screenshot(mixed_data, "card_output")
            for file_path in output_files:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        await message.channel.send(file=discord.File(f))
                    os.remove(file_path)

            # 2. 发送图片原件 (此处修复了文件占用问题)
            image_originals = [item["data"] for item in mixed_data if item["type"] == "image"]
            if image_originals:
                await message.channel.send("📸 --- 以下为图片原件 ---")
                for img_path in image_originals:
                    if os.path.exists(img_path):
                        with open(img_path, "rb") as f:
                            await message.channel.send(file=discord.File(f))
                        os.remove(img_path) # 确保发完后彻底清理
            
            await message.channel.send(f"✅ 全流程分发完成！")
        except Exception as e:
            await message.channel.send(f"❌ 处理出错: {e}")
        return

    # --- 逻辑 C: 录制中追加文字和图片 ---
    if recording_state["is_active"]:
        # 捕捉文字
        if message.content.strip() and not "#$$" in message.content:
            recording_state["content_buffer"].append({"type": "text", "data": message.content})

        # 捕捉图片
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(ext) for ext in ['png', 'jpg', 'jpeg', 'webp']):
                    file_path = f"temp_{attachment.filename}"
                    await attachment.save(file_path)
                    recording_state["content_buffer"].append({"type": "image", "data": file_path})
                    print(f"📸 捕获图片: {attachment.filename}")

if __name__ == "__main__":
    if TOKEN:
        client.run(TOKEN)
    else:
        print("❌ 错误: 未找到 DISCORD_TOKEN")