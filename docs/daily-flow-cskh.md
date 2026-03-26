# Quy trình làm việc hàng ngày của nhân viên CSKH trên hệ thống CRM

**Tài liệu mô tả UI/UX và flow thao tác sau khi triển khai thành công**

---

> **Lưu ý phân pha:**
> - **Phase 1 (hiện tại):** Hệ thống CRM đã sẵn sàng với hồ sơ bệnh nhân, views theo loại CS, workflows tự động, dashboard. Nhân viên tạo công việc CS thủ công hoặc hệ thống tự tạo qua workflow.
> - **Phase 2 (khi có tích hợp HIS/HIT/IMS):** Dữ liệu bệnh nhân, lịch hẹn, thuốc được đồng bộ tự động. Các mục đánh dấu *(Phase 2)* bên dưới là chức năng chờ tích hợp.

---

## Tổng quan

Hệ thống CRM hoạt động theo mô hình **công việc chăm sóc liên kết với bệnh nhân**. Mỗi lần cần chăm sóc (nội trú, tái khám, beta...) hệ thống tạo một công việc gắn với hồ sơ bệnh nhân tương ứng. Nhân viên CSKH làm việc bằng cách **mở danh sách công việc đã được lọc sẵn** theo từng loại chăm sóc, click vào công việc để xem hồ sơ bệnh nhân liên kết, gọi điện và ghi chú trên timeline.

> **Phase 1:** Nhân viên tạo công việc CS thủ công trên CRM (hoặc workflow tự tạo cho thai kỳ). **Phase 2:** Dữ liệu từ HIS/HIT/IMS tự động tạo công việc — không cần đăng nhập hệ thống bệnh viện.

---

## 1. Đầu ngày: đăng nhập và xem tổng quan

**Thao tác:** Mở trình duyệt → truy cập địa chỉ CRM → đăng nhập bằng tài khoản được cấp.

**Màn hình chính hiển thị:**
- Danh sách bệnh nhân cần chăm sóc hôm nay
- Số bệnh nhân chưa gọi từ hôm qua (nếu có)
- Cảnh báo nếu có ca quá hạn chưa xử lý

**So sánh với hiện tại:**

| Hiện tại | Trên CRM (Phase 1) | Trên CRM (Phase 2 - có tích hợp) |
|----------|----------|----------|
| Đăng nhập HIS, xuất Excel, copy qua Drive... | Mở trình duyệt, tạo task CS thủ công | Mở trình duyệt, danh sách đã sẵn sàng |
| ~30-60 phút chuẩn bị dữ liệu mỗi sáng | ~10 phút tạo task cho BN cần CS | 0 phút — đồng bộ tự động |

---

## 2. Flow chăm sóc nội trú

### Hiện tại (6 bước thủ công)
HIS → xuất Excel → xóa cột → copy sang file nội trú → fill ngày, phòng, BS → tick OR/ET/FET → gọi

### Trên CRM (2 bước)

**Bước 1:** Mở view **"Nội trú"** trong danh sách bệnh nhân → thấy ngay danh sách bệnh nhân nhập/xuất viện hôm nay, đã có sẵn:
- PID, họ tên, SĐT
- Ngày vào viện / xuất viện
- Phòng bệnh, BS thực hiện
- Khoa (HTSS / PTTT / Sản)
- Đánh dấu OR / ET / FET (theo lịch thủ thuật)

**Bước 2:** Click vào bệnh nhân → xem chi tiết hồ sơ → gọi điện → tạo ghi chú trên timeline → cập nhật trạng thái chăm sóc sang "Đã gọi".

---

## 3. Flow chăm sóc CBNM (ca bệnh nhân mới)

### Hiện tại (5 bước thủ công)
HIS → báo cáo tiếp đón → xuất Excel → lọc PID → kéo hàm → fill thuốc + PK/BS từ IMS → gọi

### Trên CRM (2 bước)

**Bước 1:** Mở view **"CBNM"** → danh sách bệnh nhân mới hôm nay, đã có sẵn:
- PID, họ tên, SĐT
- Thuốc đang sử dụng (fill tự động từ IMS)
- PK/BS phụ trách (phân loại từ IMS)
- Ca hủy chu kỳ đã được lọc ra riêng, kèm lý do hủy từ HIS

**Bước 2:** Click vào bệnh nhân → gọi chăm sóc → tạo ghi chú trên timeline → cập nhật trạng thái.

---

## 4. Flow nhắc hẹn thủ thuật

### Hiện tại (3 bước thủ công)
Nhận lịch PHS qua Zalo → nhập PID → fill giờ → gọi nhắc hẹn

### Trên CRM (3 bước — phần này vẫn cần nhập thủ công)

**Bước 1:** Khi PHS ban hành lịch thủ thuật (qua Zalo), nhân viên tìm bệnh nhân theo PID → mở hồ sơ → cập nhật thông tin thủ thuật (loại, ngày, giờ hẹn).

> Lưu ý: phần này chưa tự động được vì lịch PHS gửi qua Zalo, không từ hệ thống. Tuy nhiên, khi nhập PID, hệ thống hiển thị ngay toàn bộ thông tin bệnh nhân — không cần tra cứu thủ công.

**Bước 2:** Gọi nhắc hẹn → tạo ghi chú trên timeline.

**Bước 3:** Cập nhật trạng thái chăm sóc.

---

## 5. Flow gọi tái khám

### Hiện tại (6 bước thủ công, phức tạp nhất)
HIT → xuất lịch hẹn → copy qua Drive → xóa hẹn phòng hồ sơ/cấp cứu → fill thuốc từ sheet IUI/IVF → đối soát chéo 4-5 file (IUI, IVF, CBNM, IMS, HIT) → kiểm tra với file của Doanh → liên hệ HCDD nếu không khớp → gọi

### Trên CRM (2 bước)

**Bước 1:** Mở view **"Tái khám"** → danh sách bệnh nhân cần tái khám hôm nay đã sẵn sàng, bao gồm:
- PID, họ tên, SĐT
- Thuốc đang sử dụng
- Note/nhắc nhở từ phòng khám (nếu có)
- Hẹn phòng hồ sơ / cấp cứu / hành chính đã được tự động loại bỏ
- Trường hợp IMS/HIT không trùng khớp → hiển thị cảnh báo để nhân viên kiểm tra hoặc liên hệ HCDD

**Bước 2:** Click vào bệnh nhân → gọi nhắc tái khám → tạo ghi chú trên timeline → cập nhật trạng thái.

> Quy trình hiện tại mất 6 bước đối soát thủ công → trên CRM hệ thống đối soát tự động, nhân viên chỉ cần xử lý các ca cảnh báo.

---

## 6. Flow chăm sóc beta-thai

### Hiện tại (5 bước thủ công)
HIS → xuất lịch tái khám ngày mai → lọc ca beta/thai → kiểm tra chéo file beta + IUI/IVF → kiểm tra ca sảy/lưu → gửi Miss Linh duyệt → gọi

### Trên CRM (3 bước)

**Bước 1:** Mở view **"Beta-thai"** → danh sách bệnh nhân cần chăm sóc beta đã sẵn sàng:
- **IUI:** các ca ngày sau bơm, cần gọi hôm nay
- **IVF:** các ca đủ 14 ngày sau chuyển phôi
- Đã đối soát với danh sách tái khám
- Ca sảy / ca lưu được đánh dấu riêng

**Bước 2:** Kiểm tra danh sách → gửi quản lý duyệt (nút "Gửi duyệt" trên hệ thống).

**Bước 3:** Sau khi được duyệt → click vào bệnh nhân → gọi chăm sóc → nhập số liệu beta vào hồ sơ → nếu beta đậu, hệ thống tự chuyển giai đoạn sang "Mang thai" và tạo lịch chăm sóc thai kỳ hàng tháng.

---

## 7. Flow chăm sóc thai kỳ

### Hiện tại
Nhập thủ công vào file, tự nhớ lịch chăm sóc mỗi tháng 1 lần.

### Trên CRM (1 bước)

Mở view **"Thai kỳ"** → danh sách bệnh nhân mang thai đến hạn chăm sóc tháng này. Hệ thống tự đưa bệnh nhân vào view khi đến hạn (mỗi tháng 1 lần). Nhân viên click vào bệnh nhân → gọi → tạo ghi chú trên timeline → cập nhật trạng thái.

> Ca sảy / ca lưu được đánh dấu riêng và không xuất hiện trong view nữa.

---

## 8. Cuối ngày: cập nhật và báo cáo

**Nhân viên:**
- Kiểm tra các bệnh nhân chưa gọi được, ghi chú lý do (không liên lạc được, hẹn gọi lại...)
- Cập nhật trạng thái phù hợp: "Cần gọi lại" / "Không liên lạc được"

**Người điều phối:**
- Xem tổng quan toàn nhóm: bệnh nhân đã gọi / chưa gọi / quá hạn
- Phân bổ lại bệnh nhân nếu cần (nhân viên nghỉ, cân bằng khối lượng)

**Quản lý:**
- Mở dashboard → xem báo cáo: số cuộc gọi, tỷ lệ thành công, ca quá hạn, khối lượng theo nhân viên
- Không cần hỏi nhân viên tổng hợp — dữ liệu cập nhật real-time

---

## 9. Giao diện và bố cục màn hình

### Sidebar (thanh bên trái)
```
├── Khoa (danh sách khoa bệnh viện)
├── Bệnh nhân (hồ sơ bệnh nhân)
├── Tasks (công việc chăm sóc)
│   ├── View: All Tasks
│   ├── View: CS nội trú
│   ├── View: CS CBNM
│   ├── View: CS thủ thuật
│   ├── View: CS tái khám
│   ├── View: CS beta-thai
│   ├── View: CS thai kỳ
│   └── View: CS theo trạng thái (Kanban)
├── Notes
├── Dashboards
└── Cài đặt
```

> Mỗi view là **một bộ lọc sẵn** trên danh sách công việc chăm sóc. Mỗi công việc liên kết với một bệnh nhân — click vào công việc để xem hồ sơ bệnh nhân liên kết. Nhân viên chuyển giữa các view bằng cách click vào tab view trên thanh trên.

### Màn hình danh sách công việc chăm sóc

Mỗi view hiển thị dạng bảng, các cột khác nhau tùy loại chăm sóc. Cột "Bệnh nhân" hiển thị tên bệnh nhân liên kết — click vào để mở hồ sơ chi tiết.

#### View "Nội trú"

| PID | Họ tên | SĐT | Khoa | Nhập/Xuất | Ngày vào | Ngày xuất | Phòng | BS | OR | ET | FET | Đối tác | Trạng thái CS |
|-----|--------|-----|------|-----------|----------|-----------|-------|----|----|----|----|---------|---------------|
| 10234 | Nguyễn Thị Lan | 0912... | HTSS | Xuất viện | 15/3 | 22/3 | P.301 | BS. Minh | ✓ | | | BHYT | Chưa gọi |

#### View "CBNM"

| PID | Họ tên | SĐT | PK | BS | Thuốc | Liệu trình | Hủy CK | Lý do hủy | Trạng thái CS |
|-----|--------|-----|----|----|-------|-------------|--------|-----------|---------------|
| 10567 | Phạm Thị Mai | 0945... | PK2 | BS. Hà | Progynova 2mg, Utrogestan | IVF chu kỳ 2 | | | Chưa gọi |
| 10890 | Trần Thị Hoa | 0908... | PK1 | BS. Long | — | — | ✓ | KH yêu cầu dừng | Không CS |

#### View "Tái khám"

| PID | Họ tên | SĐT | PK | BS | Thuốc | Liệu trình | Note PK | ⚠ Cảnh báo | Trạng thái CS |
|-----|--------|-----|----|----|-------|-------------|---------|------------|---------------|
| 10567 | Phạm Thị Mai | 0945... | PK2 | BS. Hà | Progynova 2mg | IVF chu kỳ 2 | Nhắc mang KQ XN | | Chưa gọi |
| 10789 | Lê Thị Ngọc | 0956... | PK3 | BS. Tú | Gonal-F 75IU | IUI chu kỳ 1 | | ⚠ IMS/HIT không khớp | Cần kiểm tra |

> Dòng có cảnh báo ⚠ hiển thị nổi bật — nhân viên cần liên hệ HCDD kiểm tra trước khi gọi.

#### View "Beta-thai"

| PID | Họ tên | SĐT | Loại | Ngày bơm/chuyển phôi | Ngày đủ hạn | Số liệu beta | Kết quả | Duyệt | Trạng thái CS |
|-----|--------|-----|------|----------------------|-------------|--------------|---------|-------|---------------|
| 10234 | Nguyễn Thị Lan | 0912... | IVF | 08/3 | 22/3 (14 ngày) | — | Chờ KQ | Đã duyệt | Chưa gọi |
| 10345 | Võ Thị Thanh | 0967... | IUI | 21/3 | 22/3 (ngày sau bơm) | 250 | Đậu ✓ | Đã duyệt | Đã gọi |

> Khi nhập kết quả beta đậu trên hồ sơ bệnh nhân → hệ thống tự chuyển giai đoạn sang "Mang thai" và tạo lịch chăm sóc thai kỳ.

#### View "Thai kỳ"

| PID | Họ tên | SĐT | Tuần thai | Ngày dự sinh | Lần CS gần nhất | Ghi chú lần trước | Tình trạng | Trạng thái CS |
|-----|--------|-----|-----------|--------------|-----------------|-------------------|------------|---------------|
| 10345 | Võ Thị Thanh | 0967... | Tuần 12 | 20/12/2026 | 22/2/2026 | Thai phát triển bình thường | Bình thường | Chưa gọi |
| 10456 | Hoàng Thị Yến | 0978... | Tuần 8 | 15/1/2027 | 20/2/2026 | — | ⚠ Sảy | Không CS |

> Ca sảy / ca lưu được đánh dấu riêng và không xuất hiện trong danh sách cần gọi.

---

**Thao tác chung trên mọi view:**
- **Lọc nhanh:** theo trạng thái gọi (Chưa gọi / Đã gọi / Cần gọi lại / Không liên lạc được), theo ngày
- **Sắp xếp:** theo deadline, theo trạng thái
- **Tìm kiếm:** nhập PID hoặc tên bệnh nhân
- **Kanban:** chuyển sang view "CS theo trạng thái" để xem tổng quan dạng cột (Chưa gọi | Đã gọi | Cần gọi lại | Không liên lạc được)

### Màn hình chi tiết bệnh nhân

Khi click vào bệnh nhân liên kết trong công việc, mở trang chi tiết hồ sơ:

- **Phần trên:** thông tin cá nhân (tên, PID, SĐT, ngày sinh, CCCD, BHYT, nhóm máu, người thân)
- **Phần giữa:** thông tin liệu trình (giai đoạn, khoa, PK/BS, thuốc, ngày bơm/chuyển phôi, số liệu beta)
- **Phần dưới:** timeline — dòng thời gian hiển thị toàn bộ lịch sử:
  - Ghi chú từ các lần gọi chăm sóc
  - Thay đổi giai đoạn điều trị
  - Thay đổi thuốc
  - Kết quả beta
  - Mọi thao tác của nhân viên đều được ghi nhận

### Thao tác ghi chú sau cuộc gọi

Sau khi gọi xong, nhân viên thao tác trên **2 nơi**:

**Trên công việc chăm sóc:**
1. Cập nhật trạng thái gọi (Đã gọi / Cần gọi lại / Không liên lạc được)
2. Ghi chú nhanh vào trường "Ghi chú cuộc gọi" (VD: "Không nghe máy, gọi lại chiều")

**Trên hồ sơ bệnh nhân (nếu cần ghi chú chi tiết):**
1. Click vào bệnh nhân liên kết → mở hồ sơ
2. Click nút **"Tạo ghi chú"** (Note)
3. Nhập nội dung chi tiết → ghi chú hiển thị trên timeline bệnh nhân, lưu vĩnh viễn

---

## 10. Tóm tắt so sánh

| Quy trình | Hiện tại | Trên CRM |
|-----------|----------|----------|
| Nội trú | 6 bước, ~30 phút chuẩn bị | 2 bước, dữ liệu có sẵn |
| CBNM | 5 bước, tra cứu IMS thủ công | 2 bước, thuốc/PK tự fill |
| Thủ thuật | 3 bước, nhập từ Zalo | 3 bước (vẫn nhập thủ công, nhưng tự điền thông tin BN) |
| Tái khám | 6 bước, đối soát 4-5 file | 2 bước, đối soát tự động + cảnh báo |
| Beta-thai | 5 bước, kiểm tra chéo nhiều file | 3 bước, đối soát tự động + duyệt trên hệ thống |
| Thai kỳ | Tự nhớ lịch, nhập thủ công | View tự hiển thị bệnh nhân đến hạn |
| Báo cáo | Tổng hợp thủ công khi quản lý hỏi | Dashboard real-time |
