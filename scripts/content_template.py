# -*- coding: utf-8 -*-
"""MẪU content.py – sao chép file này rồi viết nội dung bài giảng.
Toàn bộ đơn vị tọa độ là inch, slide 16:9 = 13.333 x 7.5 in.
Chữ thường viết bình thường; công thức đặt trong $...$ (cú pháp LaTeX rút gọn, xem references/latex_subset.md).
"""
import math as _m
from engine import *          # Slide, P, T, M, TX, L, D, H, rich, set_body, màu: BG CARD BORDER YEL CYAN WHITE MINT ORANGE PINK

# ---------------------------------------------------------------- lưới bố cục chuẩn
LX, RIGHT = 0.6, 12.733          # lề trái / mép phải (có khung viền bảng: dùng 0.75 / 12.58)
GAP = 0.3
CW = (RIGHT - LX - GAP) / 2      # 2 thẻ bằng nhau
RX = LX + CW + GAP
WIDE = 7.15                      # thẻ lời giải rộng + thẻ hình hẹp
CY, CH = 1.95, 5.0               # đỉnh / chiều cao vùng thẻ (header chiếm 0.5 → 1.9)

slides = []


def new(body=18):
    """Tạo slide mới; body = cỡ chữ mặc định (16–20) cho TX/L/D trên slide này."""
    set_body(body)
    s = Slide(len(slides) + 1)
    slides.append(s)
    return s


def header(s, section, title, subtitle=None):
    """Nhãn phần (cyan) + tiêu đề (vàng) + phụ đề (có thể chứa $công thức$)."""
    paras = [P([T(section, b=True, color=CYAN)], sz=14, after=2),
             P(rich(title, color=YEL), sz=28, after=2)]
    for r in paras[1].runs:
        if isinstance(r, T):
            r.b = True
    if subtitle:
        paras.append(P(rich(subtitle, color=MINT), sz=16, after=0))
    s.text(LX, 0.45, RIGHT - LX, 1.47, paras, name='Header')


def HR(text, color=YEL, sz=18):
    """Tiêu đề thẻ cho phép chứa công thức, vd HR('a) TÍNH $\\lim{u_n}$')."""
    runs = rich(text, color=color)
    for r in runs:
        if isinstance(r, T):
            r.b = True
    return P(runs, align='ctr', sz=sz, after=6)


# ================================================================ 1. TIÊU ĐỀ
s = new()
s.card(0.9, 1.1, 11.5, 5.2, [], adj=7000, lw=2.25)
s.text(1.4, 1.5, 6.8, 4.4, [
    P([T('TOÁN 11 – KẾT NỐI TRI THỨC VỚI CUỘC SỐNG', b=True, color=CYAN)], sz=17, after=14),
    P([T('TÊN BÀI HỌC', b=True, color=YEL)], sz=40, after=8),
    P([T('Tiết …', i=True, color=WHITE)], sz=22, after=0),
], anchor='ctr', name='Title')
# hình trang trí bằng shape gốc (chỉnh sửa được)
s.poly([(8.8, 5.5), (8.8, 2.0), (11.6, 5.5)], color=CYAN, w=2, name='Triangle')

# ================================================================ 2. KIẾN THỨC (2 thẻ)
s = new(18)
header(s, 'PHẦN 1: KIẾN THỨC TRỌNG TÂM', 'CẤP SỐ NHÂN LÙI VÔ HẠN', 'Khái niệm và công thức')
s.card(LX, CY, CW, CH, [
    H('KHÁI NIỆM'),
    L('Định nghĩa:', 'cấp số nhân vô hạn $(u_n)$ có công bội $q$ với $\\left|q\\right|<1$.', after=10),
    L('Công thức:', '', after=4),
    D('S=\\frac{u_1}{1-q}\\quad\\left(\\left|q\\right|<1\\right)', color=YEL, sz=20),
])
s.card(RX, CY, CW, CH, [
    HR('VÍ DỤ: $q=\\frac{1}{2}$'),
    TX('$\\frac{1}{2}+\\frac{1}{4}+\\frac{1}{8}+\\dots=\\frac{\\frac{1}{2}}{1-\\frac{1}{2}}=1$.', align='ctr'),
], line=ORANGE)

# ================================================================ 3. LỜI GIẢI + HÌNH (thẻ rộng + thẻ hình)
s = new(18)
header(s, 'PHẦN 2: LUYỆN TẬP', 'VÍ DỤ: TAM GIÁC VUÔNG', 'Hình vẽ dựng bằng tọa độ tính toán, khớp số liệu lời giải')
s.card(LX, CY, WIDE, CH, [
    H('LỜI GIẢI'),
    TX('Tam giác $ABC$ vuông tại $A$, $AB=3$, $AC=4$ nên', after=4),
    D('BC=\\sqrt{AB^2+AC^2}=\\sqrt{9+16}=5', color=YEL),
    TX('Đơn vị đặt NGOÀI công thức: $BC=5$ (cm).', align='ctr'),
])
fx = LX + WIDE + GAP; fw = RIGHT - fx
s.card(fx, CY, fw, CH, [H('HÌNH MINH HỌA')])
sc = 0.8
A = (fx + 0.8, 6.3); B = (A[0], A[1] - 3 * sc); C = (A[0] + 4 * sc, A[1])
s.poly([A, B, C], color=WHITE, w=1.75, name='Triangle')
s.poly([(A[0], A[1] - 0.18), (A[0] + 0.18, A[1] - 0.18), (A[0] + 0.18, A[1])], color=WHITE, w=1, closed=False, name='RightMark')
for p, n, dx, dy in [(A, 'A', -0.2, 0.12), (B, 'B', -0.2, -0.1), (C, 'C', 0.2, 0.12)]:
    s.label(p[0] + dx, p[1] + dy, n, sz=16)               # nhãn điểm: chữ nghiêng
s.label((A[0] + C[0]) / 2, A[1] + 0.25, '4', sz=14, italic=False)
s.label(A[0] - 0.25, (A[1] + B[1]) / 2, '3', sz=14, italic=False)

# ================================================================ 4. BẢNG SỐ LIỆU (bảng gốc chỉnh sửa được)
s = new(18)
header(s, 'PHẦN 2: LUYỆN TẬP', 'BẢNG GIÁ TRỊ', 'Ô bảng chỉ chứa chữ/số; nhãn có công thức đặt bằng shape cạnh bảng')
rows = [['1', '2', '3', '4'], ['1', '4', '9', '16']]
tx0, ty0, rh = 3.5, 3.0, 0.5
s.table(tx0, ty0, [1.2] * 4, rows, rowh=rh, sz=18)
for k, lab in enumerate(['n', 'n^2']):
    s.shape(tx0 - 1.2, ty0 + k * rh, 1.2, rh, [P(rich('$' + lab + '$', color=YEL if k == 0 else WHITE), align='ctr', sz=18, after=0)],
            fill=CARD, line=BORDER, lw=1, anchor='ctr', name='RowLabel', txbox=False, ins=(0.03, 0.02, 0.03, 0.02))
