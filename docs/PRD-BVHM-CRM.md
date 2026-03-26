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
| **Trưởng phòng CSKH** | 1 | Phân công, giám sát, lập báo cáo |
| **Bác sĩ** (xem) | 7+ | Xem thông tin bệnh nhân, ghi lời dặn |

---

## 3. Quy trình làm việc hàng ngày

### 3.1 Buổi sáng — Xem dashboard & phân công
```
Trưởng phòng mở CRM
  → Xem Kanban "CS theo trạng thái" để biết tổng quan
  → Thấy cột "Chưa gọi" có 15 task, "Cần gọi lại" có 5 task
  → Phân công: "Lan xử lý CS nội trú, Hoa xử lý CS tái khám"
```

### 3.2 Trong ngày — Nhân viên CSKH gọi bệnh nhân
```
Nhân viên Lan mở view "CS nội trú"
  → Thấy danh sách BN vừa xuất viện sau ET (chuyển phôi)
  → Click vào task "CS nội trú - Nguyễn Thị A - xuất viện sau ET"
  → Thấy: thuốc Progesterone 400mg, BS phụ trách: BS Cường
  → Gọi BN → Cập nhật:
      - Trạng thái gọi: "Đã gọi"
      - Ghi chú: "BN uống thuốc đều, hẹn 15/04 xét nghiệm beta"
```

### 3.3 Theo dõi thai kỳ — Không sót ai
```
Nhân viên Hoa mở view "CS thai kỳ"
  → Thấy BN Hồng - Tuần 20, BN Ngọc - Tuần 12
  → Gọi BN Hồng: "Chị ơi hẹn siêu âm hình thái tuần tới nhé"
  → Cập nhật: "Đã gọi" + ghi chú
  → Hệ thống tự tạo task mới cho lần gọi tháng sau (qua Workflow)
```

### 3.4 Cuối ngày — Trưởng phòng kiểm tra
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

**21 custom fields:**

| Nhóm | Field | Loại | Mục đích |
|------|-------|------|----------|
| **Định danh** | PID | TEXT | Mã BN từ HIS, dùng để đối chiếu |
| | Năm sinh | NUMBER | Tính tuổi nhanh |
| | Ngày sinh | DATE | CS sinh nhật |
| | Giới tính | SELECT | Nam/Nữ |
| | CCCD | TEXT | Xác minh danh tính |
| **Nguồn BN** | Nguồn | SELECT | Marketing/BV/BS hợp tác/Khác |
| | Đối tác | TEXT | Tên đối tác giới thiệu |
| **Y khoa** | Chẩn đoán | TEXT | Chẩn đoán chính |
| | Thuốc đang dùng | TEXT | Từ IMS |
| | Chu kỳ hiện tại | TEXT | VD: "IVF lần 2" |
| | Kết quả Beta | TEXT | Số liệu beta HCG |
| **Điều trị** | Ngày bơm IUI | DATETIME | Lịch thủ thuật |
| | Ngày chuyển phôi | DATETIME | Lịch ET |
| | Lý do hủy | TEXT | Nếu hủy chu kỳ |
| **Liên hệ** | Người liên hệ | TEXT | Người thân |
| | SĐT liên hệ | TEXT | SĐT người thân |
| **Vợ/chồng** | Tên vợ/chồng | TEXT | Cho cặp vợ chồng cùng điều trị |
| | PID vợ/chồng | TEXT | Tra cứu chéo |
| | SĐT vợ/chồng | TEXT | Liên hệ |
| **Phân công** | Phòng khám | TEXT | PK phụ trách |
| | BS phụ trách | TEXT | Bác sĩ chính |

**Acceptance Criteria:**
- [x] Tất cả fields hiện trên form chi tiết bệnh nhân
- [x] Có thể tìm kiếm BN theo PID, tên, SĐT
- [x] BN được link với Khoa/PK (Company)

---

### 4.2 Quản lý Công việc Chăm sóc (Task)

**Mô tả:** Mỗi task = 1 việc cần làm cho 1 bệnh nhân. Nhân viên CSKH xử lý task hàng ngày.

**13 custom fields:**

| Nhóm | Field | Loại | Mục đích |
|------|-------|------|----------|
| **Phân loại** | Loại chăm sóc | SELECT | 6 loại: Nội trú, CBNM, Thủ thuật, Tái khám, Beta-thai, Thai kỳ |
| | Loại lịch hẹn | SELECT | 7 loại: Tái khám, IUI, Lấy trứng, Chuyển phôi, Phẫu thuật, PRP, Sinh nhật |
| **Lịch hẹn** | Giờ hẹn | TEXT | VD: "08:00" |
| | Giờ có mặt | TEXT | VD: "07:30" |
| | Ngày nhắc | DATETIME | Khi nào nhắc BN |
| | Mã khám | TEXT | Mã từ HIS |
| **Gọi điện** | Trạng thái gọi | SELECT | Chưa gọi / Đã gọi / Cần gọi lại / Không liên lạc |
| | Ghi chú cuộc gọi | TEXT | Kết quả cuộc gọi |
| **Y khoa** | Lời dặn BS | TEXT | BS ghi lời dặn |
| | Thuốc | TEXT | Thuốc tại thời điểm |
| | BS phụ trách | TEXT | Bác sĩ |
| | Phòng khám | TEXT | PK nào |
| **Duyệt** | Trạng thái duyệt | SELECT | Cho beta-thai: Chưa duyệt/Đã duyệt/Từ chối |

**Acceptance Criteria:**
- [x] Task luôn link với bệnh nhân (qua taskTarget)
- [x] Task có due date để sắp xếp ưu tiên
- [x] Trạng thái gọi cập nhật real-time trên Kanban

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

### 4.5 Ghi chú Lâm sàng (Note)

**Mô tả:** Ghi chú tự do, link với BN, dùng cho kết quả xét nghiệm, siêu âm, tư vấn.

**Acceptance Criteria:**
- [x] Note có title + body (rich text markdown)
- [x] Note link với BN qua noteTarget
- [x] Hiện trên timeline của BN

---

### 4.6 Sidebar sạch

**Mô tả:** Chỉ hiện menu liên quan đến bệnh viện.

**Hiện:** Companies, People, Tasks, Notes, Dashboards, Workflows
**Ẩn:** Opportunities, Workflow Runs, Workflow Versions

**Acceptance Criteria:**
- [x] Không có Opportunities trong sidebar
- [x] Không có Workflow Runs/Versions

---

## 5. Tính năng — Phase 2 (Nâng cao)

### 5.1 Workflows tự động (Ưu tiên cao)

| # | Workflow | Trigger | Action | Giá trị |
|---|---------|---------|--------|---------|
| 1 | Thai Kỳ Auto-Create | BN cập nhật → giai đoạn thai kỳ | Tự tạo task CS thai kỳ | Không sót BN mang thai |
| 2 | Thai Kỳ Recurring | Task thai kỳ "Đã gọi" | Tự tạo task tháng sau | Chuỗi CS không đứt |
| 3 | Cảnh báo quá hạn | Hàng ngày 8h sáng | Tìm task quá hạn | Trưởng phòng biết ngay |

**Status:** Có thể tạo qua UI workflow builder của Twenty. Cần thêm field `treatmentStage` trên Person.

### 5.2 Custom Objects (Ưu tiên trung bình)

| Object | Mô tả | Fields chính |
|--------|-------|-------------|
| **Chu kỳ điều trị** (Treatment Cycle) | Theo dõi IUI/IVF cycle | Loại, trạng thái, BS, ngày bắt đầu, ngày thủ thuật, kết quả beta |
| **Lần nhập viện** (Inpatient Stay) | Theo dõi nội trú | Loại (HTSS/PT/Sản), ngày nhập/xuất, phẫu thuật, hài lòng, quà tặng |

**Status:** Cần tạo qua metadata API (`createOneObject`). Script chưa implement.

### 5.3 Dashboard & Báo cáo (Ưu tiên cao)

| Báo cáo | Metrics | Dùng cho |
|---------|---------|----------|
| **Tổng quan CSKH** | Số task/ngày, tỷ lệ gọi được, task quá hạn | Trưởng phòng |
| **Theo loại CS** | Phân bổ task theo 6 loại | Lập kế hoạch nhân sự |
| **Theo BS/PK** | BN theo phòng khám | Đánh giá hiệu quả |
| **Thai kỳ** | Số BN đang mang thai, tuần thai | Theo dõi outcome |

**Status:** Twenty có Dashboard object. Cần thiết kế widget và kết nối data.

### 5.4 Tích hợp HIS (Ưu tiên thấp — Phase 3)

| Hệ thống | Dữ liệu | Hướng |
|-----------|---------|-------|
| **HIS** (Hospital Info System) | BN nội trú, PID | HIS → CRM |
| **HIT** (Appointment System) | Lịch hẹn tái khám | HIT → CRM |
| **IMS** (Medication System) | Thuốc & liệu trình | IMS → CRM |

**Status:** 3 draft workflows đã có placeholder. Cần API/connector từ phía HIS.

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
4. Done — CRM sẵn sàng sử dụng
```

---

## 8. Metrics thành công

| Metric | Mục tiêu | Đo bằng |
|--------|----------|---------|
| Tỷ lệ BN được gọi/ngày | >90% task "Đã gọi" cuối ngày | Kanban view |
| Thời gian setup CRM mới | <30 phút từ deploy đến dùng | Script execution time |
| Task quá hạn | <5% tổng task | Filter by dueAt < today |
| Adoption | 100% nhân viên CSKH dùng hàng ngày | Login frequency |

---

## 9. Trạng thái hiện tại

### Done (Phase 1 MVP)
- [x] 21 custom fields trên Person (Bệnh nhân)
- [x] 13 custom fields trên Task (Công việc CS)
- [x] 7 CS views với filter + columns
- [x] 11 Khoa/PK bệnh viện
- [x] Ẩn Opportunities, Workflow Runs/Versions
- [x] Deactivate Opportunity object
- [x] Demo data: 8 BN, 12 tasks, 8 notes (all linked)
- [x] Script idempotent, chạy từ bất kỳ đâu
- [x] Deploy trên Dokploy

### Not Done (Phase 2)
- [ ] 3 Workflows tự động (Thai Kỳ Auto-Create, Recurring, Overdue Alert)
- [ ] 2 Custom objects (Chu kỳ điều trị, Lần nhập viện)
- [ ] Dashboard báo cáo CSKH
- [ ] Đổi tên sidebar sang tiếng Việt (Companies→Khoa, People→Bệnh nhân...)
- [ ] Field `treatmentStage` trên Person (cần cho workflows)

### Not Done (Phase 3)
- [ ] Tích hợp HIS/HIT/IMS
- [ ] Email/SMS notification
- [ ] Mobile responsive testing
