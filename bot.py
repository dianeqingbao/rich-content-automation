# 文件名: bot.py
import discord
import os
from dotenv import load_dotenv
from screenshot_engine import generate_screenshot # 确保导入了你的引擎

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ 机器人 {client.user} 已上线！')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("生成 "):
        content_to_capture = message.content.replace("生成 ", "").strip()
        
        if not content_to_capture:
            await message.channel.send("请输入内容哦！")
            return

        print(f"🚀 开始多页渲染: {content_to_capture[:20]}...")
        
        try:
            # --- 核心修复点：确保这行在 async def 内部，且有正确的缩进 ---
            output_files = await generate_screenshot(content_to_capture, "card_output")
            
            # 循环发送生成的图片列表 
            for file_path in output_files:
                with open(file_path, "rb") as f:
                    picture = discord.File(f)
                    await message.channel.send(file=picture)
                
                # 可选：发完后删除临时文件，节省 Codespaces 空间
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            await message.channel.send(f"✅ 已完成 {len(output_files)} 张卡片分发。")
            # -------------------------------------------------------

        except Exception as e:
            await message.channel.send(f"❌ 出错啦: {str(e)}")
            print(f"报错详情: {e}")

if __name__ == "__main__":
    client.run(TOKEN)