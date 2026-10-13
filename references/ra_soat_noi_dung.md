# Rà soát nội dung toán học và phái sinh bài tập

## 1. Rà soát file gốc: những lỗi thực tế đã gặp

| Loại lỗi | Ví dụ đã gặp | Cách xử lý |
|---|---|---|
| Sai số chương/bài | "Chương III: Vectơ…" (đúng: Chương II, Toán 12); "Chương II / Chương V" lẫn lộn | Đối chiếu bộ sách (KNTT, CTST, Cánh Diều) và tên file |
| Sai phép tính | 5,975 thay vì 6,025; Q₁ sai do nhầm tần số tích lũy; phương sai 86 thay vì 81 | **Tính lại mọi con số bằng Python** (`fractions.Fraction`) |
| Sai lập luận nhưng đúng đáp số | BP = AP + PB; "tam giác cân tại S" (thực ra cân tại I) | Kiểm tra từng bước, không chỉ đáp số |
| Đề bài bất khả thi | Biểu diễn PQ theo AB, DC khi P ∈ AB, Q ∈ CD | Chứng minh được hay không bằng phép biểu diễn theo cơ sở |
| Dùng quy tắc ngoài sách | "tích hai vô cực dương" (KNTT không có); quy tắc thương với dãy dần tới vô cực | Viết lại theo đúng bảng quy tắc của sách |
| Kiến thức ngoài chương trình / chưa học | "chuỗi hội tụ"; n^(1/2) trước chương lũy thừa; đồng phẳng trong Toán 12 mới | Bỏ, hoặc thay bằng cách giải trong chương trình |
| Thuật ngữ sai | "hàm lũy thừa" cho dãy số | Dùng đúng: "dãy" |
| Trích dẫn bịa | Câu nói gán cho Robert May (1976) | Không có nguồn thì bỏ |
| Kết luận quá đà | "ΔQ hoàn toàn không bị ảnh hưởng"; "thiết bị chính xác hơn" khi chỉ so độ lệch chuẩn | Nói đúng mức: "ít bị ảnh hưởng", "ổn định hơn" |
| Kí hiệu | `u_1`, `x^2`, `1/(1-q)` gõ chữ; dấu chấm thập phân | OMML; dấu phẩy thập phân |
| Chính tả | "KHÔNG GIANG", "Đăng thức", "Tỉnh chất" | Đọc lại toàn văn |

Ghi lại **mọi lỗi tìm được** để báo cáo cho người dùng khi bàn giao.

## 2. Quy ước kí hiệu chuẩn (sách giáo khoa Việt Nam, chương trình 2018)

- Số thập phân dùng **dấu phẩy**: 1,25. Phân cách tọa độ, phần tử dùng **dấu chấm phẩy**: A(1; 2; −1).
- Số tuần hoàn: 2,(15). Khoảng: [a; b), (−∞; 3].
- Giới hạn dãy số viết `lim uₙ` (KNTT không ghi n → +∞ bên dưới). Giới hạn hàm số: lim với x → x₀ bên dưới.
- Vectơ có mũi tên: $\vec{AB}$, $\vec{a}$. Góc: $\widehat{ABC}$.
- Thống kê ghép nhóm: tần số $n_i$, cỡ mẫu $n$, giá trị đại diện $x_i$, số trung bình $\overline{x}$, khoảng tứ phân vị $\Delta_Q$, phương sai $s^2$ với hệ số $\frac{1}{n}$.
- Hàm và toán tử đứng thẳng: lim, sin, cos, tan, log, ln. Biến và tên điểm in nghiêng.
- Đơn vị (cm, giờ, km/h) để ngoài công thức, đứng thẳng.
- Độ: 60° viết liền.

## 3. Phái sinh bài tập (thay toàn bộ ví dụ/bài tập gốc)

Nguyên tắc: **cùng kiến thức, cùng dạng, cùng độ khó, khác số liệu**. Tránh số quá "đẹp" so với đề gốc.

1. Xác định cấu trúc đề gốc: dạng toán, số bước, kĩ thuật then chốt (chia bậc cao nhất, nhân liên hợp, đặt nhân tử, quy tắc ba điểm…).
2. Chọn số liệu mới sao cho:
   - đáp số gọn (phân số tối giản, căn đơn giản) nhưng không trùng đề gốc;
   - nếu đề gốc có tính chất đặc biệt (giá trị ngoại lệ, góc tù, |q| < 1…) thì đề mới giữ tính chất đó;
   - có thể đảo hướng để đa dạng: đề gốc ra +∞ thì một bài mới ra −∞, đề gốc góc 60° thì đề mới 120°.
3. **Tìm số liệu bằng code** khi có ràng buộc. Ví dụ: tìm bộ tần số có trung bình và phương sai nguyên, hoặc vectơ có độ dài nguyên.
4. **Kiểm tra đáp số bằng hai cách độc lập.** Ví dụ: Zeno tính bằng tổng cấp số nhân và bằng vận tốc tương đối; đường gấp khúc tính bằng công thức và bằng dựng hình số; giới hạn tính bằng biến đổi và bằng thay n = 10⁶.
5. Trắc nghiệm: phương án nhiễu phải hợp lí, vd lấy nhầm 2a − b thay vì 2a + b, quên chia 3, lấy nghịch đảo q. Đổi vị trí đáp án đúng giữa các câu.
6. Cập nhật đồng bộ: đề, lời giải, đáp số, hình vẽ, tóm tắt cuối bài, bảng "các dạng bài".

Mẫu kiểm tra nhanh bằng Python:

```python
from fractions import Fraction as F
print(F(1) / (1 - F(-1, 3)))            # tổng cấp số nhân lùi vô hạn
import math; print([math.sqrt(n*n+4*n)-n for n in (10, 10**3, 10**6)])   # giới hạn -> 2
```

## 4. Số lượng slide

- Người dùng thường yêu cầu "tối đa N slide" hoặc **"đủ N slide như bản gốc"**. Hỏi lại, hoặc giữ đúng số slide gốc nếu không rõ. Đã có trường hợp người dùng yêu cầu đủ 20 slide sau khi nhận bản rút gọn.
- Khi cần thêm slide, không nhồi nhét. Ưu tiên theo thứ tự:
  1. tách "phân tích/nhận diện" và "lời giải" thành hai slide (đúng nhịp giảng dạy);
  2. thêm thẻ "lưu ý / sai lầm thường gặp / kiểm tra";
  3. thêm hình minh họa (trục số tổng riêng, đồ thị dãy, bảng số liệu);
  4. thêm slide "bài tập tự luyện" có đáp số.
