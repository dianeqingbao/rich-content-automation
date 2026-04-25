# 文件名: screenshot_engine.py
import os
from PIL import Image, ImageDraw, ImageFont

async def generate_screenshot(content_to_capture, output_file):
    try:
        # 1. 基础配置
        bg_path = "变富短图文背景.png"
        font_path = "font.otf" 
        bg = Image.open(bg_path).convert("RGBA")
        draw = ImageDraw.Draw(bg)

        # 2. 核心排版参数 (经过 500 字容纳度优化)
        font_size = 38         
        line_height = 58       
        margin_left = 70       
        margin_center = 60     
        y_start = 320          
        
        column_width = (bg.width - 2 * margin_left - margin_center) // 2 
        max_lines_per_column = (bg.height - y_start - 100) // line_height

        font = ImageFont.truetype(font_path, font_size)

        # 3. 增强版换行算法：处理段落与自动换行
        all_lines = []
        # 先按照用户输入的原始换行符分段
        paragraphs = content_to_capture.splitlines() 
        
        for para in paragraphs:
            if not para: # 处理空行
                all_lines.append("")
                continue
                
            current_line = ""
            for char in para:
                test_line = current_line + char
                w = draw.textbbox((0, 0), test_line, font=font)[2]
                if w <= column_width:
                    current_line = test_line
                else:
                    all_lines.append(current_line)
                    current_line = char
            all_lines.append(current_line) # 添加段落最后一行

        # 4. 双栏绘制逻辑
        text_color = (60, 40, 30) 
        
        for i, line in enumerate(all_lines):
            # 计算当前行在第几栏
            column_index = i // max_lines_per_column
            line_index_in_column = i % max_lines_per_column
            
            if column_index == 0:
                # 【左栏】
                x_pos = margin_left
            elif column_index == 1:
                # 【右栏】
                x_pos = margin_left + column_width + margin_center
            else:
                # 超出两栏范围，打断并添加省略号
                last_y = y_start + (max_lines_per_column - 1) * line_height
                draw.text((margin_left + column_width + margin_center, last_y), "...", fill=text_color, font=font)
                break
                
            y_pos = y_start + (line_index_in_column * line_height)
            
            if line: # 只有非空行才绘制，避免空行报错
                draw.text((x_pos, y_pos), line, fill=text_color, font=font)

        # 5. 保存成品
        final_img = bg.convert("RGB")
        final_img.save(output_file, "PNG")
        print(f"✅ 修正版双栏排版生成成功: {output_file}")
        
    except Exception as e:
        print(f"❌ 渲染引擎报错: {e}")
        raise e