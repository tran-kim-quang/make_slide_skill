# Bài học kĩ thuật (đã trả giá bằng lỗi thật)

Đọc file này khi có lỗi hiển thị công thức, hoặc trước khi sửa `mathdsl.py`/`engine.py`.

## 1. Cấu trúc công thức trong PPTX

PowerPoint lưu công thức như sau:

```xml
<mc:AlternateContent>
  <mc:Choice Requires="a14">  <p:sp> … <a:p><a14:m><m:oMath>…</m:oMath></a14:m></a:p> … </p:sp>  </mc:Choice>
  <mc:Fallback>               … nội dung cho phần mềm KHÔNG đọc được OMML …                  </mc:Fallback>
</mc:AlternateContent>
```

- Công thức nằm trong dòng chữ: `<a14:m><m:oMath>` chen giữa các `<a:r>`.
- Công thức display (một dòng riêng): `<a14:m><m:oMathPara><m:oMathParaPr><m:jc m:val="centerGroup"/>…`.
- Mỗi `<m:r>` chứa `<a:rPr>` có `latin typeface="Cambria Math"`, `sz`, màu. Đây là kiểu PowerPoint, không phải `w:rPr` của Word.

## 2. Giá trị bật/tắt của OMML phải là `on`/`off`

`<m:degHide m:val="1"/>` trông hợp lệ, nhưng PowerPoint ghi và đọc `m:val="on"`. Khi dùng `"1"`, dấu căn có thể hiện **ô chỉ số bậc trống**. Người dùng sẽ báo là "dấu căn bị sai". Áp dụng cho mọi thuộc tính dạng này: `degHide`, `subHide`, `supHide`… `verify.py` có kiểm tra.

## 3. Bản dự phòng (Fallback) rất quan trọng

Giáo viên hay mở bằng PowerPoint 2007, Google Slides, WPS, trình xem trên điện thoại hoặc Zalo. Các phần mềm này **không đọc OMML** và hiển thị Fallback.

- Fallback là chữ một dòng (`√(3n²+2)−n`): người dùng không hiểu được phạm vi dấu căn. Đây là lỗi thật đã gặp.
- **Cách đúng**, cũng là cách PowerPoint tự làm: Fallback = shape gốc (giữ nền, viền) + ảnh PNG của phần chữ và công thức, đặt vào nhóm `p:grpSp`. `build.py` làm việc này với chế độ `final_img`.
- Phải nói rõ với người dùng: trong PowerPoint 2010+ công thức vẫn chỉnh sửa được. Ảnh chỉ là bản dự phòng cho phần mềm không hỗ trợ.

## 4. LibreOffice không vẽ OMML trong PPTX

LibreOffice Impress luôn hiển thị Fallback, nên không dùng nó để xem trực tiếp công thức. Quy trình kiểm tra của `build.py`:

1. Mỗi hộp chữ có công thức được xuất thành DOCX nhỏ với cùng OMML (`w:rPr` thay cho `a:rPr`).
2. LibreOffice Writer vẽ OMML trong DOCX được, nhưng cần gói `libreoffice-math`. Thiếu gói này thì công thức biến mất không báo lỗi: `apt-get install -y libreoffice-math`.
3. LibreOffice Math **bỏ qua cỡ chữ OMML (luôn vẽ 12pt)** và **bỏ qua màu (luôn đen)**. Cách xử lý:
   - Thu nhỏ toàn trang DOCX theo hệ số `12 / (cỡ_chữ × 1,12)`.
   - Đổi pixel đen thành trắng sau khi xuất PNG nền trong suốt (`pdftocairo -transp`).
   - Hệ số 1,12 vì Cambria Math rộng hơn: bản xem trước cố tình hơi to, tức là thận trọng.
4. DOCX nào cần hơn một trang nghĩa là chữ **tràn khung**, và được báo trong `overflow`.

## 5. Số mũ và kí hiệu độ

- Bộ phân tích cũ gắn `^` vào **chữ số cuối**, nên `100^2` thành "10" và "0²", còn `60^\circ` thành "6 0°". Đã sửa: số được nhóm nguyên khối, và `^\circ` được đổi thành `°` viết liền.
- Kí hiệu độ (U+00B0) vốn đã ở vị trí trên cao, đưa vào số mũ sẽ quá cao. Viết liền là chuẩn.

## 6. Dấu phẩy thập phân

Office Math coi `,` là dấu câu và có thể chèn khoảng trắng sau nó, gây ra "1, 25". Các số dạng `1,25`, `2,(15)`, `2,` được xuất thành run `<m:rPr><m:nor/></m:rPr>`, tức văn bản thường, nên không bị giãn. LibreOffice cũng vẽ đúng.

LibreOffice escape dấu ngoặc trong run `m:nor`, hiện thành `\(`. Vì vậy chỉ để phần `2,` là `nor`, còn `(15)` để bình thường.

## 7. Dòng display bắt đầu bằng "="

LibreOffice Math vẽ `=` đứng đầu thành `¿`. Ảnh dự phòng cũng bị lỗi theo, và người dùng phần mềm không hỗ trợ OMML sẽ thấy. Luôn viết vế trái (`PQ=…`, `2,(15)=…`), hoặc gộp vào dòng trước.

## 8. Bố cục

- Header (nhãn, tiêu đề, phụ đề có phân số) cần khoảng 1,45 in chiều cao. Phụ đề có phân số lồng hoặc `\lim{\frac{}{}}` dễ tràn nên phải chừa chỗ.
- Bảng gốc (`s.table`) chỉ đặt chữ và số. Nhãn hàng có công thức như $n^2$, $u_n$ đặt bằng shape riêng sát mép trái bảng.
- Không dùng chữ số mũ Unicode (², ⁿ) trong bảng hay trong chữ thường. Đó là kí tự giả lập.
- Kí tự ✓ ✗ ① ② không có trong Times New Roman. Thay bằng chữ ("(đúng)", "Bước 1:").
- Chuỗi tiêu đề thẻ `H()` là chữ thường. Muốn có công thức thì dùng `HR()` (xem `content_template.py`).

## 9. Đóng gói

- Dùng file gốc làm template: giữ theme, master, layout và nền. Chỉ thay XML các slide, rồi cắt `sldIdLst` theo số slide mới.
- Nếu nền là shape phủ toàn slide trong file gốc: đặt màu nền vào `p:bg` của master, đưa khung viền (nếu có) vào master (`--frame`). Như vậy nền cố định, còn nội dung chỉnh sửa được.
- Đổi font theme sang Times New Roman.
- Chạy `clean.py` của skill pptx và `validate.py`, sau đó chạy `verify.py` của skill này.
