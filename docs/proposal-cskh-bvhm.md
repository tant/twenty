# Đề xuất giải pháp hệ thống quản lý chăm sóc khách hàng

**Bệnh viện Hỗ trợ Sinh sản & Nam học Sài Gòn**

---

**Đơn vị thực hiện:** FixPartner
**Ngày:** 27/03/2026
**Phiên bản:** 2.0

---

## 1. Bối cảnh & vấn đề hiện tại

### 1.1. Quy trình hiện tại

Phòng Chăm sóc khách hàng (CSKH) đang quản lý 6 quy trình chính hoàn toàn bằng Excel/Google Drive:

| # | Quy trình | Nguồn dữ liệu | Thao tác hiện tại |
|---|-----------|---------------|-------------------|
| 1 | CS nội trú | HIS → Báo cáo nội trú | Xuất Excel → xóa cột → copy PID → fill ngày, BS, phòng → gọi |
| 2 | CS CBNM | HIS → Báo cáo tiếp đón | Xuất Excel → lọc PID → kéo hàm → fill thuốc từ IMS → gọi |
| 3 | Nhắc hẹn thủ thuật | Lịch PHS qua Zalo | Nhập PID thủ công → fill giờ từ Zalo → gọi |
| 4 | Gọi tái khám | HIT → Lịch hẹn KH | Xuất Excel → đối soát 4-5 file (IMS, HIT, sheet IUI/IVF/CBNM) → gọi |
| 5 | CS beta-thai | File IUI/IVF trên Drive | Nhập liệu ca bơm/chuyển phôi → đối soát → gửi quản lý duyệt → gọi |
| 6 | CS thai kỳ | Kết quả beta | Theo dõi thủ công, gọi mỗi tháng 1 lần |

### 1.2. Các điểm nghẽn chính

- **Thao tác thủ công nhiều:** Mỗi ngày nhân viên phải đăng nhập HIS/HIT/IMS, xuất Excel, copy-paste qua Google Drive, xóa cột, kéo hàm, fill thuốc. Riêng quy trình tái khám mất 6 bước đối soát.
- **Dữ liệu phân tán:** Thông tin bệnh nhân nằm rải rác trên HIS, HIT, IMS, Google Sheets — dễ sót hoặc sai lệch.
- **Đối soát tốn thời gian:** Quy trình tái khám cần đối soát chéo giữa 4-5 nguồn dữ liệu để đảm bảo không thiếu bệnh nhân.
- **Thiếu báo cáo tổng quan:** Quản lý không nắm được tình hình chăm sóc tổng thể, tỷ lệ gọi thành công, khối lượng công việc từng nhân viên.

---

## 2. Giải pháp đề xuất

Xây dựng **hệ thống quản lý chăm sóc khách hàng (CRM)** chuyên biệt cho bệnh viện, tập trung toàn bộ dữ liệu bệnh nhân và công việc chăm sóc về một nền tảng duy nhất, tuỳ biến hoàn toàn cho quy trình CSKH của BVHM.

### 2.1. Tổng quan hệ thống

Hệ thống gồm 2 thành phần:

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌───────────────────────────────────────────────────────┐     │
│   │              1. HỆ THỐNG CRM                          │     │
│   │                                                       │     │
│   │  NV CSKH sử dụng hàng ngày:                          │     │
│   │  • Hồ sơ bệnh nhân (32 fields)                       │     │
│   │  • Công việc chăm sóc (15 fields + Assignee)          │     │
│   │  • 6 View theo loại CS + Kanban                       │     │
│   │  • Dashboard báo cáo (8 biểu đồ)                     │     │
│   │  • Chu kỳ điều trị, Lần nhập viện                     │     │
│   │  • 3 Workflows tự động (thai kỳ, cảnh báo quá hạn)   │     │
│   └───────────────────────┬───────────────────────────────┘     │
│                           │                                     │
│                    tạo/cập nhật                                  │
│                    Person + Task                                │
│                           │                                     │
│   ┌───────────────────────┴───────────────────────────────┐     │
│   │          2. MODULE TÍCH HỢP DỮ LIỆU                  │     │
│   │             (chạy tự động mỗi ngày 6:00 sáng)         │     │
│   │                                                       │     │
│   │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐     │     │
│   │  │ HIS         │ │ HIT         │ │ IMS         │     │     │
│   │  │ Connector   │ │ Connector   │ │ Connector   │     │     │
│   │  │ (nội trú,   │ │ (tái khám,  │ │ (thuốc)     │     │     │
│   │  │  BN mới)    │ │  beta-thai) │ │             │     │     │
│   │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘     │     │
│   └─────────┼───────────────┼───────────────┼─────────────┘     │
│             │               │               │                   │
└─────────────┼───────────────┼───────────────┼───────────────────┘
              │               │               │
         ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
         │   HIS   │     │   HIT   │     │   IMS   │
         │ Bệnh   │     │ Lịch    │     │ Thuốc & │
         │ viện    │     │ hẹn     │     │ liệu    │
         │         │     │         │     │ trình    │
         └─────────┘     └─────────┘     └─────────┘
              Hệ thống hiện có của bệnh viện
```

**Thành phần 1 — Hệ thống CRM:** Giao diện NV CSKH sử dụng hàng ngày để xem danh sách bệnh nhân, gọi điện, ghi chú, theo dõi tiến độ, xem báo cáo.

**Thành phần 2 — Module tích hợp dữ liệu:** Chạy tự động mỗi sáng, đọc dữ liệu từ HIS/HIT/IMS → tạo hồ sơ bệnh nhân và công việc CS trên CRM. NV không cần xuất Excel hay nhập liệu thủ công (trừ CS thủ thuật — nguồn từ Zalo).

---

## 3. Các chức năng chính

### 3.1. Quản lý hồ sơ bệnh nhân

Tập trung toàn bộ thông tin bệnh nhân trên một nền tảng với **32 trường dữ liệu chuyên biệt:**

| Nhóm | Các trường |
|------|-----------|
| **Định danh** | PID, năm sinh, ngày sinh, giới tính, CCCD |
| **Nguồn BN** | Nguồn (Marketing/BV/BS hợp tác), đối tác giới thiệu |
| **Y khoa** | Chẩn đoán, thuốc đang dùng, chu kỳ hiện tại, kết quả beta, giai đoạn điều trị, trigger (thuốc kích) |
| **Điều trị** | Ngày bơm IUI, ngày chuyển phôi, lý do hủy chu kỳ, ngày tiếp đón, số ngày điều trị |
| **Liên hệ** | Người liên hệ, SĐT liên hệ |
| **Vợ/chồng** | Tên, PID, SĐT vợ/chồng (tra cứu chéo) |
| **Phân công** | Phòng khám, BS phụ trách |
| **Bảo hiểm** | Số BHYT, nhóm máu |
| **Thai sản** | Ngày dự sinh, tuần thai |
| **Thông tin bé** (khoa Sản) | Ngày sinh bé, giới tính bé, cân nặng bé |

### 3.2. Quản lý công việc chăm sóc

Mỗi công việc CS = 1 việc cần gọi cho 1 bệnh nhân, với **15 trường dữ liệu:**

- **Phân loại:** Loại chăm sóc (6 loại), loại lịch hẹn (7 loại)
- **Lịch hẹn:** Giờ hẹn, giờ có mặt, ngày nhắc, mã khám
- **Liên lạc:** Trạng thái gọi (Chưa gọi / Đã gọi / Cần gọi lại / Không liên lạc), ghi chú chăm sóc, ghi chú, lưu ý
- **Y khoa:** Lời dặn BS, thuốc, BS phụ trách, phòng khám
- **Duyệt:** Trạng thái duyệt (cho beta-thai)
- **Assignee:** NV CSKH nào phụ trách task (field có sẵn)

### 3.3. Bảy view chuyên biệt

| View | Lọc theo | Mục đích |
|------|---------|----------|
| CS nội trú | careType = Nội trú | BN vừa xuất viện |
| CS CBNM | careType = CBNM | BN mới đến khám |
| CS thủ thuật | careType = Thủ thuật | Nhắc lịch thủ thuật |
| CS tái khám | careType = Tái khám | Lịch tái khám |
| CS beta-thai | careType = Beta-thai | Theo dõi kết quả beta |
| CS thai kỳ | careType = Thai kỳ | Chăm sóc thai kỳ hàng tháng |
| **CS theo trạng thái** | Kanban theo trạng thái gọi | Tổng quan: kéo thả task giữa cột |

### 3.4. Dashboard báo cáo CSKH

8 biểu đồ dành cho quản lý:

| Biểu đồ | Ý nghĩa |
|----------|---------|
| Tổng bệnh nhân | Số BN trong hệ thống |
| Tổng công việc CS | Tổng task đã tạo |
| Chưa gọi | Số task chưa xử lý |
| Công việc theo loại CS | Phân bổ: Nội trú / CBNM / Thủ thuật / Tái khám / Beta / Thai kỳ |
| Trạng thái cuộc gọi | Đã gọi / Chưa gọi / Cần gọi lại / Không liên lạc |
| BN theo giai đoạn điều trị | IVF / IUI / Thai kỳ / Hoàn thành / Sảy-Lưu |
| Công việc CS theo thời gian | Xu hướng theo tuần |
| Khối lượng CS theo nhân viên | Cân bằng khối lượng giữa NV |

### 3.5. Các chức năng bổ sung

| Chức năng | Mô tả |
|-----------|-------|
| **Ghi chú chăm sóc** | Ghi kết quả liên lạc trên công việc CS (VD: "09:54 ĐÃ GỌI", "KNM, đã nhắn Zalo") + Ghi chú bổ sung + Lưu ý |
| **Chu kỳ điều trị** | Theo dõi IUI/IVF: loại, trạng thái, BS, ngày thủ thuật, kết quả beta |
| **Lần nhập viện** | Lịch sử nội trú: loại khoa, ngày nhập/xuất, BS, phòng |
| **11 Khoa/PK** | Khoa HTSS, Phụ sản, Nam khoa, 7 PK bác sĩ, PK hành chính |
| **3 Workflows** | Thai kỳ Auto-Create, Thai kỳ Recurring, Cảnh báo quá hạn |
| **Sidebar tiếng Việt** | Toàn bộ menu và nhãn tiếng Việt có dấu |

---

## 4. Phạm vi công việc & kế hoạch bàn giao

### 4.1. Phạm vi bàn giao

| # | Hạng mục | Mô tả |
|---|----------|-------|
| 1 | **Hệ thống CRM production** | Triển khai, cấu hình đầy đủ các chức năng tại mục 3, sẵn sàng sử dụng |
| 2 | **Module tích hợp HIS/HIT/IMS** | Tự động đồng bộ bệnh nhân, lịch hẹn, thuốc, tạo công việc CS |
| 3 | **Tài khoản người dùng** | Admin + Quản lý + NV CSKH (5-7 tài khoản) |
| 4 | **Tài liệu hướng dẫn sử dụng** | Hướng dẫn chi tiết cho NV CSKH (bản điện tử) |
| 5 | **Đào tạo trực tiếp** | 1 buổi tại bệnh viện (~90 phút) |
| 6 | **Hỗ trợ vận hành song song** | 1-2 tuần sau đào tạo |
| 7 | **Sao lưu tự động** | Cấu hình backup hàng ngày, giữ 30 bản |
| 8 | **Mã nguồn** | Toàn bộ mã nguồn hệ thống + tài liệu kỹ thuật |

### 4.2. Triển khai production

Tạo hệ thống mới hoàn toàn cho production:

```
Bước 1: Dựng hệ thống CRM trên server FixPartner
Bước 2: Cấu hình chuyên biệt cho BVHM
        → 32 fields BN, 15 fields Task, 7 views, 11 Khoa/PK,
          2 custom objects, 3 workflows, dashboard, sidebar tiếng Việt
Bước 3: Tạo tài khoản cho nhân viên
Bước 4: Cấu hình sao lưu tự động
Bước 5: Sẵn sàng sử dụng
```

**Thời gian triển khai:** Trong ngày

### 4.3. Tài khoản & phân quyền

| Vai trò | Quyền | Số lượng |
|---------|-------|----------|
| **Admin** | Tạo/quản lý tài khoản, cấu hình hệ thống | 1 (FixPartner hoặc IT BV) |
| **Quản lý** | Xem tất cả dữ liệu, duyệt beta-thai, xem dashboard | 1 (Trưởng phòng CSKH) |
| **Nhân viên** | Xem tất cả dữ liệu, tạo/cập nhật task, ghi chú | 3-5 (NV CSKH) |

Chức năng tự đăng ký tài khoản bị tắt — tất cả tài khoản do Admin tạo.

### 4.4. Đào tạo

**1 buổi trực tiếp** tại bệnh viện (~90 phút):

| Thời lượng | Nội dung | Đối tượng |
|------------|----------|-----------|
| 15 phút | Đăng nhập, giới thiệu giao diện | Tất cả |
| 30 phút | Tạo công việc CS, gọi BN, cập nhật trạng thái, ghi chú | NV CSKH |
| 15 phút | Kanban, lọc/sắp xếp, tìm kiếm BN | NV CSKH |
| 15 phút | Dashboard báo cáo, duyệt beta-thai | Quản lý |
| 15 phút | Quản lý tài khoản, hỏi đáp | Tất cả |

Kèm tài liệu hướng dẫn sử dụng chi tiết (bản điện tử).

### 4.5. Vận hành song song

**1-2 tuần** sau đào tạo, NV chạy song song CRM + Excel:

| Tuần | Mô tả |
|------|-------|
| **Tuần 1** | Nhập liệu cả Excel và CRM — làm quen, so sánh kết quả |
| **Tuần 2** | Chuyển chính sang CRM, chỉ dùng Excel kiểm tra chéo khi cần |
| **Sau tuần 2** | Ngừng Excel, dùng CRM hoàn toàn |

**Tiêu chí ngừng Excel:**
- 100% NV CSKH đăng nhập CRM mỗi ngày
- Tất cả task được tạo và cập nhật trên CRM
- Quản lý xác nhận dashboard phản ánh đúng thực tế

### 4.6. Tiến độ tổng thể

| GĐ | Giai đoạn | Thời gian | Mô tả |
|----|-----------|-----------|-------|
| **1** | **Khảo sát & mapping dữ liệu** | 1-2 tuần | BA làm việc với NV CSKH, review quy trình thực tế, mapping chính xác các trường dữ liệu HIS/HIT/IMS → CRM |
| **2** | **Phát triển & tích hợp** | 3-4 tuần | Xây dựng hệ thống CRM + module tích hợp HIS/HIT/IMS, chạy thử trên môi trường thử nghiệm |
| **3** | **Triển khai & vận hành thử** | 2-3 tuần | Triển khai production, đào tạo, vận hành song song CRM + Excel, nghiệm thu |

**Tổng thời gian: ~6-9 tuần**

---

## 5. Tích hợp HIS/HIT/IMS — Module đồng bộ dữ liệu

### 5.1. Mục tiêu

Xây dựng module tự động lấy dữ liệu từ HIS/HIT/IMS → tạo hồ sơ bệnh nhân và công việc CS trên CRM, **thay thế hoàn toàn** thao tác xuất Excel, copy-paste, fill, đối soát thủ công.

### 5.2. Ba giai đoạn triển khai

#### Giai đoạn 1 — Khảo sát & mapping dữ liệu (1-2 tuần)

**Nhân sự:** BA (Business Analyst) của FixPartner + 1-2 NV CSKH của bệnh viện

| # | Công việc | Đầu ra |
|---|-----------|--------|
| 1.1 | Ngồi cùng NV CSKH, quan sát quy trình thực tế hàng ngày | Tài liệu quy trình chi tiết (as-is) |
| 1.2 | Khảo sát HIS/HIT/IMS: xác định API hoặc phương thức xuất dữ liệu | Báo cáo kỹ thuật: có API hay chỉ xuất file |
| 1.3 | Lấy file mẫu thực tế từ HIS/HIT, đối chiếu cột dữ liệu | Bảng mapping chi tiết: cột Excel → field CRM |
| 1.4 | Xác nhận logic nghiệp vụ: loại trừ, đối soát, hạn CS | Tài liệu quy tắc nghiệp vụ đã được NV xác nhận |

**Kết quả giai đoạn 1:** Bảng mapping chính xác + quy tắc nghiệp vụ, đủ để phát triển module tích hợp.

#### Giai đoạn 2 — Phát triển module tích hợp (3-4 tuần)

**Nhân sự:** Đội kỹ thuật FixPartner

| # | Công việc | Mô tả |
|---|-----------|-------|
| 2.1 | Xây dựng hệ thống CRM | Cấu hình 32 fields BN, 15 fields Task, 7 views, dashboard, sidebar |
| 2.2 | Phát triển HIS Connector | Đọc dữ liệu nội trú + BN mới → tạo Person + Task (Nội trú, CBNM). Riêng khoa Phụ sản: tự tạo 2 task (CS ngày 1 + CS ngày 7-10 sau xuất viện) |
| 2.3 | Phát triển HIT Connector | Đọc lịch hẹn tái khám → tạo Task (Tái khám, Beta-thai), đối soát + loại trừ PK hành chính |
| 2.4 | Phát triển IMS Connector | Đọc thuốc theo PID → cập nhật Person.medication |
| 2.5 | Phát triển IUI/IVF Processor | Đọc file IUI/IVF → tạo Task Beta-thai (IUI+1 ngày, IVF+14 ngày sau ET) |
| 2.6 | Cấu hình Workflows | Activate: Thai kỳ Auto-Create, Thai kỳ Recurring, Cảnh báo quá hạn |
| 2.7 | Chạy thử trên môi trường test | So sánh kết quả với quy trình thủ công để đảm bảo chính xác |

**Hai chế độ tích hợp** (tùy kết quả khảo sát GĐ1):

| Chế độ | Khi nào | Cách hoạt động |
|--------|---------|----------------|
| **File Import** | HIS/HIT/IMS chỉ xuất được Excel/CSV | NV IT xuất file hàng ngày → đặt vào thư mục → module tự đọc & import |
| **API Direct** | HIS/HIT/IMS có API | Module gọi API trực tiếp, không cần can thiệp thủ công |

**Kết quả giai đoạn 2:** Hệ thống CRM hoàn chỉnh + module tích hợp, chạy ổn định trên môi trường thử nghiệm.

#### Giai đoạn 3 — Triển khai & vận hành thử (2-3 tuần)

| # | Công việc | Thời gian | Mô tả |
|---|-----------|-----------|-------|
| 3.1 | Triển khai production | Ngày 1 | Dựng hệ thống mới, cấu hình, tạo tài khoản |
| 3.2 | Đào tạo | Ngày 2 | 1 buổi trực tiếp tại bệnh viện (~90 phút) |
| 3.3 | Vận hành song song | Tuần 1-2 | NV dùng song song CRM + Excel, FixPartner hỗ trợ qua Zalo |
| 3.4 | Điều chỉnh | Trong tuần 1-2 | Sửa mapping, view, field nếu phát hiện sai lệch |
| 3.5 | Nghiệm thu | Cuối tuần 2 | Quản lý xác nhận, ký biên bản |

**Tiêu chí nghiệm thu:**
- Dữ liệu từ HIS/HIT/IMS đồng bộ chính xác vào CRM
- 100% NV CSKH sử dụng CRM hàng ngày
- Dashboard phản ánh đúng thực tế
- Không còn phụ thuộc Excel cho các quy trình CS

### 5.3. Module tích hợp — Chi tiết kỹ thuật

| Connector | Đầu vào (từ HIS/HIT/IMS) | Đầu ra (trên CRM) |
|-----------|--------------------------|---------------------|
| **HIS — Nội trú** | PID, tên, SĐT, ngày vào/xuất viện, phòng, BS, OR/ET/FET | Upsert Person + Tạo Task (Nội trú) + Tạo Lần nhập viện |
| **HIS — Tiếp đón** | PID, tên, SĐT, ngày khám, PK/BS | Upsert Person + Tạo Task (CBNM) |
| **HIT — Lịch hẹn** | PID, mã khám, ngày hẹn, PK, chẩn đoán, khung giờ | Upsert Person + Tạo Task (Tái khám hoặc Beta-thai) |
| **IMS — Thuốc** | PID, thuốc đang dùng, lý do hủy | Cập nhật Person.medication, Person.cancellationReason |
| **IUI/IVF** | PID, ngày bơm/ngày ET, BS, trạng thái | Upsert Chu kỳ điều trị + Tạo Task (Beta-thai) |

**Quy tắc nghiệp vụ (xác nhận lại ở GĐ1):**

| Quy tắc | Mô tả |
|---------|-------|
| Loại trừ phòng | Bỏ lịch hẹn Phòng hồ sơ, Cấp cứu, Hành chính |
| Đối soát | So sánh ngày hẹn HIT vs IMS → cảnh báo nếu không khớp |
| Hạn CS nội trú | Ngày xuất viện + 1 ngày |
| Hạn CS beta IUI | Ngày bơm + 1 ngày |
| Hạn CS beta IVF | Ngày chuyển phôi + 14 ngày |
| Ca hủy | Cập nhật lý do hủy, không tạo task mới |
| Chống trùng | Tìm theo PID + loại CS + ngày → không tạo task trùng |

**Lịch chạy:** Mỗi ngày lúc 6:00 sáng (trước giờ NV CSKH bắt đầu làm)

### 5.4. Yêu cầu hợp tác từ bệnh viện

| # | Yêu cầu | Giai đoạn |
|---|---------|-----------|
| 1 | Cử 1-2 NV CSKH làm việc cùng BA | GĐ1 |
| 2 | Cung cấp tài khoản HIS/HIT/IMS (hoặc file mẫu thực tế) | GĐ1 |
| 3 | Phối hợp IT để khảo sát API hoặc thống nhất quy trình xuất file | GĐ1 |
| 4 | Xác nhận bảng mapping và quy tắc nghiệp vụ | Cuối GĐ1 |
| 5 | Cử NV tham gia đào tạo và vận hành song song | GĐ3 |
| 6 | Trưởng phòng xác nhận nghiệm thu | Cuối GĐ3 |

---

## 6. Hạ tầng, vận hành & bảo mật

### 6.1. Hạ tầng & triển khai

- Hệ thống được **triển khai trên máy chủ của FixPartner**, đảm bảo hiệu năng và tính sẵn sàng cao.
- Nhân viên bệnh viện truy cập qua trình duyệt web, không cần cài đặt phần mềm.
- Nền tảng CRM chuyên biệt, cơ sở dữ liệu PostgreSQL, Redis.

### 6.2. Sao lưu & khôi phục

- **Sao lưu tự động** mỗi ngày lúc 2:00 sáng.
- Giữ **30 bản sao lưu** gần nhất.
- **Sao lưu thủ công** trước mỗi lần nâng cấp hệ thống.
- Kiểm tra khôi phục tối thiểu 1 lần/tháng.

### 6.3. Duy trì & hỗ trợ kỹ thuật

- FixPartner **chịu trách nhiệm duy trì, vận hành hệ thống** và xử lý sự cố kỹ thuật.
- Cập nhật, nâng cấp tính năng theo yêu cầu nghiệp vụ của bệnh viện.
- Hỗ trợ kỹ thuật qua Zalo nhóm hỗ trợ.

### 6.4. Cam kết bảo mật dữ liệu

**Bảo mật kỹ thuật:**
- Mã hóa toàn bộ kết nối bằng HTTPS/TLS
- Phân quyền truy cập theo vai trò — tài khoản do Admin tạo, không cho tự đăng ký
- Sao lưu dữ liệu tự động hàng ngày, lưu trữ tối thiểu 30 ngày
- Dữ liệu được lưu trữ trên máy chủ đặt tại Việt Nam

**Bảo mật vận hành:**
- Không chia sẻ, bán hoặc sử dụng dữ liệu bệnh nhân cho bất kỳ mục đích nào ngoài phạm vi hợp đồng
- Chỉ nhân sự kỹ thuật được ủy quyền của FixPartner mới có quyền truy cập ở cấp quản trị
- Cam kết thông báo cho bệnh viện trong vòng **72 giờ** khi phát hiện sự cố bảo mật
- Khi kết thúc hợp đồng, bàn giao toàn bộ dữ liệu và xóa sạch dữ liệu trên server

**Hỗ trợ quyền bệnh nhân:**
- Hệ thống là công cụ **nội bộ dành cho nhân viên** — bệnh nhân không trực tiếp truy cập
- Hỗ trợ tra cứu, chỉnh sửa và xóa dữ liệu để bệnh viện đáp ứng yêu cầu của bệnh nhân theo quy định pháp luật

### 6.5. Tuân thủ quy định pháp luật

| Văn bản | Nội dung liên quan |
|---------|-------------------|
| **Luật Bảo vệ Dữ liệu Cá nhân** (Luật 91/2025/QH15) | Khung pháp lý chính về bảo vệ DLCN |
| **Nghị định 356/2025/NĐ-CP** | Hướng dẫn chi tiết: DPIA, DPO, thời hạn phản hồi |
| **Luật An toàn Thông tin Mạng** (86/2015/QH13) | Yêu cầu bảo mật hệ thống thông tin |
| **Thông tư 46/2018/TT-BYT** | Quy định hồ sơ bệnh án điện tử |

**Phân định trách nhiệm:**
- Bệnh viện là **Bên kiểm soát dữ liệu** — chịu trách nhiệm pháp lý chính, bao gồm DPIA, DPO, thu thập sự đồng ý.
- FixPartner là **Bên xử lý dữ liệu** — cung cấp và vận hành hệ thống theo ủy quyền, cam kết không sử dụng dữ liệu cho mục đích riêng.
- Hai bên sẽ ký **Thỏa thuận Xử lý Dữ liệu Cá nhân (DPA)** theo Luật 91/2025.

---

## 7. Chi phí

### 7.1. Chi phí triển khai ban đầu

| # | Hạng mục | Giá trị (VNĐ) |
|---|----------|---------------|
| 1 | Phân tích dữ liệu, thiết kế hệ thống | 20.000.000 |
| 2 | Phát triển module tích hợp HIS/HIT/IMS | 40.000.000 |
| 3 | Thiết lập hệ thống CRM | 25.000.000 |
| 4 | Hỗ trợ hypercare & đào tạo | 15.000.000 |
| | **Tổng** | **100.000.000** |

### 7.2. Chi phí vận hành hàng tháng

| # | Hạng mục | Giá trị (VNĐ/tháng) |
|---|----------|---------------------|
| 1 | Server, hạ tầng | 900.000 |
| 2 | Sao lưu dữ liệu | 300.000 |
| 3 | Duy trì, hỗ trợ kỹ thuật | 800.000 |
| | **Tổng** | **2.000.000** |

### 7.3. Thanh toán

- **Triển khai:** 50% khi ký hợp đồng, 50% khi nghiệm thu
- **Vận hành:** Thanh toán 6 tháng/lần (12.000.000 VNĐ/kỳ)
- **Phát triển thêm:** Tính theo yêu cầu phát sinh ngoài phạm vi, báo giá riêng

---

## 8. Cam kết dịch vụ (SLA)

| Hạng mục | Cam kết |
|----------|---------|
| **Uptime hệ thống** | ≥ 99% (không tính thời gian bảo trì có thông báo trước) |
| **Thời gian phản hồi sự cố** | Sự cố nghiêm trọng (không truy cập được): ≤ 4 giờ trong giờ hành chính |
| **Thời gian khắc phục** | Sự cố nghiêm trọng: ≤ 24 giờ; Sự cố thường: ≤ 72 giờ |
| **Khung giờ hỗ trợ** | 8h–18h, thứ 2–thứ 6 (trừ lễ/Tết), qua Zalo/điện thoại |
| **Bảo trì định kỳ** | Thông báo trước tối thiểu 24 giờ, thực hiện ngoài giờ hành chính |
| **Sao lưu** | Tự động hàng ngày, giữ 30 bản, kiểm tra khôi phục 1 lần/tháng |

**Quy trình dự phòng khi hệ thống gián đoạn:**
- Nhân viên CSKH có thể tạm thời quay lại quy trình xuất Excel từ HIS/HIT
- FixPartner thông báo ngay khi có sự cố và cập nhật tiến độ khắc phục

**Bảo hành:** 3 tháng miễn phí sau nghiệm thu — bao gồm sửa lỗi, điều chỉnh cấu hình, hỗ trợ kỹ thuật.

---

## 9. Quyền sở hữu & chuyển giao

| Hạng mục | Chi tiết |
|----------|----------|
| **Dữ liệu** | Thuộc quyền sở hữu hoàn toàn của bệnh viện — có thể yêu cầu xuất toàn bộ bất kỳ lúc nào |
| **Mã nguồn** | Toàn bộ mã nguồn hệ thống và tài liệu kỹ thuật được bàn giao đầy đủ khi nghiệm thu |
| **Chuyển đổi** | Bệnh viện có thể tự vận hành hoặc chuyển sang đơn vị khác — FixPartner hỗ trợ bàn giao |
| **Kết thúc HĐ** | Bàn giao toàn bộ dữ liệu, mã nguồn, tài liệu. Xóa sạch dữ liệu trên server trong 30 ngày |

---

## 10. Yêu cầu hợp tác từ bệnh viện

Chi tiết theo từng giai đoạn xem tại mục 5.4. Tóm tắt:

| # | Yêu cầu | Giai đoạn |
|---|---------|-----------|
| 1 | Cử 1-2 NV CSKH làm việc cùng BA để review quy trình | GĐ1 — Khảo sát |
| 2 | Cung cấp tài khoản HIS/HIT/IMS hoặc file mẫu thực tế | GĐ1 — Khảo sát |
| 3 | Phối hợp IT để khảo sát API hoặc thống nhất quy trình xuất file | GĐ1 — Khảo sát |
| 4 | Xác nhận bảng mapping và quy tắc nghiệp vụ | Cuối GĐ1 |
| 5 | Chọn domain production (hoặc dùng domain FixPartner cung cấp) | GĐ3 — Triển khai |
| 6 | Cử NV tham gia đào tạo và vận hành song song | GĐ3 — Triển khai |
| 7 | Trưởng phòng xác nhận nghiệm thu | Cuối GĐ3 |

---

*FixPartner — Đối tác công nghệ đáng tin cậy*
