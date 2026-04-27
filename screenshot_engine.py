import os
from PIL import Image, ImageDraw, ImageFont

async def generate_screenshot(mixed_data, output_prefix="card"):
    generated_files = []
    try:
        # 1. 基础配置
        bg_path = "变富短图文背景.png"
        font_path = "font.otf"
        font_size = 38
        line_height = 58
        margin_left = 70
        margin_center = 60
        y_start = 320
        text_color = (60, 40, 30)
        
        bg_template = Image.open(bg_path).convert("RGBA")
        font = ImageFont.truetype(font_path, font_size)
        
        column_width = (bg_template.width - 2 * margin_left - margin_center) // 2
        max_y = bg_template.height - 100 

        pages = []
        current_bg = bg_template.copy()
        current_draw = ImageDraw.Draw(current_bg)
        curr_col, curr_y = 0, y_start

        def get_x_pos(col):
            return margin_left if col == 0 else (margin_left + column_width + margin_center)

        # 2. 核心排版循环
        for item in mixed_data:
            if item["type"] == "text":
                paragraphs = item["data"].splitlines()
                for para in paragraphs:
                    if not para:
                        curr_y += line_height / 2
                        continue
                    
                    current_line = ""
                    for char in para:
                        test_line = current_line + char
                        w = current_draw.textbbox((0, 0), test_line, font=font)[2]
                        if w <= column_width:
                            current_line = test_line
                        else:
                            # 检查是否需要切栏/切页
                            if curr_y + line_height > max_y:
                                if curr_col == 0:
                                    curr_col, curr_y = 1, y_start
                                else:
                                    pages.append(current_bg)
                                    current_bg = bg_template.copy()
                                    current_draw = ImageDraw.Draw(current_bg)
                                    curr_col, curr_y = 0, y_start
                            
                            current_draw.text((get_x_pos(curr_col), curr_y), current_line, fill=text_color, font=font)
                            curr_y += line_height
                            current_line = char
                    
                    # 绘制段落剩余行
                    if current_line:
                        if curr_y + line_height > max_y:
                            if curr_col == 0:
                                curr_col, curr_y = 1, y_start
                            else:
                                pages.append(current_bg)
                                current_bg = bg_template.copy()
                                current_draw = ImageDraw.Draw(current_bg)
                                curr_col, curr_y = 0, y_start
                        current_draw.text((get_x_pos(curr_col), curr_y), current_line, fill=text_color, font=font)
                        curr_y += line_height

            elif item["type"] == "image":
                img_path = item["data"]
                if os.path.exists(img_path):
                    with Image.open(img_path) as img:
                        w_percent = (column_width / float(img.size[0]))
                        h_size = int((float(img.size[1]) * float(w_percent)))
                        img_resized = img.resize((column_width, h_size), Image.Resampling.LANCZOS)
                        
                        if curr_y + h_size > max_y:
                            if curr_col == 0:
                                curr_col, curr_y = 1, y_start
                            else:
                                pages.append(current_bg)
                                current_bg = bg_template.copy()
                                current_draw = ImageDraw.Draw(current_bg)
                                curr_col, curr_y = 0, y_start
                        
                        current_bg.paste(img_resized, (get_x_pos(curr_col), int(curr_y)))
                        curr_y += h_size + 20 

        pages.append(current_bg)

        # 3. 保存结果
        for i, page in enumerate(pages):
            file_name = f"{output_prefix}_{i+1}.png"
            page.convert("RGB").save(file_name, "PNG")
            generated_files.append(file_name)

        return generated_files
        
    except Exception as e:
        print(f"❌ 渲染引擎报错: {e}")
        raise e