# Cú pháp công thức (LaTeX rút gọn → Office Math)

Công thức viết trong `$...$` bên trong chuỗi của `TX()`, `L()`, `HR()`, `label()`, hoặc cả chuỗi trong `D()` (công thức display) và `M()` (run công thức). `scripts/mathdsl.py` chuyển sang OMML thật.

Trong file `content.py` các chuỗi là chuỗi Python thường, nên **mỗi dấu `\` phải viết thành `\\`** (vd `'$\\frac{1}{2}$'`). Có thể dùng chuỗi raw `r'...'` để viết một dấu `\`.

## Cấu trúc

| Viết | Kết quả | Ghi chú |
|---|---|---|
| `\frac{a}{b}` | phân số tử/mẫu xếp dọc | lồng được |
| `\sqrt{x}` | căn bậc hai, gạch ngang phủ hết biểu thức | luôn dùng ngoặc nhọn |
| `x^2`, `x^{n-1}` | số mũ | số mũ nhiều kí tự phải có `{}` |
| `x_1`, `u_{n+1}` | chỉ số dưới | |
| `x_1^2` | chỉ số + số mũ | |
| `\vec{AB}` | vectơ có mũi tên | |
| `\widehat{ABC}`, `\hat{C}` | góc (mũ) | |
| `\overline{x}` | số trung bình x̄ | |
| `\left( ... \right)` | ngoặc co giãn theo nội dung | dùng `(`, `[`, `|`, `\{`, `.` (rỗng) |
| `\left| ... \right|` | trị tuyệt đối, độ dài vectơ | |
| `\sys{x=1\\y=2}` | hệ phương trình có dấu `{` | trong chuỗi Python: `\\sys{x=1\\\\y=2}` |
| `\sum_{i=1}^{k}{n_ix_i}` | tổng Σ | thân tổng luôn trong `{}` |
| `\lim{u_n}` | lim đứng thẳng | đối số luôn trong `{}`: `\lim{\frac{1}{n}}` |
| `\cos{\alpha}`, `\sin{B}`, `\tan{x}` | hàm lượng giác đứng thẳng | đối số trong `{}` |
| `\cos^{2}{\alpha}` | cos²α | |
| `\text{...}` | chữ đứng trong công thức | hạn chế dùng; đơn vị đặt ngoài `$...$` |
| `\mathbb{N}`, `\R` | ℕ, ℝ | |
| `\Delta_Q` | Δ_Q | |

## Số và kí hiệu đặc biệt

- **Số được nhóm nguyên khối**: `100^2` cho 100², `10^{n-1}` cho 10ⁿ⁻¹. Số mũ áp lên cả số.
- **Dấu phẩy thập phân** (chuẩn Việt Nam): viết thẳng `1,25`, `0,08^5`. Bộ chuyển tự đánh dấu là văn bản thường nên không bị chèn khoảng trắng.
- **Số tuần hoàn**: `2,(15)` hiển thị đúng.
- **Độ**: `60^\circ` được tự đổi thành `60°` viết liền, không đẩy lên làm số mũ.
- Dấu trừ `-` tự đổi thành `−` (U+2212). Dấu nháy `A'` thành `A′`.
- Dấu cách bị bỏ qua. Dùng `\,` (hẹp), `\ ` (vừa), `\quad` (rộng) khi cần.

## Kí hiệu có sẵn

`\cdot \times \div \pm \le \ge \leq \geq \ne \neq \approx \equiv \sim \in \notin \subset \cup \cap \emptyset \perp \parallel \angle \triangle \infty \to \Rightarrow \Leftarrow \Leftrightarrow \exists \forall \neg \mid \dots \ldots \cdots \circ \deg`

Chữ Hy Lạp: `\alpha \beta \gamma \delta \theta \lambda \mu \pi \sigma \omega \varphi \varepsilon \Delta`

Lệnh lạ sẽ báo lỗi `unknown cmd`. Khi đó thêm vào bảng `SYM` trong `mathdsl.py`, hoặc viết lại.

## Lỗi hay gặp khi viết

| Sai | Đúng | Vì sao |
|---|---|---|
| `\cos 60^\circ` | `\cos{60^\circ}` | không có `{}` thì hàm chỉ nhận một kí tự |
| `\lim u_n` | `\lim{u_n}` | như trên |
| `\cos(\vec a,\vec b)` | `\cos{\left(\vec{a},\vec{b}\right)}` | ngoặc thường không co giãn và không thuộc đối số |
| `D('=\\sqrt{...}')` | `D('PQ=\\sqrt{...}')` | dòng display bắt đầu bằng `=` hiển thị sai ở bản dự phòng |
| `$t=1\\ \\text{(giờ)}$` | `$t=1$ (giờ)` | đơn vị phải đứng thẳng, nằm ngoài công thức |
| `x²` gõ Unicode trong chữ | `$x^2$` | kí tự giả lập là lỗi; `verify.py` sẽ báo |
