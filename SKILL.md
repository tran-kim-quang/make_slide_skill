---
name: thiet-ke-slide-toan
description: Biên soạn lại và thiết kế bài giảng Toán (PowerPoint .pptx) từ file gốc – rà soát lỗi kiến thức/phép tính, phái sinh bài tập mới, viết 100% công thức bằng Office Math (OMML) chỉnh sửa được, giữ nền/bố cục bảng xanh, thêm hình vẽ, đồ thị, bảng bằng shape gốc, kiểm tra render trước khi bàn giao. Dùng skill này BẤT CỨ KHI NÀO người dùng gửi file PPTX bài giảng toán (giới hạn, dãy số, vectơ, tọa độ Oxyz, thống kê, hình học, đạo hàm, tích phân…) và yêu cầu sửa, biên soạn lại, thiết kế lại, làm đẹp, chuẩn hóa công thức, "làm cái này", "tiếp tục", hoặc phàn nàn kí hiệu căn/số mũ/công thức hiển thị sai – kể cả khi không nói rõ chữ "skill" hay "OMML". Also use for any request to build or fix math lecture slides in Vietnamese with editable equations.
---

# Thiết kế slide bài giảng Toán

Skill này đóng gói quy trình đã dùng thực tế để biên soạn lại các bộ slide toán THPT, gồm Toán 11 (Giới hạn dãy số) và Toán 12 (Vectơ, Oxyz, Thống kê). Người dùng là giáo viên Việt Nam. Thứ tự ưu tiên của họ là: **chính xác toán học > chỉnh sửa được > đầy đủ nội dung > thẩm mỹ**.

Trước khi bắt đầu, đọc `/mnt/skills/public/pptx/SKILL.md`. Skill này dùng `clean.py`, `validate.py`, `thumbnail.py` và `office/soffice.py` của skill pptx.

## Bộ công cụ (thư mục `scripts/`)

| File | Vai trò |
|---|---|
| `mathdsl.py` | Chuyển công thức LaTeX rút gọn thành OMML (cho PowerPoint) và OMML (cho DOCX kiểm tra) |
| `engine.py` | API dựng slide: `Slide`, thẻ (`card`), hộp chữ, đường, mũi tên, đa giác, cung, điểm, nhãn, bảng, hình chữ nhật; đoạn văn `TX/L/D/H` |
| `build.py` | Đóng gói: dùng file gốc làm template, render kiểm tra, xuất PPTX cuối (OMML + ảnh dự phòng) |
| `verify.py` | Kiểm tra tự động trước bàn giao |
| `content_template.py` | Mẫu `content.py`: tiêu đề, 2 thẻ, thẻ lời giải + hình, bảng |

Tài liệu tham khảo (đọc khi cần):
- `references/latex_subset.md`: cú pháp công thức được hỗ trợ và các lỗi hay viết sai. **Đọc trước khi viết content.**
- `references/ra_soat_noi_dung.md`: checklist rà soát kiến thức, quy ước kí hiệu SGK, cách phái sinh bài tập, số lượng slide.
- `references/pitfalls.md`: bài học kĩ thuật (dấu căn, số mũ, bản dự phòng, LibreOffice…). Đọc khi gặp lỗi hiển thị.

## Quy trình

### Bước 0: Chuẩn bị môi trường

```bash
S=/mnt/skills/user/thiet-ke-slide-toan/scripts      # hoặc nơi skill được cài
WORK=/home/claude/work && mkdir -p $WORK && cp $S/*.py $WORK/
dpkg -l | grep -q libreoffice-math || apt-get install -y libreoffice-math   # BẮT BUỘC để vẽ OMML khi kiểm tra
```

### Bước 1: Đọc file gốc

```bash
cd $WORK && cp /mnt/user-data/uploads/<file>.pptx goc.pptx
markitdown goc.pptx > goc.md                                    # toàn bộ chữ
python /mnt/skills/public/pptx/scripts/thumbnail.py goc.pptx thumb   # nhìn bố cục
mkdir g && cd g && unzip -q ../goc.pptx && cd ..
```

Cần xác định:
- **Nền:** màu `p:bg` của slide, hoặc shape phủ toàn slide và khung viền. Ghi lại mã màu để dùng cho `--bg` và `--frame`.
- **Bảng màu của "slide mẫu"** mà người dùng chỉ định (vd "theo slide 9"): màu thẻ, màu viền, màu tiêu đề, màu nhãn. Lấy bằng `grep -o 'srgbClr val="[^"]*"' g/ppt/slides/slide9.xml | sort | uniq -c`.
- Số slide, kích thước slide, cấu trúc nội dung (mục tiêu, lí thuyết, ví dụ, luyện tập, vận dụng, tổng kết).

### Bước 2: Rà soát nội dung

Làm theo `references/ra_soat_noi_dung.md`:
- **Tính lại mọi phép tính bằng Python.** File gốc rất hay sai số liệu.
- Kiểm tra lập luận, quy tắc có trong sách hay không, kiến thức có đúng chương trình và đúng thời điểm học không.
- Kiểm tra số chương/bài, chính tả, trích dẫn.
- Ghi danh sách lỗi để báo cáo.

### Bước 3: Lập dàn ý và phái sinh bài tập

- Giữ mạch bài của file gốc. **Số slide:** giữ đúng số slide gốc, hoặc theo yêu cầu "tối đa N". Không tự ý rút gọn nhiều khi người dùng cần "đủ" slide.
- Thay toàn bộ ví dụ và bài tập bằng đề mới cùng dạng, cùng độ khó. Mỗi đáp số kiểm tra bằng hai cách.
- Viết dàn ý: slide → tiêu đề → các thẻ → hình minh họa cần có.

### Bước 4: Viết `content.py`

Sao chép `content_template.py` và viết từng slide. Các quy tắc chính:

**Công thức**
- Mọi kí hiệu toán (biến, chỉ số, số mũ, phân số, căn, vectơ, ∞, ⇒…) phải nằm trong `$...$` hoặc `D()`.
- Không gõ ², ⁿ, √, ⇒ bằng kí tự Unicode trong chữ thường.

**Bố cục chuẩn (16:9)**
- Header gồm nhãn phần (14pt, cyan), tiêu đề (28pt đậm, vàng) và phụ đề (16pt). Header nằm trong khoảng y 0,45–1,9 in.
- Vùng thẻ bắt đầu từ `CY≈1,95`, cao `CH≈5,0`. Có hai kiểu:
  - hai thẻ bằng nhau (`LX/RX/CW`);
  - một thẻ lời giải rộng (`WIDE=7,15`) cộng một thẻ hình.
- Nếu có khung viền bảng ở mép 0,4 in: lề trái 0,75, mép phải 12,58, `CY≥2,05`.
- Thẻ là `roundRect` với màu nền thẻ và viền lấy theo file gốc. Tiêu đề thẻ 18pt đậm, vàng, căn giữa. Nhãn đậm màu cyan, nội dung màu trắng.
- Cỡ chữ nội dung 16–20pt (`new(body)`). Khi thẻ còn trống nhiều, tăng cỡ chữ hoặc giãn dòng, hoặc thêm thẻ "lưu ý / kiểm tra". Không để một nửa slide trống.

**Màu sắc**
- Lấy từ file gốc và truyền qua `--palette`.
- Dùng màu nhất quán: vàng cho kết quả và kết luận, cyan cho nhãn, cam/hồng cho cảnh báo hoặc thẻ thứ hai.

**Font**
- Chữ dùng Times New Roman (engine tự đặt), công thức dùng Cambria Math.

**Hình minh họa**
- Chỉ dùng shape gốc: `line/arrow/poly/arc/dot/rect/label/table`.
- **Tính tọa độ từ số liệu thật.** Ví dụ: chân đường vuông góc tính bằng phép chiếu; cột biểu đồ cao tỉ lệ đúng với giá trị; tổng riêng đặt đúng trên trục số.
- Hình phải khớp lời giải.
- Gợi ý theo chủ đề:
  - Dãy số, giới hạn: trục số các tổng riêng, đồ thị điểm uₙ kèm đường giới hạn hoặc ±M, biểu đồ tăng trưởng.
  - Hình học không gian: hình hộp, tứ diện, chóp, dùng nét đứt cho cạnh khuất.
  - Tọa độ: hệ trục Oxyz kèm hình chiếu.
  - Thống kê: histogram, đa giác tần số tích lũy (giao với n/4, 3n/4 cho ra Q₁, Q₃).
- Nhãn điểm in nghiêng, nhãn số đứng (`italic=False`). Nhãn có công thức thì dùng `'$...$'`.

**Bảng**
- `s.table()` chỉ chứa chữ và số.
- Nhãn hàng hoặc cột có kí hiệu toán đặt bằng shape riêng sát mép bảng (xem template).

### Bước 5: Build và kiểm tra hình ảnh

```bash
python build.py --src goc.pptx --content content.py --out bai_giang.pptx --work $WORK/b \
   --bg 0E3822 [--frame 1B5E3A] --title "Tên bài" \
   --palette '{"CARD":"13462C","BORDER":"80DEEA","YEL":"FFEB3B","CYAN":"80DEEA","WHITE":"F5F5F5"}' --grid
```

- `overflow` phải rỗng. Nếu có, hộp đó tràn chữ (tên `sNN_id` cho biết số slide): rút gọn chữ, giảm `after`, hoặc nới thẻ.
- **Xem mọi ảnh `grid*.jpg`.** Đây chính là cách phần mềm không hỗ trợ OMML hiển thị file. Kiểm tra từng slide:
  - công thức đúng: căn phủ đủ, số mũ nằm trên cả số, phân số xếp dọc, 60° viết liền;
  - không chồng lấn, không chạm mép thẻ, nhãn hình không đè lên nét vẽ;
  - không còn khoảng trống lớn;
  - nội dung khớp lời giải.
- Muốn xem gần một slide: `pdftoppm -jpeg -r 110 -f N -l N $WORK/b/grid/bai_giang.pdf x`.
- Sửa `content.py` rồi build lại. Lặp đến khi sạch.

### Bước 6: Kiểm tra tự động

```bash
python /mnt/skills/public/pptx/scripts/office/validate.py bai_giang.pptx
python verify.py bai_giang.pptx --expect-slides 20
```

`verify.py` kiểm tra:
- font;
- kí tự giả lập trong chữ hiển thị;
- ảnh nằm ngoài Fallback;
- `m:val="1"` (phải là `on`);
- dòng display bắt đầu bằng `=`;
- số mũ chỉ gắn vào chữ số cuối;
- kí hiệu độ bị đẩy thành số mũ;
- số slide.

### Bước 7: Bàn giao

Chép file vào `/mnt/user-data/outputs/` và gọi `present_files`. Chỉ trình bày những file người dùng cần, không gửi kèm file cũ nếu họ đã nói "chỉ cần 2 file".

Báo cáo ngắn gọn bằng tiếng Việt, theo thứ tự:
1. Số slide, nền đã giữ.
2. **Các lỗi đã sửa trong file gốc**, cụ thể từng lỗi (sai số liệu, lập luận, kí hiệu, chương trình).
3. Bảng các bài phái sinh và đáp số.
4. Hình minh họa đã thêm.
5. Kết quả kiểm tra (validate, verify, số công thức, đã xem render bao nhiêu slide).
6. Lưu ý trung thực:
   - không có PowerPoint để mở thử, nên kích thước công thức có thể lệch nhẹ;
   - PowerPoint 2010+ chỉnh sửa được công thức;
   - phần mềm khác thấy ảnh công thức.

## Khi người dùng báo lỗi hiển thị

| Người dùng nói | Nguyên nhân thường gặp | Xử lý |
|---|---|---|
| "dấu căn sai", "không biết căn như nào" | Fallback dạng chữ `√(…)`, hoặc `degHide m:val="1"` | Fallback ảnh (`build.py` đã làm); `m:val="on"` |
| "mũ bị sai" | Số mũ gắn vào chữ số cuối; độ bị đẩy thành số mũ | Kiểm tra `mathdsl.py` có nhóm số và đổi `^\circ` |
| Ảnh chụp có công thức một dòng, nghiêng | Đang xem Fallback dạng chữ | Hỏi phần mềm đang dùng; dùng Fallback ảnh |
| "phải đủ N slide" | Đã rút gọn quá tay | Tách phân tích/lời giải, thêm lưu ý, hình, bài tự luyện (không nhồi nhét) |

Khi chưa chắc nguyên nhân, xin ảnh chụp màn hình của một slide cụ thể. Không khẳng định đã sửa xong khi chưa kiểm chứng; nói rõ phần nào đã xác minh và phần nào chưa.
