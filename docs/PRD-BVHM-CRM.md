# PRD: Hệ thống Quản lý Chăm sóc Bệnh nhân — BVHM

**Product:** BVHM CRM (dựa trên Twenty CRM)
**Khách hàng:** Bệnh Viện Hỗ Trợ Sinh Sản & Nam Học Sài Gòn
**Phiên bản:** 1.0
**Ngày:** 2026-03-26

---

## 1. Bối cảnh & Vấn đề

### 1.1 Về bệnh viện
BVHM là bệnh viện chuyên hỗ trợ sinh sản (IVF, IUI), sản khoa, nam khoa tại TP.HCM. Bệnh viện có ~100 nhân viên, 4 khoa chuyên môn và 7 phòng khám bác sĩ.

### 1.2 Vấn đề hiện tại
Phòng Chăm sóc Khách hàng (CSKH) đang quản lý bệnh nhân bằng Excel/sổ tay:
- **Sót bệnh nhân:** Không có hệ thống nhắc nhở, bệnh nhân sau thủ thuật/xuất viện có thể bị quên gọi
- **Không theo dõi được:** Ai đã gọi, ai chưa, kết quả gọi ra sao — không có nơi ghi nhận
- **Không phân loại:** Bệnh nhân nội trú, tái khám, thai kỳ... đều nằm chung, khó ưu tiên
- **Không lập báo cáo:** Trưởng phòng không biết team đã chăm sóc bao nhiêu BN, tỷ lệ liên lạc được

### 1.3 Giải pháp
Triển khai Twenty CRM (mã nguồn mở) được tuỳ biến cho quy trình chăm sóc bệnh nhân của BVHM. Không sửa code Twenty — toàn bộ tuỳ biến qua API bằng script Python.

---

## 2. Người dùng mục tiêu

| Vai trò | Số lượng | Công việc chính |
|---------|----------|-----------------|
| **Nhân viên CSKH** | 3-5 | Gọi điện bệnh nhân, ghi nhận kết quả, nhắc lịch hẹn |
| **Trưởng phòng CSKH** | 1 | Phân công, giám sát, duyệt beta-thai, xem báo cáo |

---

## 3. Quy trình làm việc hàng ngày

### 3.1 Buổi sáng — Xem dashboard & phân công
```
Trưởng phòng mở CRM
  → Xem Kanban "CS theo trạng thái" để biết tổng quan
  → Thấy cột "Chưa gọi" có 15 task (đã được tạo tự động từ HIS/HIT lúc 6:00 sáng)
  → Cột "Cần gọi lại" có 5 task từ hôm qua
  → Phân công: "Lan xử lý CS nội trú, Hoa xử lý CS tái khám"
```

### 3.2 Trong ngày — Nhân viên CSKH gọi bệnh nhân
```
Nhân viên Lan mở view "CS nội trú"
  → Thấy danh sách task đã được tạo tự động từ dữ liệu HIS
  → Click vào task "CS nội trú - Nguyễn Thị A - xuất viện sau ET"
  → Thấy: thuốc Progesterone 400mg, BS phụ trách: BS Cường
  → Gọi BN → Cập nhật:
      - Trạng thái gọi: "Đã gọi"
      - Ghi chú: "BN uống thuốc đều, hẹn 15/04 xét nghiệm beta"
```

### 3.3 Nhắc hẹn thủ thuật — Tạo thủ công
```
Nhân viên Lan nhận lịch thủ thuật PHS qua Zalo
  → Mở CRM view "CS thủ thuật" → Bấm "+ Bản ghi mới"
  → Nhập PID → Hệ thống tự hiển thị thông tin BN
  → Chọn loại lịch hẹn, nhập giờ hẹn, hạn chăm sóc
  → Gọi nhắc BN
```

> **Lưu ý:** CS thủ thuật là loại duy nhất cần tạo thủ công. Lịch thủ thuật do PHS (phòng hành chính) ban hành qua nhóm Zalo, không nằm trong HIS/HIT/IMS nên không thể tự động hóa. (Theo quy trình gốc của khách hàng: "Nhập PID từ lịch thủ thuật khi PHS ban hành lịch → Fill giờ PHS gửi trong gr zalo → Gọi nhắc hẹn")

### 3.4 Theo dõi thai kỳ — Không sót ai
```
Nhân viên Hoa mở view "CS thai kỳ"
  → Thấy BN Hồng - Tuần 20, BN Ngọc - Tuần 12
  → Gọi BN Hồng: "Chị ơi hẹn siêu âm hình thái tuần tới nhé"
  → Cập nhật: "Đã gọi" + ghi chú
  → Workflow tự tạo task mới cho lần gọi tháng sau
```

### 3.5 Cuối ngày — Trưởng phòng kiểm tra
```
Trưởng phòng xem Kanban
  → Cột "Chưa gọi" còn 3 task (giảm từ 15)
  → Cột "Không liên lạc được" có 2 BN → chuyển sang ngày mai
  → Xem Dashboard báo cáo: hôm nay team gọi 20 BN, liên lạc được 85%
```

---

## 4. Tính năng — Phase 1 (MVP)

### 4.1 Quản lý Bệnh nhân (Person)

**Mô tả:** Mỗi bệnh nhân là một record Person với đầy đủ thông tin y tế.

**32 custom fields:**

| Nhóm | Field | Loại | Mục đích |
|------|-------|------|----------|
| **Định danh** | PID | TEXT | Mã BN từ HIS, dùng để đối chiếu |
| | Năm sinh | NUMBER | Tính tuổi nhanh |
| | Ngày sinh | DATE | CS sinh nhật |
| | Giới tính | SELECT | Nam/Nữ |
| | CCCD | TEXT | Xác minh danh tính |
| **Nguồn BN** | Nguồn | SELECT | Marketing/BV/BS hợp tác/Khác |
| | Đối tác giới thiệu | TEXT | Tên đối tác |
| **Y khoa** | Chẩn đoán | TEXT | Chẩn đoán chính |
| | Thuốc đang dùng | TEXT | Từ IMS |
| | Chu kỳ hiện tại | TEXT | VD: "IVF lần 2" |
| | Kết quả Beta | TEXT | Số liệu beta HCG |
| | Giai đoạn điều trị | SELECT | IVF/IUI/Thai kỳ/Hoàn thành |
| | Trigger | TEXT | Loại thuốc kích (VD: Cetrotide) |
| **Điều trị** | Ngày bơm IUI | DATETIME | Lịch thủ thuật |
| | Ngày chuyển phôi | DATETIME | Lịch ET |
| | Lý do hủy | TEXT | Nếu hủy chu kỳ |
| | Ngày tiếp đón | DATE | Ngày đầu tiên đến khám (từ HIT) |
| | Số ngày điều trị | NUMBER | Tính từ ngày tiếp đón |
| **Liên hệ** | Người liên hệ | TEXT | Người thân |
| | SĐT liên hệ | TEXT | SĐT người thân |
| **Vợ/chồng** | Tên vợ/chồng | TEXT | Cho cặp vợ chồng cùng điều trị |
| | PID vợ/chồng | TEXT | Tra cứu chéo |
| | SĐT vợ/chồng | TEXT | Liên hệ |
| **Phân công** | Phòng khám | TEXT | PK phụ trách |
| | BS phụ trách | TEXT | Bác sĩ chính |
| **Bảo hiểm** | Số BHYT | TEXT | Số thẻ bảo hiểm y tế |
| | Nhóm máu | SELECT | A/B/AB/O |
| **Thai sản** | Ngày dự sinh | DATE | Cho BN mang thai |
| | Tuần thai | NUMBER | Tuần thai hiện tại |
| **Thông tin bé** (khoa Sản) | Ngày sinh bé | DATETIME | Ngày giờ sinh |
| | Giới tính bé | SELECT | Trai/Gái |
| | Cân nặng bé | NUMBER | Gram |

**Acceptance Criteria:**
- [x] Tất cả fields hiện trên form chi tiết bệnh nhân
- [x] Có thể tìm kiếm BN theo PID, tên, SĐT
- [x] BN được link với Khoa/PK (Company)

---

### 4.2 Quản lý Công việc Chăm sóc (Task)

**Mô tả:** Mỗi task = 1 việc cần làm cho 1 bệnh nhân. Nhân viên CSKH xử lý task hàng ngày.

**Cách tạo task:** Nhân viên tạo thủ công trên CRM dựa trên dữ liệu từ HIS/HIT/IMS/Zalo:

| Loại CS | Nguồn dữ liệu gốc | Cách tạo |
|---------|--------------------|----|
| Nội trú | HIS → Báo cáo nội trú (nhập/xuất viện) | Thủ công |
| CBNM | HIS → Báo cáo tiếp đón (BN mới) | Thủ công |
| Thủ thuật | Lịch PHS gửi qua nhóm Zalo | Thủ công |
| Tái khám | HIT → Báo cáo lịch hẹn KH + đối soát IMS | Thủ công |
| Beta-thai | File IUI/IVF trên Drive (ngày bơm IUI, 14 ngày sau ET) | Thủ công |
| Thai kỳ | Kết quả beta đậu → cập nhật giai đoạn "Thai kỳ" | Thủ công (mỗi tháng) |

> Khi tích hợp HIS (Phase 3), task sẽ được tạo tự động. Khi activate workflows (Phase 3), task thai kỳ recurring và cảnh báo quá hạn sẽ tự động.

**15 custom fields + Assignee (built-in):**

| Nhóm | Field | Loại | Mục đích |
|------|-------|------|----------|
| **Phân loại** | Loại chăm sóc | SELECT | 6 loại: Nội trú, CBNM, Thủ thuật, Tái khám, Beta-thai, Thai kỳ |
| | Loại lịch hẹn | SELECT | 7 loại: Tái khám, IUI, Lấy trứng, Chuyển phôi, Phẫu thuật, PRP, Sinh nhật |
| **Lịch hẹn** | Giờ hẹn | TEXT | VD: "08:00" |
| | Giờ có mặt | TEXT | VD: "07:30" |
| | Ngày nhắc | DATETIME | Khi nào nhắc BN |
| | Mã khám | TEXT | Mã từ HIS |
| **Liên lạc** | Trạng thái gọi | SELECT | Chưa gọi / Đã gọi / Cần gọi lại / Không liên lạc |
| | Ghi chú chăm sóc | TEXT | Kết quả liên lạc (VD: "09:54 ĐÃ GỌI NHẮC TÁI KHÁM" hoặc "KNM, đã nhắn SMS Zalo") |
| | Ghi chú | TEXT | Thông tin bổ sung về ca này |
| | Lưu ý | TEXT | Cảnh báo quan trọng cần chú ý khi gọi |
| **Y khoa** | Lời dặn BS | TEXT | BS ghi lời dặn |
| | Thuốc | TEXT | Thuốc tại thời điểm |
| | BS phụ trách | TEXT | Bác sĩ |
| | Phòng khám | TEXT | PK nào |
| **Duyệt** | Trạng thái duyệt | SELECT | Cho beta-thai: Chưa duyệt/Đã duyệt/Từ chối |

**Assignee (built-in):** Twenty Task có sẵn field Assignee — dùng để ghi **NV CSKH nào xử lý** task này. Quản lý có thể lọc/báo cáo theo NV.

**Acceptance Criteria:**
- Task luôn link với bệnh nhân (qua taskTarget)
- Task có due date để sắp xếp ưu tiên
- Trạng thái gọi cập nhật real-time trên Kanban
- Assignee cho biết NV nào phụ trách task

---

### 4.3 Bảy (7) View chuyên biệt

**Mô tả:** Mỗi loại chăm sóc có view riêng, filter sẵn, chỉ hiện columns cần thiết.

| # | View | Filter | Columns | Mục đích |
|---|------|--------|---------|----------|
| 1 | CS nội trú | careType=NOI_TRU | Title, BN, Call status, Due, Notes, Thuốc | BN vừa xuất viện |
| 2 | CS CBNM | careType=CBNM | Title, BN, BS, Thuốc, Call status, Notes | BN mới đến khám |
| 3 | CS thủ thuật | careType=THU_THUAT | Title, BN, Due, Call status, Notes | Nhắc lịch thủ thuật |
| 4 | CS tái khám | careType=TAI_KHAM | Title, BN, BS, Thuốc, Call status, Notes, Due | Lịch tái khám |
| 5 | CS beta-thai | careType=BETA_THAI | Title, BN, Due, Duyệt, Call status, Notes | Theo dõi kết quả beta |
| 6 | CS thai kỳ | careType=THAI_KY | Title, BN, Due, Call status, Notes | Chăm sóc thai kỳ |
| 7 | CS theo trạng thái | (none) | Kanban by callStatus | Tổng quan tiến độ |

**Acceptance Criteria:**
- [x] Mỗi view chỉ hiện task đúng loại
- [x] Kanban hiện 4 cột: Chưa gọi / Đã gọi / Cần gọi lại / Không liên lạc
- [x] Có thể kéo thả task giữa các cột Kanban

---

### 4.4 Cấu trúc Bệnh viện (Company)

**Mô tả:** 11 khoa/phòng khám của bệnh viện, seed sẵn.

| # | Tên | Nhân sự |
|---|-----|---------|
| 1 | Khoa HTSS | 30 |
| 2 | Khoa Phụ sản | 20 |
| 3 | Khoa Nam khoa | 10 |
| 4 | Phòng khám hành chính | 15 |
| 5-11 | 7 PK Bác sĩ | 3-5 mỗi PK |

**Acceptance Criteria:**
- [x] BN được gắn với Khoa/PK
- [x] Có thể filter BN theo Khoa

---

### 4.5 Sidebar

**Menu chính:**

```
├── Các Khoa           → 11 khoa/phòng khám
├── Bệnh nhân          → Hồ sơ bệnh nhân
├── Công việc CS        → Danh sách việc cần làm (6 view + Kanban)
├── Báo cáo            → Dashboard CSKH (8 biểu đồ)
├── Quy trình           → Workflows tự động
├── Chu kỳ điều trị     → Theo dõi IUI/IVF
└── Lần nhập viện       → Lịch sử nội trú
```

### 4.6 Tài khoản & Phân quyền

**3 loại tài khoản:**

| Vai trò | Quyền | Ghi chú |
|---------|-------|---------|
| **Admin** | Tạo/quản lý tài khoản, cấu hình hệ thống, xem tất cả dữ liệu | Chỉ FixPartner hoặc IT bệnh viện |
| **Quản lý** | Xem tất cả dữ liệu, duyệt beta-thai, xem dashboard báo cáo | Trưởng phòng CSKH |
| **Nhân viên** | Xem tất cả dữ liệu, tạo/cập nhật task, ghi chú | NV CSKH |

**Quy tắc hiện tại:**
- Quản lý và Nhân viên có **quyền sử dụng giống nhau** (chưa phân quyền chi tiết)
- Chỉ Admin mới có quyền vào Settings → tạo/xóa tài khoản
- Chức năng **tự đăng ký tài khoản bị tắt** — tất cả tài khoản do Admin tạo

**Tài khoản cần tạo khi go-live:**

| # | Email | Vai trò | Người dùng |
|---|-------|---------|------------|
| 1 | admin@bvhmsg.com | Admin | IT bệnh viện / FixPartner |
| 2 | quanly@bvhmsg.com | Quản lý | Trưởng phòng CSKH |
| 3-7 | nv1@bvhmsg.com ... | Nhân viên | 3-5 NV CSKH |

> **Tương lai:** Khi có yêu cầu phân quyền chi tiết (VD: NV chỉ thấy task được assign cho mình), sẽ cấu hình qua Twenty's role-based access control.

---

## 5. Tính năng nâng cao

### 5.1 Workflows tự động

| # | Workflow | Trigger | Action | Status |
|---|---------|---------|--------|--------|
| 1 | Thai Kỳ Auto-Create | Person.treatmentStage đổi → "THAI_KY" | Tạo Task careType=THAI_KY, hạn = hôm nay + 30 ngày | Draft |
| 2 | Thai Kỳ Recurring | Task (THAI_KY) có callStatus đổi → "DA_GOI" | Tạo Task THAI_KY mới, hạn = hôm nay + 30 ngày | Draft |
| 3 | Cảnh báo quá hạn | Cron: mỗi ngày 8:00 | Tìm Task có dueAt < hôm nay & callStatus ≠ DA_GOI → tạo cảnh báo | Draft |

**Note:** Workflows tạo ở trạng thái draft. Cần cấu hình trigger + steps qua UI workflow builder của Twenty rồi activate.

**Phân ranh giới tạo Task — Data Sync vs Workflow:**

```
Dữ liệu bên ngoài (HIS/HIT/IMS)          Sự kiện bên trong CRM
         │                                          │
         ▼                                          ▼
┌─────────────────────┐              ┌─────────────────────────┐
│  DATA SYNC SERVICE  │              │  TWENTY WORKFLOW ENGINE  │
│  (Python, cron 6AM) │              │  (built-in, real-time)   │
├─────────────────────┤              ├─────────────────────────┤
│ Tạo Task:           │              │ Tạo Task:               │
│  • Nội trú          │              │  • Thai kỳ (auto-create) │
│  • CBNM             │              │  • Thai kỳ (recurring)   │
│  • Tái khám         │              │                          │
│  • Beta-thai        │              │ Cảnh báo:                │
│                     │              │  • Task quá hạn          │
│ Cập nhật Person:    │              │                          │
│  • Thuốc, giai đoạn │──triggers──▶│ Giai đoạn → THAI_KY      │
│  • Ngày thủ thuật   │              │  → auto-create task      │
└─────────────────────┘              └─────────────────────────┘
         │
         ✗ KHÔNG tạo: Thủ thuật (nguồn Zalo, luôn thủ công)
```

| Loại CS | Ai tạo Task | Nguồn dữ liệu |
|---------|-------------|----------------|
| **Nội trú** | Data Sync | HIS → báo cáo nội trú |
| **CBNM** | Data Sync | HIS → báo cáo tiếp đón |
| **Tái khám** | Data Sync | HIT → lịch hẹn KH |
| **Beta-thai** | Data Sync | File IUI/IVF (ngày bơm, ngày ET) |
| **Thai kỳ** | Workflow #1 + #2 | Sự kiện: giai đoạn đổi → THAI_KY, hoặc hoàn thành gọi |
| **Thủ thuật** | Thủ công (NV CSKH) | Lịch PHS qua Zalo |

### 5.2 Custom Objects

| Object | Fields | Relation |
|--------|--------|----------|
| **Chu kỳ điều trị** | 9 fields: Loại (IUI/IVF/CBNM/PRP), trạng thái, BS, ngày bắt đầu, ngày thủ thuật, ngày beta, kết quả beta, lý do hủy, ghi chú | MANY_TO_ONE → Bệnh nhân |
| **Lần nhập viện** | 10 fields: Loại (HTSS/PT-TT/Sản), ngày nhập/xuất, loại thủ thuật, BS, phòng, hài lòng, ghi chú, **OR Ngày 3**, **OR Ngày 5** | MANY_TO_ONE → Bệnh nhân |

**CS nội trú khoa Phụ sản — 2 task tự động:**

Khoa Phụ sản có quy trình CS 2 lần sau xuất viện (theo file thực tế của khách):

| Task | Hạn CS | Nội dung |
|------|--------|---------|
| CS sau xuất viện 1 ngày | Ngày xuất + 1 | Chăm sóc mẹ & bé sau 1 ngày xuất viện |
| CS 7-10 ngày sau xuất viện | Ngày xuất + 7 | Hỏi thăm sức khỏe, kết quả sàng lọc sơ sinh |

Data Sync tự tạo **2 task riêng** khi đọc dữ liệu nhập viện khoa Phụ sản (loại = "Sản").

### 5.3 Dashboard "Báo cáo CSKH"

| Widget | Loại | Dữ liệu |
|--------|------|---------|
| Tổng bệnh nhân | KPI | COUNT(person) |
| Tổng công việc CS | KPI | COUNT(task) |
| Chưa gọi | KPI | COUNT_EMPTY(callStatus) |
| Công việc theo loại chăm sóc | Pie chart | GROUP BY careType |
| Trạng thái cuộc gọi | Bar chart | GROUP BY callStatus |
| BN theo giai đoạn điều trị | Pie chart | GROUP BY treatmentStage |
| Công việc CS theo thời gian | Line chart | GROUP BY dueAt (weekly) |
| Khối lượng CS theo nhân viên | Bar chart | GROUP BY createdBy.name |

### 5.4 Module tích hợp dữ liệu — Data Sync Service (Phase 3)

**Mục tiêu:** Tự động lấy dữ liệu từ HIS/HIT/IMS → tạo/cập nhật hồ sơ Bệnh nhân và Công việc CS trên CRM, thay thế toàn bộ thao tác thủ công (xuất Excel, copy-paste, fill, đối soát).

**Phạm vi:** Data Sync chịu trách nhiệm tạo Task từ **dữ liệu bên ngoài** (Nội trú, CBNM, Tái khám, Beta-thai). Task từ **sự kiện bên trong CRM** (Thai kỳ auto-create, recurring) do Workflow engine xử lý (xem mục 5.1). Task **Thủ thuật** luôn tạo thủ công (nguồn Zalo).

#### 5.4.1 Kiến trúc tổng quan

```
┌──────────────────────────────────────────────────────────────────┐
│                     DATA SYNC SERVICE                            │
│                  (Python, chạy định kỳ via cron)                 │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ HIS         │  │ HIT         │  │ IMS         │              │
│  │ Connector   │  │ Connector   │  │ Connector   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         ▼                ▼                ▼                      │
│  ┌──────────────────────────────────────────────┐                │
│  │              Transform & Validate             │                │
│  │  - Chuẩn hóa PID (key chính)                 │                │
│  │  - Mapping fields HIS→CRM                    │                │
│  │  - Đối soát chéo (HIT vs IMS)                │                │
│  │  - Loại trừ (PK hành chính, ca hủy)          │                │
│  └──────────────────┬───────────────────────────┘                │
│                     ▼                                            │
│  ┌──────────────────────────────────────────────┐                │
│  │              CRM Writer                       │                │
│  │  - Upsert Person (tạo mới / cập nhật)        │                │
│  │  - Create Task (tránh trùng lặp)             │                │
│  │  - Log kết quả & cảnh báo                    │                │
│  └──────────────────┬───────────────────────────┘                │
│                     │                                            │
└─────────────────────┼────────────────────────────────────────────┘
                      ▼
               Twenty CRM API
            (REST / GraphQL)
```

#### 5.4.2 Hai chế độ vận hành

| Chế độ | Khi nào | Cách hoạt động |
|--------|---------|----------------|
| **File Import** (ưu tiên, khả thi ngay) | HIS/HIT/IMS chỉ xuất được Excel/CSV | NV IT xuất file hàng ngày → đặt vào thư mục chỉ định → Service tự đọc & import |
| **API Direct** (lý tưởng) | HIS/HIT/IMS có API | Service gọi API trực tiếp, không cần can thiệp thủ công |

> **Thực tế:** Phần lớn HIS tại Việt Nam (eHospital, Viettel HIS, FPT.eHospital) chỉ hỗ trợ xuất báo cáo → chế độ File Import sẽ là phương án chính.

#### 5.4.3 Connector chi tiết

##### A. HIS Connector — Bệnh nhân nội trú + Bệnh nhân mới

**Nguồn dữ liệu gốc (từ quy trình hiện tại):**
- HIS → Phân hệ báo cáo thống kê → Báo cáo nội trú → Thống kê tình hình nội trú → Xuất Excel
- HIS → Báo cáo tiếp đón → Xuất Excel

**Đầu vào (Excel từ HIS):**

| Cột | Ví dụ | Mapping → CRM |
|-----|-------|---------------|
| PID | `26005816` | Person.pid |
| TÊN NB | `VÕ THỊ LOAN` | Person.name.firstName + lastName |
| NĂM SINH | `1988` | Person.yearOfBirth |
| GIỚI TÍNH | `Nữ` | Person.gender |
| SĐT | `0901234567` | Person.phones |
| ĐỊA CHỈ | `Q.7, TP.HCM` | Person.city |
| NGUỒN | `MKT` | Person.patientSource |
| ĐỐI TÁC | `BS Nguyễn` | Person.referralPartner |
| BS THỰC HIỆN | `BS Cường` | Person.doctorName, Task.doctorName |
| NGÀY VÀO VIỆN | `2026-03-20` | InpatientStay.admissionDate |
| NGÀY XUẤT VIỆN | `2026-03-22` | InpatientStay.dischargeDate |
| PHÒNG BỆNH | `P.301` | InpatientStay.room |
| OR/ET/FET | `x` | InpatientStay.procedureType |

**Đầu ra → CRM:**

| Action | Object | Điều kiện |
|--------|--------|-----------|
| Upsert Person | Bệnh nhân | Tìm theo PID. Nếu chưa có → tạo mới. Nếu có → cập nhật SĐT, địa chỉ |
| Create InpatientStay | Lần nhập viện | Link với Person. Tránh trùng bằng PID + ngày vào viện |
| Create Task (careType=NOI_TRU) | Công việc CS | Tiêu đề: "CS nội trú - {tên} - Xuất viện {ngày}". Hạn CS = ngày xuất viện + 1 |
| Create Task (careType=CBNM) | Công việc CS | Từ báo cáo tiếp đón: "CS CBNM - {tên} - Khám {ngày}". Hạn CS = ngày khám + 1 |

**Lịch chạy:** Mỗi ngày 1 lần, lúc 6:00 sáng (trước giờ NV CSKH bắt đầu làm)

---

##### B. HIT Connector — Lịch hẹn tái khám

**Nguồn dữ liệu gốc (từ quy trình hiện tại):**
- HIT → Phân hệ báo cáo thống kê → Báo cáo multi người dùng → Báo cáo lịch hẹn KH → Xuất Excel

**Đầu vào (Excel từ HIT):**

| Cột | Ví dụ | Mapping → CRM |
|-----|-------|---------------|
| PID | `26005816` | Lookup Person |
| Mã khám | `26005816` | Task.examCode |
| Tên người bệnh | `VÕ THỊ LOAN` | Verify against Person |
| Ngày hẹn | `2026-03-18` | Task.dueAt |
| Nội dung | `TÁI KHÁM 18/03` | Task.title (bổ sung) |
| Phòng khám | `PK BSCKII. Hồ Cao Cường` | Task.clinic |
| Chẩn đoán | `HIẾM MUỘN II` | Person.diagnosis |
| Ngày nhắc lịch | `2026-03-17` | Task.reminderDate |
| KHUNG GIỜ KHÁM | `9-10h` | Task.appointmentTime |

**Xử lý đặc biệt — Đối soát & loại trừ:**

| Quy tắc | Mô tả |
|---------|-------|
| Loại trừ phòng | Bỏ lịch hẹn có Phòng khám = "Phòng hồ sơ", "Cấp cứu", "Hành chính" |
| Đối soát IMS | So sánh ngày hẹn HIT vs IMS → cảnh báo nếu không khớp |
| Phát hiện beta/thai | Nếu nội dung chứa "beta" hoặc "thai" → careType=BETA_THAI thay vì TAI_KHAM |

**Đầu ra → CRM:**

| Action | Object | Điều kiện |
|--------|--------|-----------|
| Upsert Person | Bệnh nhân | Cập nhật chẩn đoán, phòng khám nếu thay đổi |
| Create Task (careType=TAI_KHAM) | Công việc CS | Tiêu đề: "CS tái khám - {tên} - {ngày hẹn}". Tránh trùng bằng PID + ngày hẹn |
| Create Task (careType=BETA_THAI) | Công việc CS | Nếu phát hiện là ca beta/thai |
| Create Alert | Cảnh báo | Khi HIT vs IMS không khớp ngày hẹn |

**Lịch chạy:** Mỗi ngày 1 lần, lúc 6:00 sáng (lấy lịch hẹn ngày mai để NV nhắc trước 1 ngày)

---

##### C. IMS Connector — Thuốc & liệu trình

**Nguồn dữ liệu gốc (từ quy trình hiện tại):**
- IMS → Tra cứu theo PID → Lấy thuốc đang dùng, thời gian tiêm/uống

**Đầu vào:**

| Cột | Ví dụ | Mapping → CRM |
|-----|-------|---------------|
| PID | `26005816` | Lookup Person |
| Thuốc | `Progesterone 400mg` | Person.medication |
| Thời gian tiêm thuốc | `Ngày 3-5-7` | TreatmentCycle.notes |
| Trigger | `Cetrotide` | TreatmentCycle.notes |
| Lý do hủy | `BN không đồng ý` | Person.cancellationReason |

**Đầu ra → CRM:**

| Action | Object | Điều kiện |
|--------|--------|-----------|
| Update Person.medication | Bệnh nhân | Cập nhật thuốc đang dùng mới nhất |
| Update Person.cancellationReason | Bệnh nhân | Nếu có lý do hủy → tự đánh dấu, task không cần gọi nữa |

**Lịch chạy:** Mỗi ngày 1 lần, hoặc theo yêu cầu (NV bấm nút "Sync thuốc")

---

#### 5.4.4 Xử lý dữ liệu IUI/IVF (beta-thai)

**Đây là quy trình phức tạp nhất.** Khác với nội trú/tái khám (xuất từ HIS/HIT), dữ liệu IUI/IVF hiện tại **không xuất từ hệ thống nào** — NV CSKH tự nhập liệu các ca bơm/chuyển phôi vào file Google Sheets trên Drive (file "IUI 2026", "IVF 2026"). Đây là file quản lý nội bộ của phòng CSKH.

Theo quy trình gốc của khách:
- IUI: "vào file IUI 2026 trên Drive, nhập liệu các ca ngày mai bơm IUI → hôm sau gọi chăm sóc (không có đổ file, gọi từ phần nhập liệu thủ công)"
- IVF: "vào file IVF 2026 trên Drive, nhập liệu các ca chuyển phôi ngày mai → gọi chăm các ca đủ 14 ngày sau chuyển phôi"

> **Cần xác nhận ở giai đoạn khảo sát (GĐ1):** Dữ liệu lịch bơm IUI / chuyển phôi có trong HIS không? Nếu có → Data Sync lấy trực tiếp từ HIS, NV không cần nhập file Drive nữa. Nếu không → Data Sync đọc file Drive hoặc NV nhập trực tiếp trên CRM.

**Đầu vào (file IUI/IVF trên Drive, hoặc HIS nếu có):**

| Cột | Ví dụ | Mapping → CRM |
|-----|-------|---------------|
| PID | `26005816` | Lookup Person |
| TÊN | `NGUYỄN THỊ LAN` | Verify |
| BS | `BS Cường` | TreatmentCycle.doctor |
| NGÀY BƠM (IUI) | `2026-03-15` | Person.iuiDate, TreatmentCycle.procedureDate |
| NGÀY OR (IVF) | `2026-03-10` | TreatmentCycle.procedureDate |
| NGÀY FET/ET | `2026-03-12` | Person.embryoTransferDate |
| NGÀY TEST BETA | `2026-03-26` | TreatmentCycle.betaDate |
| ĐÃ IUI / ĐÃ OR | `x` | TreatmentCycle.status = DONE |
| HỦY | `x` | TreatmentCycle.status = CANCELLED |
| LÍ DO HỦY | `BN KPC` | Person.cancellationReason |

**Logic tạo task tự động:**

| Loại | Điều kiện | Task được tạo |
|------|-----------|---------------|
| IUI beta | Có NGÀY BƠM và chưa hủy | careType=BETA_THAI, hạn CS = ngày bơm + 1 ngày |
| IVF beta | Có NGÀY ET/FET và chưa hủy | careType=BETA_THAI, hạn CS = ngày ET + 14 ngày |
| Thai kỳ | Kết quả beta dương tính | careType=THAI_KY, cập nhật giai đoạn → "Thai kỳ" |

**Đầu ra → CRM:**

| Action | Object |
|--------|--------|
| Upsert TreatmentCycle | Chu kỳ điều trị — link với Person |
| Update Person.iuiDate / embryoTransferDate | Bệnh nhân — ngày thủ thuật |
| Create Task (careType=BETA_THAI) | Công việc CS — hạn theo logic trên |
| Update Person.treatmentStage → THAI_KY | Bệnh nhân — khi beta đậu |
| Create Task (careType=THAI_KY) | Công việc CS — khi giai đoạn = Thai kỳ |

---

#### 5.4.5 Quy tắc chống trùng lặp

Service chạy hàng ngày, cần đảm bảo không tạo bản ghi trùng:

| Object | Unique key | Xử lý khi trùng |
|--------|-----------|-----------------|
| Person | PID | Upsert — cập nhật fields mới, giữ nguyên fields cũ |
| Task | PID + careType + dueAt | Skip — không tạo task trùng |
| InpatientStay | PID + admissionDate | Skip |
| TreatmentCycle | PID + type + startDate | Upsert — cập nhật status, kết quả |

#### 5.4.6 Xử lý lỗi & cảnh báo

| Tình huống | Hành động |
|------------|-----------|
| PID không tìm thấy trong CRM | Tự tạo Person mới với thông tin từ file |
| Ngày hẹn HIT ≠ IMS | Tạo Note cảnh báo trên Person: "⚠ Ngày hẹn không khớp: HIT={x}, IMS={y}" |
| File Excel định dạng sai | Log lỗi, bỏ qua dòng, tiếp tục xử lý dòng khác |
| CRM API lỗi | Retry 3 lần, sau đó log và báo qua Zalo nhóm hỗ trợ |
| Ca hủy chu kỳ | Cập nhật lý do hủy trên Person, không tạo task mới |

#### 5.4.7 Thư mục import & cấu hình

```
/data/imports/
├── his-noi-tru/          ← NV IT đặt file nội trú hàng ngày
│   └── 2026-03-27.xlsx
├── his-tiep-don/         ← File BN mới (CBNM)
│   └── 2026-03-27.xlsx
├── hit-tai-kham/         ← Lịch hẹn tái khám
│   └── 2026-03-27.xlsx
├── iui-ivf/              ← File IUI/IVF từ Drive
│   └── iui-2026.xlsx
│   └── ivf-2026.xlsx
├── processed/            ← File đã xử lý (lưu lại để đối soát)
└── errors/               ← File lỗi
```

**Cấu hình (env vars):**
```
CRM_API_URL=https://bvhmsg.fixpartner.co/api
CRM_API_TOKEN=<admin-api-token>
IMPORT_DIR=/data/imports
SYNC_SCHEDULE=0 6 * * *     # 6:00 sáng mỗi ngày
ALERT_ZALO_WEBHOOK=<url>     # Thông báo lỗi qua Zalo
```

#### 5.4.8 Trạng thái phát triển

| Component | Ghi chú |
|-----------|---------|
| HIS Connector (File Import) | Cần file mẫu thực tế để validate mapping |
| HIT Connector (File Import) | Cấu trúc file tham khảo từ `cs-ngoai-tru.xlsx` sheet "LỊCH TÁI KHÁM" |
| IMS Connector | Cần khảo sát phương thức truy xuất IMS |
| IUI/IVF Processor | Cấu trúc file tham khảo từ `cs-ngoai-tru.xlsx` sheet "KTBT-IUI", "KTBT-IVF" |
| Transform & Validate | Logic đối soát + loại trừ cần xác nhận ở giai đoạn khảo sát |
| CRM Writer | Tạo Person/Task qua Twenty CRM API |
| Chống trùng lặp | Unique key: PID + careType + dueAt |
| Cảnh báo & logging | Thông báo lỗi qua Zalo nhóm hỗ trợ |

**Điều kiện tiên quyết từ bệnh viện:**
1. Cung cấp tài khoản HIS/HIT để khảo sát API (nếu có)
2. Hoặc: cam kết NV IT xuất file Excel hàng ngày theo cấu trúc cố định
3. Cung cấp file mẫu thực tế (không phải demo) để validate mapping

---

## 6. Ngoài phạm vi (Out of Scope)

- Quản lý tài chính/thanh toán
- Lịch hẹn online cho bệnh nhân
- Telemedicine/video call
- Mobile app riêng (dùng web responsive)
- Đa ngôn ngữ (chỉ tiếng Việt)
- Multi-tenant (chỉ 1 bệnh viện)

---

## 7. Kiến trúc kỹ thuật

### 7.1 Nguyên tắc
- **Zero code modification** — không sửa source code Twenty
- **API-only customization** — tất cả qua REST/GraphQL API
- **Script-driven setup** — 1 file Python, chạy từ bất kỳ đâu
- **Upgrade-safe** — sync upstream Twenty không conflict

### 7.2 Stack
- **CRM Engine:** Twenty CRM (upstream, unmodified)
- **Setup Script:** Python + httpx (`scripts/setup-bvhm.py`)
- **Database:** PostgreSQL 16
- **Cache:** Redis
- **Deploy:** Docker Compose on Dokploy
- **Domain:** https://bvhmsg.fixpartner.co

### 7.3 Setup flow
```
1. Deploy Twenty nguyên bản (docker-compose.yml)
2. Tạo tài khoản admin qua UI
3. Chạy: uv run scripts/setup-bvhm.py --level base   (hoặc --level demo)
4. Sẵn sàng sử dụng
```

### 7.4 Backup & Restore

Sử dụng tính năng **Volume Backups** của Dokploy để backup volume `db-data` (PostgreSQL) và kết hợp `pg_dump` để đảm bảo tính toàn vẹn dữ liệu.

#### Cấu hình backup

**Bước 1 — Trên Dokploy dashboard:**
1. Mở project BVHMSG → chọn service Compose
2. Vào tab **Advanced** → mục **Volumes**
3. Tìm volume `db-data` → bấm **Enable Backup**
4. Cấu hình:
   - **Schedule:** `0 2 * * *` (2:00 sáng mỗi ngày)
   - **Destination:** S3-compatible storage (khuyến nghị) hoặc local
   - **Retention:** 30 (giữ 30 bản backup gần nhất)
   - **Prefix:** `bvhm-db`

**Bước 2 — Cấu hình S3 Destination (nếu dùng S3):**
1. Dokploy Settings → **S3 Destinations** → **Add**
2. Nhập: Endpoint, Bucket, Access Key, Secret Key, Region
3. Chọn destination này khi cấu hình backup ở bước 1

#### Restore

1. Trên Dokploy → Volume Backups → chọn bản backup cần restore
2. Bấm **Restore** → xác nhận
3. **Lưu ý:** Cần stop service trước khi restore để tránh conflict

#### Backup thủ công (pg_dump)

Khi cần backup tức thì hoặc trước khi nâng cấp:

```bash
# Chạy trên server Dokploy
docker exec crm-db pg_dump -U postgres default > backup-$(date +%Y%m%d).sql

# Restore
docker exec -i crm-db psql -U postgres default < backup-20260327.sql
```

#### Chính sách backup

| Hạng mục | Giá trị |
|----------|---------|
| Tần suất | Mỗi ngày lúc 2:00 sáng |
| Lưu trữ | 30 bản gần nhất |
| Nơi lưu | S3-compatible storage (hoặc local trên server Dokploy) |
| Backup thủ công | Trước mỗi lần nâng cấp hệ thống |
| Kiểm tra restore | Tối thiểu 1 lần/tháng |

---

## 8. Kế hoạch Go-live

### 8.1 Triển khai Production

**Nguyên tắc:** Tạo hệ thống mới hoàn toàn cho production — không dùng hệ thống staging có demo data.

```
Bước 1: Tạo project mới trên Dokploy
  → Compose → Git → branch: main
  → Cấu hình env vars (APP_SECRET, PG_DATABASE_PASSWORD, SERVER_URL)
  → Domain: <domain production do BV chọn>
  → Deploy (~20 phút)

Bước 2: Tạo tài khoản admin đầu tiên qua UI
  → Đăng nhập → tắt chức năng tự đăng ký

Bước 3: Chạy script setup (không demo data)
  → uv run scripts/setup-bvhm.py --level base
  → Tạo: 26 Person fields, 13 Task fields, 7 views, 11 Khoa/PK,
    2 custom objects, 3 workflows draft, dashboard, sidebar

Bước 4: Tạo tài khoản cho NV
  → Admin tạo 5-7 tài khoản (quản lý + nhân viên)

Bước 5: Cấu hình backup
  → Theo hướng dẫn mục 7.4

Bước 6: Sẵn sàng sử dụng
```

### 8.2 Đào tạo

**1 buổi đào tạo trực tiếp** tại bệnh viện, nội dung:

| Thời lượng | Nội dung | Đối tượng |
|------------|----------|-----------|
| 15 phút | Đăng nhập, giới thiệu giao diện, sidebar | Tất cả |
| 30 phút | Thực hành: tạo công việc CS, gọi BN, cập nhật trạng thái, ghi chú | NV CSKH |
| 15 phút | Kanban, lọc/sắp xếp, tìm kiếm BN (Ctrl+K) | NV CSKH |
| 15 phút | Dashboard báo cáo, duyệt beta-thai | Quản lý |
| 15 phút | Quản lý tài khoản, hỏi đáp | Tất cả |

**Tài liệu kèm theo:** Gửi file [daily-flow-cskh.md](daily-flow-cskh.md) cho NV tham khảo sau buổi đào tạo.

### 8.3 Vận hành song song

**Thời gian:** 1-2 tuần sau đào tạo, NV chạy song song CRM + Excel cũ.

| Tuần | NV CSKH làm gì | Mục đích |
|------|----------------|----------|
| **Tuần 1** | Làm trên Excel **và** CRM — nhập liệu cả 2 nơi | Làm quen CRM, so sánh kết quả |
| **Tuần 2** | Chuyển chính sang CRM, chỉ dùng Excel kiểm tra chéo khi cần | Xác nhận CRM đáp ứng đủ |
| **Sau tuần 2** | Ngừng Excel, dùng CRM hoàn toàn | Go-live chính thức |

**Tiêu chí ngừng Excel:**
- 100% NV CSKH đăng nhập CRM mỗi ngày
- Tất cả task được tạo và cập nhật trên CRM
- Quản lý xác nhận dashboard phản ánh đúng thực tế
- Không có lỗi hệ thống nghiêm trọng trong tuần 2

**Hỗ trợ trong giai đoạn song song:**
- FixPartner hỗ trợ qua Zalo nhóm, phản hồi trong 4 giờ (giờ hành chính)
- Sửa lỗi, điều chỉnh view/field nếu phát hiện thiếu sót

---

## 9. Metrics thành công

| Metric | Mục tiêu | Đo bằng |
|--------|----------|---------|
| Tỷ lệ BN được gọi/ngày | >90% task "Đã gọi" cuối ngày | Kanban view |
| Thời gian setup CRM mới | <30 phút từ deploy đến dùng | Script execution time |
| Task quá hạn | <5% tổng task | Filter by dueAt < today |
| Adoption | 100% nhân viên CSKH dùng hàng ngày | Login frequency |

---

## 10. Checklist bàn giao

### Hệ thống CRM
- [ ] 32 custom fields trên Bệnh nhân
- [ ] 15 custom fields trên Công việc CS + Assignee
- [ ] 7 CS views với filter + columns (tiếng Việt có dấu)
- [ ] 11 Khoa/PK bệnh viện
- [ ] Sidebar tiếng Việt
- [ ] Custom object: Chu kỳ điều trị (9 fields + relation → Bệnh nhân)
- [ ] Custom object: Lần nhập viện (8 fields + relation → Bệnh nhân)
- [ ] Dashboard "Báo cáo CSKH" — 8 widgets
- [ ] Labels tiếng Việt có dấu cho tất cả fields và options

### Module tích hợp HIS/HIT/IMS
- [ ] HIS Connector: tạo task Nội trú + CBNM
- [ ] HIT Connector: tạo task Tái khám + Beta-thai
- [ ] IMS Connector: cập nhật thuốc
- [ ] IUI/IVF Processor: tạo task Beta-thai
- [ ] Activate workflows: Thai kỳ Auto-Create, Recurring, Cảnh báo quá hạn

### Triển khai & bàn giao
- [ ] Triển khai production
- [ ] Tạo tài khoản (admin + quản lý + NV CSKH)
- [ ] Tắt chức năng tự đăng ký
- [ ] Cấu hình backup tự động
- [ ] Đào tạo 1 buổi trực tiếp
- [ ] Vận hành song song 1-2 tuần
- [ ] Nghiệm thu

### Tương lai (ngoài phạm vi bàn giao)
- [ ] Phân quyền chi tiết: NV chỉ thấy task được assign
- [ ] Email/SMS notification tự động
- [ ] Mobile responsive testing
