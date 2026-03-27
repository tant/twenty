# Hướng dẫn sử dụng CRM cho Nhân viên Chăm sóc Khách hàng

**Bệnh Viện Hỗ Trợ Sinh Sản & Nam Học Sài Gòn**
**Địa chỉ hệ thống:** https://bvhmsg.fixpartner.co

---

## Mục lục

1. [Đăng nhập và giao diện chính](#1-đăng-nhập-và-giao-diện-chính)
2. [Công việc CS xuất hiện như thế nào?](#2-công-việc-cs-xuất-hiện-như-thế-nào)
3. [Quy trình chăm sóc nội trú](#3-quy-trình-chăm-sóc-nội-trú)
4. [Quy trình chăm sóc CBNM (bệnh nhân mới)](#4-quy-trình-chăm-sóc-cbnm)
5. [Quy trình nhắc hẹn thủ thuật](#5-quy-trình-nhắc-hẹn-thủ-thuật)
6. [Quy trình gọi tái khám](#6-quy-trình-gọi-tái-khám)
7. [Quy trình chăm sóc beta-thai](#7-quy-trình-chăm-sóc-beta-thai)
8. [Quy trình chăm sóc thai kỳ](#8-quy-trình-chăm-sóc-thai-kỳ)
9. [Kanban — Theo dõi trạng thái tổng quan](#9-kanban--theo-dõi-trạng-thái-tổng-quan)
10. [Ghi chú trên công việc CS](#10-ghi-chú-trên-công-việc-cs)
11. [Dashboard báo cáo (dành cho quản lý)](#11-dashboard-báo-cáo)

---

## 1. Đăng nhập và giao diện chính

**Bước 1:** Mở trình duyệt → nhập `https://bvhmsg.fixpartner.co`
**Bước 2:** Nhập email và mật khẩu đã được cấp → bấm **Đăng nhập**

### Thanh bên trái (sidebar)

```
Workspace
├── Các Khoa          → Danh sách 11 khoa/phòng khám
├── Bệnh nhân         → Hồ sơ bệnh nhân
├── Công việc CS       → Danh sách việc cần làm (★ dùng nhiều nhất)
│   ├── CS nội trú
│   ├── CS CBNM
│   ├── CS thủ thuật
│   ├── CS tái khám
│   ├── CS beta-thai
│   ├── CS thai kỳ
│   └── CS theo trạng thái (Kanban)
├── Báo cáo           → Dashboard tổng quan
├── Quy trình          → Workflows tự động
├── Chu kỳ điều trị    → Theo dõi IUI/IVF
└── Lần nhập viện      → Lịch sử nội trú
```

> **Mẹo:** Phần lớn thời gian làm việc nằm ở **Công việc CS**. Click vào tên view để chuyển giữa các loại chăm sóc.

---

## 2. Công việc CS xuất hiện như thế nào?

Mỗi sáng lúc 6:00, hệ thống **tự động đồng bộ** dữ liệu từ HIS/HIT/IMS và tạo công việc CS. Khi nhân viên mở CRM, danh sách việc cần làm đã sẵn sàng.

### Tổng quan

| Loại CS | Nguồn dữ liệu | Cách tạo | Assignee |
|---------|---------------|----------|----------|
| **Nội trú** | HIS → Báo cáo nội trú | Tự động | Quản lý phân công |
| **CBNM** | HIS → Báo cáo tiếp đón | Tự động | Quản lý phân công |
| **Tái khám** | HIT → Lịch hẹn KH | Tự động | Quản lý phân công |
| **Beta-thai** | File IUI/IVF | Tự động | Quản lý phân công |
| **Thai kỳ** | Kết quả beta đậu | Tự động (workflow) | Quản lý phân công |
| **Thủ thuật** | Lịch PHS qua Zalo | **Tạo thủ công** | NV tự tạo |

> **Lưu ý:** CS thủ thuật là loại duy nhất cần tạo thủ công. Lịch thủ thuật do PHS ban hành qua nhóm Zalo, không nằm trong HIS/HIT/IMS.

### Tạo công việc thủ thuật (thủ công)

1. Nhận lịch thủ thuật PHS qua Zalo
2. Mở view **"CS thủ thuật"** → bấm **"+ Bản ghi mới"**
3. Nhập thông tin:
   - **Bệnh nhân:** Tìm theo PID hoặc tên
   - **Loại lịch hẹn:** Lấy trứng / IUI / Chuyển phôi / Phẫu thuật / PRP
   - **Giờ hẹn, Giờ có mặt:** Theo lịch PHS
   - **Hạn chăm sóc:** Ngày thủ thuật
4. Công việc hiển thị trong view với trạng thái **"Chưa gọi"**

### Trường thông tin trên mỗi công việc CS

| Trường | Mô tả |
|--------|-------|
| Loại chăm sóc | Nội trú / CBNM / Thủ thuật / Tái khám / Beta-thai / Thai kỳ |
| Bệnh nhân | Link tới hồ sơ BN (click để xem chi tiết) |
| Hạn chăm sóc | Ngày cần gọi |
| Assignee | NV CSKH phụ trách task này |
| Trạng thái gọi | Chưa gọi / Đã gọi / Cần gọi lại / Không liên lạc |
| Ghi chú chăm sóc | Kết quả liên lạc (VD: "09:54 ĐÃ GỌI", "KNM, đã nhắn Zalo") |
| Ghi chú | Thông tin bổ sung về ca này |
| Lưu ý | Cảnh báo quan trọng cần chú ý khi gọi |
| BS phụ trách | Bác sĩ chính |
| Phòng khám | PK nào |
| Thuốc | Thuốc tại thời điểm |
| Trạng thái duyệt | Cho beta-thai: Chưa duyệt / Đã duyệt / Từ chối |

### Nội trú khoa Phụ sản — 2 công việc CS

Riêng khoa Phụ sản, hệ thống tự tạo **2 task** cho mỗi sản phụ xuất viện:

| Task | Hạn CS | Nội dung |
|------|--------|---------|
| CS sau xuất viện 1 ngày | Ngày xuất + 1 | Chăm sóc mẹ & bé sau 1 ngày xuất viện |
| CS 7-10 ngày sau xuất viện | Ngày xuất + 7 | Hỏi thăm sức khỏe, kết quả sàng lọc sơ sinh |

### So sánh quy trình cũ (Excel) với CRM

| Trước (Excel) | Trên CRM |
|---------------|----------|
| Xuất Excel từ HIS/HIT, copy-paste, fill thủ công (6+ bước) | Mở view → task đã sẵn sàng → gọi → ghi chú (2 bước) |
| Đối soát chéo 4-5 file, dễ sót BN | Tất cả trong 1 view, lọc/sắp xếp theo hạn CS |
| Ghi chú trên file Drive, dễ mất | Ghi chú trực tiếp trên task, lưu vĩnh viễn |
| Không biết ai gọi ca nào | Assignee ghi rõ NV phụ trách |

---

## 3. Quy trình chăm sóc nội trú

**Đối tượng:** Bệnh nhân nhập/xuất viện tại khoa HTSS, PTTT, Sản

### Các bước

1. Click **Công việc CS** trên sidebar
2. Chọn view **"CS nội trú"** ở thanh trên
3. Thấy danh sách bệnh nhân nội trú với các cột:
   - Tiêu đề công việc
   - **Bệnh nhân** (click để xem hồ sơ)
   - **BS phụ trách**
   - **Phòng khám**
   - Trạng thái gọi
   - Hạn chăm sóc
   - Ghi chú chăm sóc
   - Thuốc
4. Click vào bệnh nhân → xem hồ sơ chi tiết (PID, SĐT, thuốc, ngày vào/xuất viện)
5. Gọi điện cho bệnh nhân
6. Quay lại công việc → cập nhật:
   - **Trạng thái gọi:** Chưa gọi → **Đã gọi** (hoặc Cần gọi lại / Không liên lạc được)
   - **Ghi chú chăm sóc:** VD: "BN uống thuốc đều, hẹn tái khám 15/04"

### So sánh với trước

| Trước (Excel) | Trên CRM |
|---|---|
| HIS → xuất Excel → xóa cột → copy → fill thủ công → gọi (6 bước) | Mở view → gọi → ghi chú (2 bước) |

---

## 4. Quy trình chăm sóc CBNM

**Đối tượng:** Bệnh nhân mới đến khám, cần tư vấn

### Các bước

1. Chọn view **"CS CBNM"**
2. Thấy danh sách với cột: Bệnh nhân, BS phụ trách, Thuốc, Trạng thái gọi, Ghi chú
3. Click vào bệnh nhân liên kết → xem thông tin liệu trình, thuốc đang dùng
4. Gọi chăm sóc → cập nhật trạng thái và ghi chú

> **Lưu ý:** Nếu bệnh nhân hủy chu kỳ, ghi rõ lý do vào trường **"Lý do hủy chu kỳ"** trên hồ sơ bệnh nhân. Task sẽ không cần gọi nữa.

---

## 5. Quy trình nhắc hẹn thủ thuật

**Đối tượng:** Bệnh nhân có lịch thủ thuật (lấy trứng, IUI, chuyển phôi, phẫu thuật...)

### Các bước

1. Khi PHS ban hành lịch thủ thuật (qua Zalo):
   - Bấm **"+ Bản ghi mới"** trên view **"CS thủ thuật"**
   - Nhập tiêu đề: VD "Nhắc hẹn - Nguyễn Thị Lan - Lấy trứng 7h30"
   - Chọn **Loại lịch hẹn:** Lấy trứng / IUI / Chuyển phôi / Phẫu thuật / PRP
   - Chọn **Hạn chăm sóc** (ngày thủ thuật)
   - Link với bệnh nhân
2. Gọi nhắc hẹn → cập nhật trạng thái

> **Lưu ý:** Phần này vẫn cần nhập thủ công vì lịch PHS gửi qua Zalo, không từ hệ thống. Nhưng khi nhập PID, hệ thống hiển thị ngay toàn bộ thông tin bệnh nhân.

---

## 6. Quy trình gọi tái khám

**Đối tượng:** Bệnh nhân có lịch hẹn tái khám

### Các bước

1. Chọn view **"CS tái khám"**
2. Thấy danh sách với: Bệnh nhân, BS, Thuốc, Trạng thái gọi, Ghi chú, Hạn
3. Đối soát: kiểm tra thuốc, lời dặn BS có khớp không
4. Gọi nhắc tái khám → cập nhật trạng thái và ghi chú

### So sánh

| Trước | Trên CRM |
|---|---|
| 6 bước đối soát chéo HIT/IMS/sheet IUI/IVF/CBNM | View hiện sẵn, đối soát tự động khi có tích hợp HIS (Phase 3) |

---

## 7. Quy trình chăm sóc beta-thai

**Đối tượng:**
- **IUI:** bệnh nhân ngày sau bơm IUI
- **IVF:** bệnh nhân đủ 14 ngày sau chuyển phôi

### Các bước

1. Chọn view **"CS beta-thai"**
2. Thấy: Bệnh nhân, Loại lịch hẹn (IUI/IVF), Hạn, **Trạng thái duyệt**, Trạng thái gọi
3. Kiểm tra danh sách → nếu cần duyệt, cập nhật **Trạng thái duyệt** = "Chưa duyệt"
4. Gửi quản lý xem → quản lý đổi thành **"Đã duyệt"** hoặc **"Từ chối"**
5. Sau khi được duyệt → gọi bệnh nhân
6. Nhập kết quả beta vào hồ sơ bệnh nhân (trường **Kết quả Beta**)
7. Nếu beta dương tính:
   - Cập nhật **Giai đoạn điều trị** → **"Thai kỳ"**
   - Nhập **Tuần thai** và **Ngày dự sinh**
   - Bệnh nhân sẽ tự xuất hiện trong view "CS thai kỳ"

> **Trường hợp sảy/lưu:** Cập nhật Giai đoạn → **"Sảy thai"** hoặc **"Lưu thai"**. Bệnh nhân sẽ không hiện trong view thai kỳ nữa.

---

## 8. Quy trình chăm sóc thai kỳ

**Đối tượng:** Bệnh nhân mang thai (beta đậu), chăm sóc mỗi tháng 1 lần

### Các bước

1. Chọn view **"CS thai kỳ"**
2. Thấy: Bệnh nhân, Hạn, Thuốc, Trạng thái gọi, Ghi chú
3. Gọi hỏi thăm → ghi chú kết quả (siêu âm, tình trạng thai, thuốc bổ sung)
4. Cập nhật trạng thái → **"Đã gọi"**
5. Tạo công việc mới cho lần gọi tháng sau (hoặc workflow tự tạo khi activate)

> **Cập nhật tuần thai:** Mỗi lần gọi, vào hồ sơ bệnh nhân cập nhật **Tuần thai** cho chính xác.

---

## 9. Kanban — Theo dõi trạng thái tổng quan

Chọn view **"CS theo trạng thái"** để xem Kanban:

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│  Chưa gọi    │  │   Đã gọi     │  │ Cần gọi lại  │  │ Không liên lạc   │
│              │  │              │  │              │  │     được         │
│  ▪ Lan - NT  │  │  ▪ Mai - TK  │  │  ▪ Hoa - BT  │  │  ▪ Minh - CBNM   │
│  ▪ Thanh - TT│  │  ▪ Hong - TK │  │              │  │                  │
│  ▪ Ngoc - BT │  │  ▪ Yen - NT  │  │              │  │                  │
│  ...         │  │  ...         │  │              │  │                  │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────────┘
```

**Cách dùng:**
- Kéo thả task từ cột "Chưa gọi" sang "Đã gọi" sau khi gọi xong
- Cuối ngày: cột "Chưa gọi" phải còn ít nhất có thể
- Cột "Không liên lạc được" → chuyển sang ngày mai

---

## 10. Ghi chú trên công việc CS

Mỗi công việc CS có 3 trường ghi chú:

| Trường | Khi nào dùng | Ví dụ |
|--------|-------------|-------|
| **Ghi chú chăm sóc** | Sau mỗi lần liên lạc (gọi/nhắn tin) | "09:54 ĐÃ GỌI, BN uống thuốc đều, hẹn TK 15/04" |
| | | "KNM, đã nhắn SMS Zalo" |
| **Ghi chú** | Thông tin bổ sung về ca này | "BN hỏi về kết quả XN, chuyển BS tư vấn" |
| **Lưu ý** | Cảnh báo quan trọng cần chú ý | "BN dị ứng Paracetamol", "Chồng bận, gọi vợ" |

---

## 11. Dashboard báo cáo

**Dành cho:** Trưởng phòng CSKH, quản lý

### Xem báo cáo

1. Click **Báo cáo** trên sidebar
2. Click vào **"Báo cáo CSKH"**

### 8 biểu đồ:

| Biểu đồ | Ý nghĩa |
|----------|---------|
| **Tổng bệnh nhân** | Số BN trong hệ thống |
| **Tổng công việc CS** | Tổng task đã tạo |
| **Chưa gọi** | Số task chưa xử lý |
| **Công việc theo loại chăm sóc** | Phân bổ: Nội trú / CBNM / Thủ thuật / Tái khám / Beta / Thai kỳ |
| **Trạng thái cuộc gọi** | Đã gọi / Chưa gọi / Cần gọi lại / Không liên lạc |
| **BN theo giai đoạn điều trị** | IVF / IUI / Thai kỳ / Hoàn thành / Sảy-Lưu |
| **Công việc CS theo thời gian** | Xu hướng theo tuần — tăng hay giảm |
| **Khối lượng CS theo nhân viên** | Ai gọi bao nhiêu — cân bằng khối lượng |

---

## Các thao tác thường dùng

| Thao tác | Cách làm |
|----------|----------|
| Tìm bệnh nhân | Bấm **Ctrl+K** → nhập PID hoặc tên |
| Tạo công việc CS mới | Click **"+ Bản ghi mới"** trên view |
| Cập nhật trạng thái gọi | Click vào task → đổi trường "Trạng thái gọi" |
| Xem hồ sơ BN từ task | Click tên BN trong cột "Bệnh nhân" |
| Tạo ghi chú chi tiết | Mở hồ sơ BN → Ghi chú → + Thêm mới |
| Xem Kanban | Chọn view "CS theo trạng thái" |
| Xem báo cáo | Sidebar → Báo cáo → Báo cáo CSKH |
| Lọc theo ngày | Bấm "Lọc" → chọn "Hạn chăm sóc" → chọn ngày |
| Sắp xếp theo hạn | Bấm "Sắp xếp" → "Hạn chăm sóc" → Tăng dần |

---

## Quy ước trạng thái

### Trạng thái gọi (trên công việc CS)

| Trạng thái | Khi nào dùng | Màu |
|---|---|---|
| **Chưa gọi** | Mới tạo, chưa xử lý | Xanh nhạt |
| **Đã gọi** | Đã gọi và liên lạc được | Xanh lá |
| **Cần gọi lại** | BN bận, hẹn gọi lại sau | Cam |
| **Không liên lạc được** | Gọi 3 lần không nghe | Đỏ |

### Giai đoạn điều trị (trên hồ sơ bệnh nhân)

| Giai đoạn | Ý nghĩa |
|---|---|
| **Tư vấn** | BN mới, đang tư vấn |
| **IVF** | Đang điều trị IVF |
| **IUI** | Đang điều trị IUI |
| **Thai kỳ** | Beta đậu, đang mang thai |
| **Hoàn thành** | Điều trị xong, không cần CS nữa |
| **Sảy thai** | Ca sảy — ngừng CS thai kỳ |
| **Lưu thai** | Ca lưu — ngừng CS thai kỳ |

### Trạng thái duyệt (trên CS beta-thai)

| Trạng thái | Khi nào dùng |
|---|---|
| **Chưa duyệt** | NV lập danh sách, chờ quản lý duyệt |
| **Đã duyệt** | Quản lý đã kiểm tra, cho phép gọi |
| **Từ chối** | Quản lý không đồng ý, cần xem lại |

---

## Hỗ trợ kỹ thuật

Nếu gặp sự cố hoặc cần hỗ trợ, liên hệ:
- **FixPartner:** Qua Zalo nhóm hỗ trợ (đã được mời)
- **Giờ hỗ trợ:** 8h–18h, thứ 2–thứ 6
