# 文件名: screenshot_engine.py
import os
from PIL import Image, ImageDraw, ImageFont

async def generate_screenshot(content_to_capture, output_prefix="card"):
    """
    支持多图生成：根据内容长度自动分页渲染
    返回生成的所有图片路径列表
    """
    generated_files = []
    try:
        # 1. 资源加载
        bg_path = "变富短图文背景.png"
        font_path = "font.otf"
        font_size = 38
        line_height = 58
        margin_left = 70
        margin_center = 60
        y_start = 320
        
        # 2. 基础计算
        bg_template = Image.open(bg_path).convert("RGBA")
        draw_temp = ImageDraw.Draw(bg_template)
        font = ImageFont.truetype(font_path, font_size)
        
        column_width = (bg_template.width - 2 * margin_left - margin_center) // 2
        max_lines_per_column = (bg_template.height - y_start - 100) // line_height
        lines_per_page = max_lines_per_column * 2 # 一张图两栏的总行数

        # 3. 将全文切分为“行列表”
        all_lines = []
        paragraphs = content_to_capture.splitlines()
        for para in paragraphs:
            if not para:
                all_lines.append("") # 保持空行
                continue
            current_line = ""
            for char in para:
                test_line = current_line + char
                w = draw_temp.textbbox((0, 0), test_line, font=font)[2]
                if w <= column_width:
                    current_line = test_line
                else:
                    all_lines.append(current_line)
                    current_line = char
            all_lines.append(current_line)

        # 4. 分页渲染逻辑
        page_num = 1
        # 只要还有没画完的行，就继续生成新图
        while all_lines:
            # 取出当前页要画的行
            current_page_lines = all_lines[:lines_per_page]
            all_lines = all_lines[lines_per_page:] # 剩下的是后面页码的
            
            # 创建新画布
            bg = bg_template.copy()
            draw = ImageDraw.Draw(bg)
            text_color = (60, 40, 30)

            for i, line in enumerate(current_page_lines):
                col_idx = i // max_lines_per_column
                row_idx = i % max_lines_per_column
                
                x_pos = margin_left if col_idx == 0 else (margin_left + column_width + margin_center)
                y_pos = y_start + (row_idx * line_height)
                
                if line:
                    draw.text((x_pos, y_pos), line, fill=text_color, font=font)

            # 保存当前页
            file_name = f"{output_prefix}_{page_num}.png"
            bg.convert("RGB").save(file_name, "PNG")
            generated_files.append(file_name)
            page_num += 1

        print(f"✅ 渲染完成，共生成 {len(generated_files)} 张图片")
        return generated_files
        
    except Exception as e:
        print(f"❌ 渲染引擎分页逻辑报错: {e}")
        raise e