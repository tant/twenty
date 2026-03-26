# Đề xuất giải pháp hệ thống quản lý chăm sóc khách hàng

**Bệnh viện Hỗ trợ Sinh sản & Nam học Sài Gòn**

---

**Đơn vị thực hiện:** FixPartner
**Ngày:** 22/03/2026
**Phiên bản:** 1.0

---

## 1. Bối cảnh & vấn đề hiện tại

### 1.1. Quy trình hiện tại

Phòng Chăm sóc khách hàng (CSKH) đang quản lý 4 quy trình chính:

| # | Quy trình | Mô tả |
|---|-----------|-------|
| 1 | Chăm sóc nội trú | Gọi chăm sóc bệnh nhân nhập/xuất viện tại các khoa HTSS, PTTT, Sản |
| 2 | Chăm sóc TT/CBNM | Chăm sóc ca bệnh nhân mới và nhắc hẹn thủ thuật |
| 3 | Gọi tái khám | Đối soát lịch hẹn từ nhiều nguồn, gọi nhắc tái khám |
| 4 | Chăm sóc beta-thai | Theo dõi kết quả beta, chăm sóc thai kỳ cho ca IUI/IVF |

### 1.2. Các điểm nghẽn chính

- **Thao tác thủ công nhiều:** Nhân viên phải đăng nhập HIS/HIT/IMS, xuất Excel, copy-paste dữ liệu qua Google Drive, xóa cột, kéo hàm, fill thuốc thủ công mỗi ngày.
- **Dữ liệu phân tán:** Thông tin bệnh nhân nằm rải rác trên HIS, HIT, IMS, Google Sheets (file IUI, IVF, CBNM, Nội trú, Beta...) — rất dễ sót hoặc sai lệch.
- **Đối soát tốn thời gian:** Quy trình tái khám cần đối soát chéo giữa 4-5 nguồn dữ liệu (IMS, HIT, sheet IUI, sheet IVF, file tái khám) để đảm bảo không thiếu bệnh nhân.
- **Thiếu báo cáo tổng quan:** Quản lý khó nắm được tình hình chăm sóc tổng thể, tỷ lệ gọi thành công, số ca đang theo dõi.

---

## 2. Giải pháp đề xuất

Xây dựng **hệ thống quản lý chăm sóc khách hàng (CRM)** chuyên biệt cho bệnh viện, tích hợp trực tiếp với hệ thống HIS/HIT/IMS hiện có, giúp tự động hóa các thao tác thủ công và tập trung toàn bộ dữ liệu về một nền tảng duy nhất.

**Địa chỉ hệ thống:** https://bvhmsg.fixpartner.co (hoặc địa chỉ khác do khách hàng chọn)

### 2.1. Sơ đồ tổng quan

```
┌─────────────────────────────────────────────────────────────┐
│                    HỆ THỐNG CRM BVHM                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Hồ sơ      │  │  Danh sách   │  │   Báo cáo &     │   │
│  │  Bệnh nhân   │  │  chăm sóc    │  │   Thống kê      │   │
│  └──────▲───────┘  └──────▲───────┘  └────────▲────────┘   │
│       │               │                      │              │
│       └───────────────┼──────────────────────┘              │
│                       │                                     │
│              ┌────────▼────────┐                            │
│              │  Module tích hợp  │                            │
│              │  dữ liệu tự động │                            │
│              └────────▲────────┘                            │
└───────────────────────┼─────────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
     ┌────▼───┐   ┌────▼───┐   ┌────▼───┐
     │  HIS   │   │  HIT   │   │  IMS   │
     └────────┘   └────────┘   └────────┘
```

---

## 3. Các chức năng chính

### 3.1. Quản lý hồ sơ bệnh nhân

Tập trung toàn bộ thông tin bệnh nhân trên một nền tảng:

- **Thông tin cá nhân:** Họ tên, PID, ngày sinh, giới tính, CCCD, số BHYT, nhóm máu
- **Thông tin liên hệ:** SĐT, email, địa chỉ, thông tin người thân (tên, quan hệ, SĐT)
- **Thông tin điều trị:** Giai đoạn (Tư vấn → Khám → IUI/IVF → Mang thai → Theo dõi thai → Sau sinh), khoa điều trị, PK/BS phụ trách, đối tác (bảo hiểm/giới thiệu)
- **Thông tin liệu trình:** Thuốc đang sử dụng (từ IMS), chu kỳ IUI/IVF hiện tại, ngày bơm IUI / ngày chuyển phôi, số liệu beta, lý do hủy chu kỳ (nếu có)
- **Lịch sử chăm sóc:** Toàn bộ lịch sử gọi điện, ghi chú, kết quả chăm sóc được lưu trữ theo dòng thời gian

### 3.2. Danh sách bệnh nhân theo loại chăm sóc

Thay vì xuất Excel và fill thủ công, hệ thống sẽ **tự động lọc và hiển thị danh sách bệnh nhân** cần chăm sóc theo từng loại. Nhân viên mở view tương ứng, click vào bệnh nhân để xem hồ sơ, gọi điện và ghi chú trực tiếp trên timeline.

| View | Nguồn dữ liệu | Mô tả |
|------|---------------|-------|
| **Nội trú** | HIS - Báo cáo nội trú + lịch thủ thuật PHS | Danh sách bệnh nhân nhập/xuất viện (HTSS, PTTT, Sản), kèm ngày vào/xuất viện, phòng bệnh, BS thực hiện. Đánh dấu OR/ET/FET theo lịch thủ thuật |
| **CBNM** | HIS - Báo cáo tiếp đón + IMS | Danh sách bệnh nhân mới, kèm thông tin thuốc và phân loại PK/BS từ IMS. Tự loại trừ ca hủy chu kỳ (lấy lý do hủy từ HIS) |
| **Thủ thuật** | Lịch thủ thuật PHS (nhập thủ công) | Bệnh nhân có lịch thủ thuật theo PID từ lịch PHS ban hành, kèm giờ hẹn (PHS gửi qua Zalo). *Phần này cần nhập thủ công vì nguồn không từ hệ thống* |
| **Tái khám** | HIT - Lịch hẹn KH + IMS + sheet IUI/IVF/CBNM | Danh sách bệnh nhân cần tái khám, đã loại bỏ hẹn phòng hồ sơ/cấp cứu/hành chính, đối soát chéo với IMS và các sheet liệu trình, cảnh báo khi IMS/HIT không trùng khớp |
| **Beta-thai** | HIS - Lịch tái khám ngày mai + file IUI/IVF trên Drive | IUI: bệnh nhân ngày sau bơm. IVF: bệnh nhân đủ 14 ngày sau chuyển phôi. Đối soát với danh sách tái khám, gửi quản lý duyệt trước khi gọi |
| **Thai kỳ** | Kết quả beta | Bệnh nhân beta đậu được tự động chuyển giai đoạn sang "Mang thai", hiển thị trong view khi đến hạn chăm sóc (mỗi tháng 1 lần) |

**Trên mỗi hồ sơ bệnh nhân, nhân viên thấy:**
- Thông tin đầy đủ: PID, họ tên, SĐT, PK/BS phụ trách
- Thuốc đang sử dụng (fill tự động từ IMS)
- Thông tin liệu trình: chu kỳ, ngày bơm/chuyển phôi, số liệu beta, lý do hủy (nếu có)
- Note/nhắc nhở từ phòng khám (nếu có)
- Trạng thái chăm sóc: Chưa gọi → Đã gọi → Cần gọi lại → Không liên lạc được
- Timeline: toàn bộ lịch sử ghi chú, cuộc gọi, thay đổi giai đoạn

### 3.3. Tích hợp & đối soát tự động

Đây là phần cốt lõi giúp loại bỏ thao tác thủ công:

- **Đồng bộ lịch hẹn:** Tự động lấy lịch hẹn tái khám từ HIT, đối soát với IMS, đánh dấu các trường hợp không trùng khớp để nhân viên kiểm tra
- **Đồng bộ bệnh nhân mới:** Bệnh nhân tiếp đón trên HIS tự động được tạo hồ sơ trên CRM
- **Đồng bộ nội trú:** Thông tin nhập/xuất viện tự động cập nhật
- **Tự lọc loại trừ:** Tự động loại bỏ lịch hẹn Phòng hồ sơ, Cấp cứu, Hành chính; tự loại các ca hủy chu kỳ

### 3.4. Báo cáo cho quản lý

Báo cáo tổng quan phục vụ cấp quản lý:

- Số lượng cuộc gọi theo ngày/tuần/tháng
- Tỷ lệ gọi thành công / không liên lạc được / cần gọi lại
- Khối lượng chăm sóc theo nhân viên
- Số bệnh nhân chưa gọi, quá hạn
- Thời gian trung bình hoàn thành chăm sóc

---

## 4. Phạm vi công việc

### Giai đoạn 1: Phân tích & tích hợp dữ liệu (2-3 tuần)

| # | Công việc | Chi tiết |
|---|-----------|----------|
| 1.1 | Khảo sát hệ thống HIS/HIT/IMS | Xác định API hoặc phương thức xuất dữ liệu khả dụng, cấu trúc dữ liệu, tần suất cập nhật |
| 1.2 | Mapping dữ liệu | Lập bảng ánh xạ các trường dữ liệu giữa HIS/HIT/IMS và CRM (PID, mã bệnh nhân, thuốc, lịch hẹn...) |
| 1.3 | Xây dựng module tích hợp | Viết các connector lấy dữ liệu tự động từ HIS/HIT/IMS, xử lý đối soát, loại trừ dữ liệu không cần thiết |
| 1.4 | Kiểm thử tích hợp | Chạy thử với dữ liệu thực, so sánh kết quả với quy trình thủ công hiện tại để đảm bảo độ chính xác |

### Giai đoạn 2: Giao diện làm việc & quy trình chăm sóc (2 tuần)

| # | Công việc | Chi tiết |
|---|-----------|----------|
| 2.1 | Thiết kế các view bệnh nhân | Tạo các view lọc sẵn theo loại chăm sóc (nội trú, CBNM, tái khám, beta-thai, thai kỳ) với các cột hiển thị phù hợp |
| 2.2 | Cấu hình đồng bộ tự động | Dữ liệu từ HIS/HIT/IMS tự động cập nhật vào hồ sơ bệnh nhân, bệnh nhân tự xuất hiện trong view đúng khi có dữ liệu mới |
| 2.3 | Quy trình ghi nhận kết quả | Xây dựng giao diện ghi chú nhanh trên timeline bệnh nhân sau cuộc gọi, cập nhật trạng thái chăm sóc |
| 2.4 | Chuyển giai đoạn tự động | Beta đậu → tự chuyển sang "Mang thai", bệnh nhân tự xuất hiện trong view thai kỳ khi đến hạn chăm sóc hàng tháng |

### Giai đoạn 3: Báo cáo & bàn giao (1 tuần)

| # | Công việc | Chi tiết |
|---|-----------|----------|
| 3.1 | Xây dựng dashboard hoạt động CSKH | Báo cáo tổng quan cuộc gọi, hiệu suất nhân viên, tỷ lệ hoàn thành, ca quá hạn |
| 3.2 | Đào tạo sử dụng | Hướng dẫn nhân viên CSKH và quản lý sử dụng hệ thống |
| 3.3 | Hỗ trợ vận hành song song | Chạy song song với quy trình cũ trong 1-2 tuần để đảm bảo ổn định |

---

## 5. Lợi ích kỳ vọng

| Hiện tại | Sau khi triển khai |
|----------|-------------------|
| Xuất Excel từ 3 hệ thống mỗi ngày, copy-paste thủ công | Dữ liệu tự động đồng bộ, không cần xuất file |
| Đối soát chéo 4-5 file, dễ sót bệnh nhân | Hệ thống tự đối soát, cảnh báo khi có sai lệch |
| Không biết nhân viên đã gọi bao nhiêu ca | Dashboard theo dõi real-time |
| Quản lý hỏi phải tổng hợp thủ công | Báo cáo tự động, xem bất cứ lúc nào |
| Thông tin bệnh nhân nằm rải rác nhiều file | Một nơi duy nhất, tra cứu nhanh theo PID |

---

## 6. Yêu cầu hợp tác từ bệnh viện

Để triển khai hiệu quả, chúng tôi cần sự phối hợp từ bệnh viện:

1. **Cung cấp tài khoản truy cập** HIS/HIT/IMS (hoặc API documentation nếu có)
2. **Cử 1-2 nhân viên CSKH** phối hợp trong quá trình phân tích và kiểm thử
3. **Cung cấp file mẫu** (file IUI, IVF, CBNM, Nội trú hiện đang dùng trên Drive) để mapping dữ liệu
4. **Phối hợp với phòng IT** để đảm bảo kết nối mạng giữa CRM và các hệ thống nội bộ

---

## 7. Hạ tầng, vận hành & bảo mật

### 7.1. Hạ tầng & triển khai

- Hệ thống được **triển khai trên máy chủ của FixPartner**, đảm bảo hiệu năng và tính sẵn sàng cao.
- Địa chỉ truy cập: https://bvhmsg.fixpartner.co (hoặc một url khác cho bệnh viện chọn) — nhân viên bệnh viện truy cập qua trình duyệt web, không cần cài đặt phần mềm.
- Dữ liệu được lưu trữ trên hệ thống cơ sở dữ liệu chuyên dụng, sao lưu định kỳ.

### 7.2. Duy trì & hỗ trợ kỹ thuật

- FixPartner **chịu trách nhiệm duy trì, vận hành hệ thống** và xử lý các sự cố kỹ thuật phát sinh trong quá trình sử dụng.
- Cập nhật, nâng cấp tính năng theo yêu cầu nghiệp vụ của bệnh viện.
- Hỗ trợ kỹ thuật qua các kênh liên lạc đã thống nhất.

### 7.3. Cam kết bảo mật dữ liệu

FixPartner cam kết thực hiện các biện pháp bảo mật sau:

**Bảo mật kỹ thuật:**
- Mã hóa toàn bộ kết nối bằng HTTPS/TLS, không truyền dữ liệu dạng văn bản thường (plaintext)
- Phân quyền truy cập theo vai trò (RBAC) — mỗi nhân viên chỉ xem được dữ liệu thuộc phạm vi công việc
- Xác thực người dùng bằng mật khẩu mạnh, hỗ trợ xác thực hai yếu tố (2FA)
- Ghi nhận nhật ký truy cập và thao tác (audit log) cho mọi hành động trên hệ thống
- Sao lưu dữ liệu tự động hàng ngày, lưu trữ bản sao lưu tối thiểu 30 ngày
- Dữ liệu được lưu trữ trên máy chủ đặt tại Việt Nam, không chuyển ra nước ngoài

**Bảo mật vận hành:**
- Không chia sẻ, bán hoặc sử dụng dữ liệu bệnh nhân cho bất kỳ mục đích nào ngoài phạm vi hợp đồng
- Chỉ nhân sự kỹ thuật được ủy quyền của FixPartner mới có quyền truy cập hệ thống ở cấp quản trị
- Cam kết thông báo cho bệnh viện trong vòng **72 giờ** khi phát hiện sự cố bảo mật hoặc rò rỉ dữ liệu (theo đúng quy định pháp luật)
- Khi kết thúc hợp đồng, FixPartner sẽ bàn giao toàn bộ dữ liệu và xóa sạch dữ liệu trên máy chủ theo yêu cầu của bệnh viện

**Hỗ trợ quyền bệnh nhân:**
- Hệ thống là công cụ **nội bộ dành cho nhân viên** — bệnh nhân không trực tiếp truy cập. Khi bệnh nhân yêu cầu xem, sửa hoặc xóa dữ liệu cá nhân, nhân viên bệnh viện sẽ thực hiện thao tác trên CRM.
- Hệ thống hỗ trợ các chức năng tra cứu, chỉnh sửa và xóa dữ liệu để bệnh viện đáp ứng yêu cầu của bệnh nhân đúng thời hạn pháp luật (xác nhận trong 2 ngày làm việc, xử lý trong 10-20 ngày theo NĐ 356/2025/NĐ-CP).

### 7.4. Tuân thủ quy định pháp luật

Hệ thống được thiết kế tuân thủ các văn bản pháp luật hiện hành:

| Văn bản | Nội dung liên quan |
|---------|-------------------|
| **Luật Bảo vệ Dữ liệu Cá nhân** (Luật 91/2025/QH15, hiệu lực 01/01/2026) | Khung pháp lý chính về bảo vệ DLCN, thay thế NĐ 13/2023 |
| **Nghị định 356/2025/NĐ-CP** | Hướng dẫn chi tiết Luật BVDLCN: DPIA, DPO, thời hạn phản hồi, xử phạt |
| **Luật An toàn Thông tin Mạng** (86/2015/QH13) | Yêu cầu bảo mật hệ thống thông tin |
| **Thông tư 46/2018/TT-BYT** | Quy định hồ sơ bệnh án điện tử, yêu cầu lưu trữ dữ liệu y tế |
| **Thông tư 53/2014/TT-BYT** | Điều kiện hoạt động y tế trên môi trường mạng |

**Về dữ liệu y tế nhạy cảm:**

Dữ liệu sức khỏe của bệnh nhân được phân loại là **dữ liệu cá nhân nhạy cảm** theo Luật 91/2025. Dù hệ thống CRM chỉ sử dụng nội bộ, nghĩa vụ pháp lý vẫn áp dụng đầy đủ vì dữ liệu nhạy cảm vẫn đang được xử lý. Cụ thể:

- **Đánh giá tác động (DPIA):** Bệnh viện cần thực hiện và nộp hồ sơ DPIA trong vòng 60 ngày kể từ ngày bắt đầu xử lý dữ liệu trên hệ thống CRM. FixPartner sẽ **hỗ trợ cung cấp thông tin kỹ thuật** cần thiết.
- **Nhân sự bảo vệ dữ liệu (DPO):** Bệnh viện cần chỉ định nhân sự hoặc bộ phận phụ trách bảo vệ dữ liệu cá nhân (bắt buộc khi xử lý dữ liệu nhạy cảm). FixPartner sẽ **phối hợp kỹ thuật** với bộ phận này.
- **Về sự đồng ý:** Việc thu thập đồng ý xử lý dữ liệu sức khỏe thuộc trách nhiệm của bệnh viện tại khâu tiếp đón bệnh nhân (trên HIS/HIT). CRM không trực tiếp thu thập dữ liệu từ bệnh nhân mà chỉ xử lý dữ liệu đã được bệnh viện thu thập hợp pháp.

**Phân định trách nhiệm:**

- Bệnh viện là **Bên kiểm soát dữ liệu** — chịu trách nhiệm pháp lý chính về thu thập, xử lý và bảo vệ dữ liệu cá nhân bệnh nhân, bao gồm thực hiện DPIA, chỉ định DPO, và thu thập sự đồng ý.
- FixPartner là **Bên xử lý dữ liệu** — cung cấp và vận hành hệ thống theo ủy quyền của bệnh viện, cam kết không sử dụng dữ liệu cho mục đích riêng.
- Hai bên sẽ ký **Thỏa thuận Xử lý Dữ liệu Cá nhân (DPA)** theo quy định tại Luật 91/2025, nêu rõ phạm vi, mục đích xử lý và biện pháp bảo mật.

**Giới hạn trách nhiệm:**

- Trách nhiệm của mỗi bên được thực hiện theo đúng quy định pháp luật hiện hành và các điều khoản chi tiết trong hợp đồng.
- Mức phạt vi phạm hợp đồng (nếu có) theo quy định tại Điều 301 Luật Thương mại 2005.
- FixPartner không chịu trách nhiệm về thiệt hại phát sinh từ các sự kiện bất khả kháng.
- Khi phát sinh vấn đề liên quan đến dữ liệu, FixPartner sẽ phối hợp cung cấp thông tin hiện trạng hệ thống để các bên cùng xử lý.

---

## 8. Chi phí

*(Chi tiết sẽ được thống nhất trong hợp đồng)*

| Hạng mục | Mô tả |
|----------|-------|
| **Chi phí triển khai ban đầu** | Bao gồm: phân tích, tích hợp HIS/HIT/IMS, cấu hình hệ thống, đào tạo |
| **Chi phí vận hành hàng tháng** | Bao gồm: server, duy trì, hỗ trợ kỹ thuật, sao lưu dữ liệu |
| **Chi phí phát triển thêm** | Tính theo yêu cầu phát sinh ngoài phạm vi ban đầu |
| **Không phát sinh thêm** | Bản quyền phần mềm (nền tảng mã nguồn mở), phí người dùng |

---

## 9. Cam kết dịch vụ (SLA)

| Hạng mục | Cam kết |
|----------|---------|
| **Uptime hệ thống** | ≥ 99% (không tính thời gian bảo trì có thông báo trước) |
| **Thời gian phản hồi sự cố** | Sự cố nghiêm trọng (không truy cập được): ≤ 4 giờ trong giờ hành chính |
| **Thời gian khắc phục** | Sự cố nghiêm trọng: ≤ 24 giờ; Sự cố thường: ≤ 72 giờ |
| **Khung giờ hỗ trợ** | 8h–18h, thứ 2–thứ 6 (trừ lễ/Tết), qua Zalo/điện thoại |
| **Bảo trì định kỳ** | Thông báo trước tối thiểu 24 giờ, thực hiện ngoài giờ hành chính |

**Quy trình dự phòng khi hệ thống gián đoạn:**
- Nhân viên CSKH có thể tạm thời quay lại quy trình xuất Excel từ HIS/HIT như hiện tại
- FixPartner sẽ thông báo ngay khi hệ thống gặp sự cố và cập nhật tiến độ khắc phục

---

## 10. Điều kiện tiên quyết về tích hợp

> **Lưu ý quan trọng:** Khả năng tự động hóa của hệ thống phụ thuộc hoàn toàn vào việc HIS/HIT/IMS có cung cấp API hoặc phương thức trích xuất dữ liệu tự động hay không.

| Kịch bản | Mức độ tự động | Ảnh hưởng |
|----------|---------------|-----------|
| HIS/HIT/IMS **có API** | Tự động hoàn toàn | Như mô tả trong đề xuất này |
| HIS/HIT/IMS **chỉ xuất được file** (Excel/CSV) | Bán tự động | Nhân viên IT xuất file định kỳ, CRM tự import và xử lý — vẫn giảm đáng kể thao tác thủ công |
| HIS/HIT/IMS **không hỗ trợ gì** | Hạn chế | Nhân viên nhập liệu trên CRM — chỉ tập trung được dữ liệu, chưa giảm nhiều thao tác |

FixPartner đề xuất **Giai đoạn 0: Khảo sát kỹ thuật (1 tuần, miễn phí)** để đánh giá khả năng tích hợp thực tế trước khi triển khai, tránh rủi ro cho cả hai bên.

---

## 11. Quyền sở hữu & chuyển giao

| Hạng mục | Chi tiết |
|----------|----------|
| **Nền tảng** | Mã nguồn mở (Open Source), không phụ thuộc bản quyền nhà cung cấp |
| **Dữ liệu** | Thuộc quyền sở hữu hoàn toàn của bệnh viện — có thể yêu cầu xuất toàn bộ dữ liệu bất kỳ lúc nào |
| **Chuyển đổi nhà cung cấp** | Bệnh viện có thể tự vận hành hoặc chuyển sang đơn vị khác — FixPartner sẽ hỗ trợ bàn giao kỹ thuật |
| **Kết thúc hợp đồng** | Bàn giao toàn bộ dữ liệu, mã nguồn đã tùy chỉnh, tài liệu kỹ thuật. Xóa sạch dữ liệu trên server FixPartner trong 30 ngày |

---

## 12. Thời gian dự kiến

| Giai đoạn | Thời gian | Mốc hoàn thành |
|-----------|-----------|----------------|
| GĐ0: Khảo sát kỹ thuật HIS/HIT/IMS | 1 tuần (miễn phí) | Trước khi khởi động |
| GĐ1: Phân tích & tích hợp | 2-3 tuần | Tuần 3 sau khi khởi động |
| GĐ2: Giao diện & quy trình chăm sóc | 2 tuần | Tuần 5 |
| GĐ3: Báo cáo & bàn giao | 1 tuần | Tuần 6 |
| Vận hành song song | 1-2 tuần | Tuần 7-8 |

**Tổng thời gian dự kiến: 7-9 tuần** (bao gồm khảo sát, tùy thuộc mức độ phức tạp của tích hợp HIS/HIT/IMS)

---

*FixPartner — Đối tác công nghệ đáng tin cậy*
