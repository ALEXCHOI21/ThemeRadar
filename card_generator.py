import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def get_hangul_font(size=20):
    """
    Search for a valid Korean TrueType font to prevent character breakages.
    Downloads NanumGothic from Google Fonts on serverless environments (/tmp).
    """
    # 1. Serverless dynamic font downloader
    tmp_font_path = "/tmp/NanumGothic-Bold.ttf"
    if not os.path.exists(tmp_font_path):
        try:
            import requests
            print("[Font Loader] NanumGothic-Bold.ttf is missing in /tmp. Downloading...")
            r = requests.get("https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Bold.ttf", timeout=15)
            if r.status_code == 200:
                # Ensure /tmp exists (always does in Unix-like envs)
                with open(tmp_font_path, "wb") as f:
                    f.write(r.content)
                print("[Font Loader] Download completed successfully.")
        except Exception as e:
            print(f"[Font Loader] Warning: Failed to download font: {e}")
            
    # Candidate font paths (Windows, Linux, macOS)
    font_paths = [
        tmp_font_path,                         # Vercel Fallback first
        r"C:\Windows\Fonts\malgunbd.ttf",      # Windows 맑은고딕 Bold
        r"C:\Windows\Fonts\malgun.ttf",        # Windows 맑은고딕
        r"C:\Windows\Fonts\nanum\NanumBarunGothic.ttf", # Linux Nanum
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf", # Ubuntu Nanum
        "/System/Library/Fonts/Supplemental/AppleGothic.ttf",  # macOS AppleGothic
        "malgun.ttf"                           # Local fallback
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
                
    # Ultimate safe fallback
    return ImageFont.load_default()

def wrap_text(text, font, max_width, draw):
    """
    Helper to wrap text nicely to fit inside the specified width.
    """
    lines = []
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para.strip():
            lines.append("")
            continue
        words = para.split(" ")
        current_line = []
        for word in words:
            test_line = " ".join(current_line + [word])
            # Calculate width of the test line
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
    return lines

def generate_market_briefing_card(title: str, content: str, filepath: str = "daily_briefing_card.png") -> str:
    """
    Renders a stunning dark-theme glassmorphic card news image (1080x1080).
    """
    # 1. Base Gradient Canvas (1080x1080)
    width, height = 1080, 1080
    base_img = Image.new("RGBA", (width, height))
    
    # Draw soft navy-to-slate gradient background
    draw = ImageDraw.Draw(base_img)
    for y in range(height):
        # Linear interpolation from deep dark navy (#0B0F19) to slate navy (#1E293B)
        r = int(0x0B + (0x1E - 0x0B) * (y / height))
        g = int(0x0F + (0x29 - 0x0F) * (y / height))
        b = int(0x19 + (0x3B - 0x19) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # 2. Semi-transparent Glassmorphism overlay
    # We create a separate overlay to support alpha channel drawing
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ol_draw = ImageDraw.Draw(overlay)
    
    # Large Glass Panel (Main content background)
    panel_left = 60
    panel_top = 180
    panel_right = 1020
    panel_bottom = 980
    
    # Round rectangle glass panel (Dark semi-transparent filled)
    ol_draw.rounded_rectangle(
        [panel_left, panel_top, panel_right, panel_bottom],
        radius=24,
        fill=(255, 255, 255, 12),  # 5% Alpha white fill
        outline=(255, 255, 255, 45), # 18% Alpha border
        width=2
    )
    
    # Highlight sub-header tag glass box
    ol_draw.rounded_rectangle(
        [panel_left + 40, panel_top + 40, panel_left + 260, panel_top + 90],
        radius=8,
        fill=(0, 122, 255, 30), # Soft Blue tint glass
        outline=(0, 122, 255, 120),
        width=1
    )
    
    # Composite the glass card back onto the background
    final_img = Image.alpha_composite(base_img, overlay)
    draw = ImageDraw.Draw(final_img)
    
    # 3. Typography & Data Rendering
    title_font = get_hangul_font(38)
    body_font = get_hangul_font(26)
    tag_font = get_hangul_font(20)
    footer_font = get_hangul_font(18)
    
    # Format with current Korean local timezone format (Hour and Minute included)
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Draw Brand Logo & Header
    draw.text((60, 60), "🔮 ChoiGPT Corp. 수석 전략가 리포트", fill="#007aff", font=get_hangul_font(28))
    draw.text((60, 110), f"ThemeRadar Market Intelligence | 조사 시점: {today_str}", fill="#8e8e93", font=get_hangul_font(18))
    
    # Draw tag text inside blue glass box
    draw.text((panel_left + 65, panel_top + 50), "FACT VERIFIED 100%", fill="#30d158", font=tag_font)
    
    # Draw main title (auto wrapped to prevent clipping)
    title_lines = wrap_text(title, title_font, (panel_right - panel_left) - 100, draw)
    y_cursor = panel_top + 130
    for t_line in title_lines:
        draw.text((panel_left + 40, y_cursor), t_line, fill="#ffffff", font=title_font)
        y_cursor += 55
        
    # Draw simple divider line
    y_cursor += 15
    draw.line([(panel_left + 40, y_cursor), (panel_right - 40, y_cursor)], fill=(255, 255, 255, 30), width=1)
    y_cursor += 30
    
    # Draw briefing content body (auto wrapped)
    content_lines = wrap_text(content, body_font, (panel_right - panel_left) - 80, draw)
    for c_line in content_lines:
        if y_cursor > panel_bottom - 60:
            break # Avoid overflowing below the card boundary
        
        # Color specific highlighters (e.g. KOSPI, KOSDAQ, 외국인)
        color = "#e5e5ea"
        if "KOSPI" in c_line or "코스피" in c_line:
            color = "#007aff"
        elif "KOSDAQ" in c_line or "코스닥" in c_line:
            color = "#34c759"
            
        draw.text((panel_left + 40, y_cursor), c_line, fill=color, font=body_font)
        y_cursor += 42
        
    # Draw Premium Footer Branding
    draw.text((panel_left + 40, panel_bottom - 45), "※ 본 카드는 ChoiGPT 실시간 자금흐름 AI 스캐너에 의해 100% 자동 생성되었습니다.", fill="#8e8e93", font=footer_font)
    
    # Save Image to disk (supporting PNG)
    final_img.convert("RGB").save(filepath, "PNG")
    print(f"[Card Generator] Successfully saved briefing card to {filepath}")
    return filepath

if __name__ == "__main__":
    # Test generation run
    test_title = "[초격차 마켓] 장중 사상 최초 KOSPI 8,900선 돌파 후 차익실현 급변 장세"
    test_content = (
        "1. KOSPI 지수 흐름: 장중 8,933.62 고점 터치 후 급격한 되돌림 현상 출회 중.\n"
        "2. 외인 역대급 매도세: 장중 1.5조원 이상 폭풍 매도 출회로 상승분 대부분 반납.\n"
        "3. 코스닥 시장 약세: 양대 지수 동반 조정 국면 속에 외국인/기관 수급은 분산.\n"
        "4. 환율 리스크 부각: 원/달러 환율 1,512원대 유지로 외국인 매도 기조 자극.\n"
        "5. 대응 권고: 현 구간 무리한 고점 매수 극도로 제한. SMR/방산 중심 포트 재편 권장."
    )
    generate_market_briefing_card(test_title, test_content, "test_briefing_card.png")
