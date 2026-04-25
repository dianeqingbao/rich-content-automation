import discord
import os
from dotenv import load_dotenv
from screenshot_engine import generate_screenshot

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ 机器人 {client.user} 已上线，准备开始生成图片！')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("生成 "):
        content_to_capture = message.content.replace("生成 ", "").strip()
        
        if not content_to_capture:
            await message.channel.send("请输入要生成的内容，例如：生成 今天的财富密码是...")
            return

        print(f"🚀 正在为内容生成图片: {content_to_capture}")
        
        output_file = "card_output.png"
        try:
            await generate_screenshot(content_to_capture, output_file)
            
            with open(output_file, "rb") as f:
                picture = discord.File(f)
                await message.channel.send(content="✅ 视觉卡片渲染完成：", file=picture)
        except Exception as e:
            await message.channel.send(f"❌ 图片生成失败：{str(e)}")
            print(f"❌ 生成失败详情: {e}")

if __name__ == "__main__":
    client.run(TOKEN)