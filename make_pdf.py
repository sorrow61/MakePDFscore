import os
import re
from PIL import Image, ImageDraw, ImageFont

def create_sheet_music_pdf():
    # 1. 설정
    a4_width, a4_height = 595, 842  # A4 사이즈 (72 DPI 기준)
    output_filename = '악보모음집.pdf'
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # [수정] 굵은 폰트(malgunbd.ttf) 경로와 크기(50) 설정
    font_path_bold = "C:/Windows/Fonts/malgunbd.ttf"
    try:
        font = ImageFont.truetype(font_path_bold, 50) 
    except:
        # 굵은 폰트가 없을 경우 일반 폰트로 시도
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 50)
        except:
            font = ImageFont.load_default()

    # 2. 파일 정렬 함수
    def extract_number(filename):
        match = re.search(r'^(\d+)', filename)
        return int(match.group(1)) if match else 9999

    pdf_pages = []

    # 3. '설교전' -> '설교후' 순서대로 폴더 처리
    folders = ['설교전', '설교후']
    
    for folder_name in folders:
        if not os.path.exists(folder_name):
            print(f"'{folder_name}' 폴더가 없습니다. 건너뜁니다.")
            continue

        files = [f for f in os.listdir(folder_name) if f.lower().endswith(valid_extensions)]
        files.sort(key=extract_number)

        for index, file in enumerate(files):
            img_path = os.path.join(folder_name, file)
            with Image.open(img_path) as img:
                img = img.convert('RGB')
                
                is_first_after_sermon = (folder_name == '설교후' and index == 0)
                
                canvas = Image.new('RGB', (a4_width, a4_height), (255, 255, 255))
                draw = ImageDraw.Draw(canvas)
                
                available_height = a4_height
                y_offset_start = 0
                
                if is_first_after_sermon:
                    text = "설교 후 찬양"
                    # 텍스트 중앙 정렬을 위한 좌표 계산
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    
                    # [수정] 텍스트 위치(y=40) 및 색상(fill=(0, 0, 255) - 파란색) 설정
                    draw.text(((a4_width - text_width) // 2, 40), text, font=font, fill=(0, 0, 255))
                    
                    # 텍스트 공간 확보를 위해 이미지 시작점과 가용 높이 조정
                    y_offset_start = 120 
                    available_height = a4_height - 150
                
                # 이미지 리사이징
                img_width, img_height = img.size
                ratio = min(a4_width / img_width, available_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 이미지 중앙 배치
                x_pos = (a4_width - new_width) // 2
                y_pos = y_offset_start + (available_height - new_height) // 2
                
                canvas.paste(resized_img, (x_pos, y_pos))
                pdf_pages.append(canvas)

    # 4. PDF 저장
    if pdf_pages:
        pdf_pages[0].save(
            output_filename, 
            save_all=True, 
            append_images=pdf_pages[1:], 
            resolution=100.0, 
            quality=95
        )
        print(f"\n성공! 파란색 강조 문구가 포함된 '{output_filename}' 파일이 생성되었습니다.")
    else:
        print("\n이미지를 하나도 찾지 못했습니다.")

if __name__ == "__main__":
    create_sheet_music_pdf()