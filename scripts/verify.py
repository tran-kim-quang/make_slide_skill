# -*- coding: utf-8 -*-
"""Kiểm tra tự động file PPTX bài giảng toán trước khi bàn giao.
Usage: python verify.py bai_giang.pptx [--expect-slides 20]
Kiểm tra: số slide, font, số công thức OMML, ảnh chỉ nằm trong Fallback, kí tự toán giả lập
trong chữ hiển thị, giá trị on/off của OMML, công thức display bắt đầu bằng '=', số mũ đặt
sai trên chữ số cuối, kí hiệu độ bị đẩy thành số mũ."""
import re, sys, zipfile, argparse

PSEUDO = set('²³¹⁰⁴⁵⁶⁷⁸⁹ⁿ₀₁₂₃₄√∛✓✗⇒⇔①②③④')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('--expect-slides', type=int, default=None)
    a = ap.parse_args()
    z = zipfile.ZipFile(a.pptx)
    names = z.namelist()
    slides = sorted([n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)],
                    key=lambda n: int(re.findall(r'\d+', n)[-1]))
    problems = []
    fonts = set(); omml = 0
    for n in slides:
        raw = z.read(n).decode('utf-8')
        idx = re.findall(r'\d+', n)[-1]
        fonts |= set(re.findall(r'<a:latin typeface="([^"]+)"', raw))
        omml += raw.count('<m:oMath>')
        choice = ''.join(re.findall(r'<mc:Choice.*?</mc:Choice>', raw, re.S))
        visible = re.sub(r'<mc:Fallback>.*?</mc:Fallback>', '', raw, flags=re.S)
        txt = ' '.join(re.findall(r'<a:t>([^<]*)</a:t>', visible))
        bad = sorted(set(c for c in txt if c in PSEUDO))
        if bad:
            problems.append(f'slide {idx}: kí tự toán giả lập trong chữ thường: {"".join(bad)} -> chuyển sang $...$')
        if re.search(r'<p:pic>', visible):
            problems.append(f'slide {idx}: có ảnh nằm ngoài Fallback (không được dùng ảnh thay nội dung)')
        if re.search(r'Hide m:val="(1|true|0|false)"', choice):
            problems.append(f'slide {idx}: OMML dùng m:val="1"/"0" -> PowerPoint cần "on"/"off" (dấu căn hiện ô bậc trống)')
        for para in re.findall(r'<m:oMathPara>.*?</m:oMathPara>', choice, re.S):
            first = re.search(r'<m:t>([^<]*)</m:t>', para)
            if first and first.group(1).startswith('='):
                problems.append(f'slide {idx}: công thức display bắt đầu bằng "=" (bản dự phòng hiện sai) -> viết lại vế trái')
        if re.search(r'<m:t>[^<]*\d</m:t></m:r><m:sSup>(?:(?!</m:sSup>).)*?<m:e>(?:(?!</m:e>).)*?<m:t>\d+</m:t>', choice, re.S):
            problems.append(f'slide {idx}: số mũ có thể chỉ gắn vào chữ số cuối (vd 100^2 thành 10·0²)')
        if '<m:t>°</m:t></m:r></m:sup>' in choice:
            problems.append(f'slide {idx}: kí hiệu độ bị đặt làm số mũ -> viết 60° liền')
    extra_fonts = fonts - {'Times New Roman', 'Cambria Math'}
    if extra_fonts:
        problems.append(f'font ngoài chuẩn: {extra_fonts}')
    if a.expect_slides and len(slides) != a.expect_slides:
        problems.append(f'số slide = {len(slides)}, yêu cầu {a.expect_slides}')
    media = [n for n in names if n.startswith('ppt/media/')]
    print(f'Slides: {len(slides)} | công thức OMML: {omml} | font: {sorted(fonts)} | ảnh (chỉ dùng làm Fallback): {len(media)}')
    if problems:
        print('VẤN ĐỀ:')
        for p in problems:
            print(' -', p)
        sys.exit(1)
    print('OK – không phát hiện lỗi.')


if __name__ == '__main__':
    main()
