#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
BVHM Hospital CRM Setup Script

Transforms a stock Twenty CRM into a fully-configured BVHM hospital CRM
via the API. No code modifications to Twenty required.

Usage:
    # Level 1: Base setup (hospital structure, custom fields, views — no patient data)
    uv run scripts/setup-bvhm.py --url https://bvhmsg.fixpartner.co --email admin@bvhm.vn --password xxx --level base

    # Level 2: Demo data (includes base + 8 patients, 12 tasks, 8 notes)
    uv run scripts/setup-bvhm.py --url https://bvhmsg.fixpartner.co --email admin@bvhm.vn --password xxx --level demo
"""

import argparse
import sys
import json
from datetime import datetime, timedelta

import httpx

# =============================================================================
# BVHM FIELD DEFINITIONS
# =============================================================================

PERSON_FIELDS = [
    {"name": "pid", "label": "PID", "type": "TEXT", "icon": "IconId", "description": "Mã bệnh nhân từ HIS"},
    {"name": "yearOfBirth", "label": "Năm sinh", "type": "NUMBER", "icon": "IconCalendar"},
    {"name": "dateOfBirth", "label": "Ngày sinh", "type": "DATE", "icon": "IconCake"},
    {"name": "gender", "label": "Giới tính", "type": "SELECT", "icon": "IconGenderBigender",
     "options": [{"label": "Nam", "value": "NAM", "position": 0, "color": "blue"},
                 {"label": "Nữ", "value": "NU", "position": 1, "color": "red"}]},
    {"name": "cccd", "label": "CCCD", "type": "TEXT", "icon": "IconIdBadge2"},
    {"name": "patientSource", "label": "Nguồn", "type": "SELECT", "icon": "IconRoute",
     "options": [{"label": "Marketing", "value": "MARKETING", "position": 0, "color": "blue"},
                 {"label": "Bệnh viện", "value": "BENH_VIEN", "position": 1, "color": "green"},
                 {"label": "Bác sĩ hợp tác", "value": "BAC_SI_HOP_TAC", "position": 2, "color": "turquoise"},
                 {"label": "Khác", "value": "KHAC", "position": 3, "color": "sky"}]},
    {"name": "referralPartner", "label": "Đối tác giới thiệu", "type": "TEXT", "icon": "IconUsersGroup"},
    {"name": "diagnosis", "label": "Chẩn đoán", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "contactPerson", "label": "Người liên hệ", "type": "TEXT", "icon": "IconUser"},
    {"name": "contactPhone", "label": "SĐT liên hệ", "type": "TEXT", "icon": "IconPhone"},
    {"name": "spouseName", "label": "Tên vợ/chồng", "type": "TEXT", "icon": "IconHeart"},
    {"name": "spousePid", "label": "PID vợ/chồng", "type": "TEXT", "icon": "IconId"},
    {"name": "spousePhone", "label": "SĐT vợ/chồng", "type": "TEXT", "icon": "IconPhone"},
    {"name": "medication", "label": "Thuốc đang dùng", "type": "TEXT", "icon": "IconPill"},
    {"name": "currentCycle", "label": "Chu kỳ hiện tại", "type": "TEXT", "icon": "IconRepeat"},
    {"name": "iuiDate", "label": "Ngày bơm IUI", "type": "DATE_TIME", "icon": "IconCalendar"},
    {"name": "embryoTransferDate", "label": "Ngày chuyển phôi", "type": "DATE_TIME", "icon": "IconCalendar"},
    {"name": "betaResult", "label": "Kết quả Beta", "type": "TEXT", "icon": "IconHeartbeat"},
    {"name": "cancelReason", "label": "Lý do hủy chu kỳ", "type": "TEXT", "icon": "IconAlertTriangle"},
    {"name": "clinicRoom", "label": "Phòng khám", "type": "TEXT", "icon": "IconBuilding"},
    {"name": "doctorName", "label": "BS phụ trách", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "treatmentStage", "label": "Giai đoạn điều trị", "type": "SELECT", "icon": "IconProgress",
     "options": [{"label": "IVF", "value": "IVF", "position": 0, "color": "purple"},
                 {"label": "IUI", "value": "IUI", "position": 1, "color": "blue"},
                 {"label": "Thai kỳ", "value": "THAI_KY", "position": 2, "color": "green"},
                 {"label": "Hoàn thành", "value": "HOAN_THANH", "position": 3, "color": "turquoise"}]},
]

TASK_FIELDS = [
    {"name": "appointmentType", "label": "Loại lịch hẹn", "type": "SELECT", "icon": "IconCalendarEvent",
     "options": [{"label": "Tái khám", "value": "TAI_KHAM", "position": 0, "color": "blue"},
                 {"label": "IUI", "value": "IUI", "position": 1, "color": "green"},
                 {"label": "Lấy trứng", "value": "LAY_TRUNG", "position": 2, "color": "orange"},
                 {"label": "Chuyển phôi", "value": "CHUYEN_PHOI", "position": 3, "color": "purple"},
                 {"label": "Phẫu thuật", "value": "PHAU_THUAT", "position": 4, "color": "red"},
                 {"label": "PRP", "value": "PRP", "position": 5, "color": "turquoise"},
                 {"label": "Sinh nhật", "value": "SINH_NHAT", "position": 6, "color": "yellow"}]},
    {"name": "appointmentTime", "label": "Giờ hẹn", "type": "TEXT", "icon": "IconClock"},
    {"name": "arrivalTime", "label": "Giờ có mặt", "type": "TEXT", "icon": "IconClockHour3"},
    {"name": "reminderDate", "label": "Ngày nhắc lịch", "type": "DATE_TIME", "icon": "IconBell"},
    {"name": "examCode", "label": "Mã khám", "type": "TEXT", "icon": "IconBarcode"},
    {"name": "doctorAdvice", "label": "Lời dặn BS", "type": "TEXT", "icon": "IconMessageDots"},
    {"name": "clinicRoom", "label": "Phòng khám", "type": "TEXT", "icon": "IconBuilding"},
    {"name": "careType", "label": "Loại chăm sóc", "type": "SELECT", "icon": "IconHeartHandshake",
     "options": [{"label": "Nội trú", "value": "NOI_TRU", "position": 0, "color": "blue"},
                 {"label": "CBNM", "value": "CBNM", "position": 1, "color": "green"},
                 {"label": "Thủ thuật", "value": "THU_THUAT", "position": 2, "color": "orange"},
                 {"label": "Tái khám", "value": "TAI_KHAM", "position": 3, "color": "purple"},
                 {"label": "Beta-thai", "value": "BETA_THAI", "position": 4, "color": "red"},
                 {"label": "Thai kỳ", "value": "THAI_KY", "position": 5, "color": "turquoise"}]},
    {"name": "callStatus", "label": "Trạng thái gọi", "type": "SELECT", "icon": "IconPhoneCall",
     "options": [{"label": "Chưa gọi", "value": "CHUA_GOI", "position": 0, "color": "sky"},
                 {"label": "Đã gọi", "value": "DA_GOI", "position": 1, "color": "green"},
                 {"label": "Cần gọi lại", "value": "CAN_GOI_LAI", "position": 2, "color": "orange"},
                 {"label": "Không liên lạc được", "value": "KHONG_LIEN_LAC", "position": 3, "color": "red"}]},
    {"name": "callNote", "label": "Ghi chú cuộc gọi", "type": "TEXT", "icon": "IconNote"},
    {"name": "medication", "label": "Thuốc", "type": "TEXT", "icon": "IconPill"},
    {"name": "doctorName", "label": "BS phụ trách", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "approvalStatus", "label": "Trạng thái duyệt", "type": "SELECT", "icon": "IconCheck",
     "options": [{"label": "Chưa duyệt", "value": "CHUA_DUYET", "position": 0, "color": "sky"},
                 {"label": "Đã duyệt", "value": "DA_DUYET", "position": 1, "color": "green"},
                 {"label": "Từ chối", "value": "TU_CHOI", "position": 2, "color": "red"}]},
]

# View definitions: (name, icon, type, filter_value, columns[(fieldName, size)])
CS_VIEWS = [
    ("CS nội trú", "IconBuildingHospital", "TABLE", "NOI_TRU",
     [("title", 220), ("taskTargets", 180), ("callStatus", 130), ("dueAt", 120), ("callNote", 200), ("medication", 150)]),
    ("CS CBNM", "IconStethoscope", "TABLE", "CBNM",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("medication", 150), ("callStatus", 130), ("callNote", 200)]),
    ("CS thủ thuật", "IconNeedle", "TABLE", "THU_THUAT",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS tái khám", "IconCalendar", "TABLE", "TAI_KHAM",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("medication", 150), ("callStatus", 130), ("callNote", 200), ("dueAt", 120)]),
    ("CS beta-thai", "IconHeartbeat", "TABLE", "BETA_THAI",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("approvalStatus", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS thai kỳ", "IconMoodKid", "TABLE", "THAI_KY",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS theo trạng thái", "IconLayoutKanban", "KANBAN", None, []),
]

# =============================================================================
# OBJECT RENAMES (Vietnamese labels)
# =============================================================================

OBJECT_RENAMES = {
    "company": ("Khoa", "Các Khoa"),
    "person": ("Bệnh nhân", "Bệnh nhân"),
    "task": ("Công việc CS", "Công việc CS"),
    "note": ("Ghi chú", "Ghi chú"),
    "dashboard": ("Báo cáo", "Báo cáo"),
    "workflow": ("Quy trình", "Quy trình"),
}

# =============================================================================
# CUSTOM OBJECTS
# =============================================================================

CUSTOM_OBJECTS = [
    {
        "nameSingular": "treatmentCycle",
        "namePlural": "treatmentCycles",
        "labelSingular": "Chu kỳ điều trị",
        "labelPlural": "Chu kỳ điều trị",
        "icon": "IconHeartbeat",
        "description": "Chu kỳ điều trị IUI/IVF/CBNM của bệnh nhân",
        "fields": [
            {"name": "cycleType", "label": "Loại chu kỳ", "type": "SELECT", "icon": "IconList",
             "options": [{"label": "IUI", "value": "IUI", "position": 0, "color": "blue"},
                         {"label": "IVF", "value": "IVF", "position": 1, "color": "purple"},
                         {"label": "CBNM", "value": "CBNM", "position": 2, "color": "green"},
                         {"label": "PRP", "value": "PRP", "position": 3, "color": "turquoise"}]},
            {"name": "status", "label": "Trạng thái", "type": "SELECT", "icon": "IconCircleCheck",
             "options": [{"label": "Đang điều trị", "value": "DANG_DIEU_TRI", "position": 0, "color": "blue"},
                         {"label": "Hoàn thành", "value": "HOAN_THANH", "position": 1, "color": "green"},
                         {"label": "Đã hủy", "value": "DA_HUY", "position": 2, "color": "red"}]},
            {"name": "doctor", "label": "Bác sĩ", "type": "TEXT", "icon": "IconStethoscope"},
            {"name": "startDate", "label": "Ngày bắt đầu", "type": "DATE", "icon": "IconCalendar"},
            {"name": "procedureDate", "label": "Ngày thủ thuật", "type": "DATE", "icon": "IconCalendar"},
            {"name": "betaTestDate", "label": "Ngày xét nghiệm Beta", "type": "DATE", "icon": "IconCalendar"},
            {"name": "betaResult", "label": "Kết quả Beta", "type": "TEXT", "icon": "IconHeartbeat"},
            {"name": "cancelReason", "label": "Lý do hủy", "type": "TEXT", "icon": "IconAlertTriangle"},
            {"name": "generalNotes", "label": "Ghi chú chung", "type": "TEXT", "icon": "IconNote"},
        ],
        "relation_to_person": {"targetFieldLabel": "Chu kỳ điều trị", "targetFieldIcon": "IconHeartbeat"},
    },
    {
        "nameSingular": "inpatientStay",
        "namePlural": "inpatientStays",
        "labelSingular": "Lần nhập viện",
        "labelPlural": "Lần nhập viện",
        "icon": "IconBuildingHospital",
        "description": "Lần nhập viện nội trú (HTSS, TT/PT, Phụ sản)",
        "fields": [
            {"name": "stayType", "label": "Loại nhập viện", "type": "SELECT", "icon": "IconList",
             "options": [{"label": "HTSS", "value": "HTSS", "position": 0, "color": "blue"},
                         {"label": "PT-TT", "value": "PT_TT", "position": 1, "color": "orange"},
                         {"label": "Sản", "value": "SAN", "position": 2, "color": "green"}]},
            {"name": "admissionDate", "label": "Ngày nhập viện", "type": "DATE", "icon": "IconCalendar"},
            {"name": "dischargeDate", "label": "Ngày xuất viện", "type": "DATE", "icon": "IconCalendar"},
            {"name": "procedureType", "label": "Loại thủ thuật", "type": "SELECT", "icon": "IconList",
             "options": [{"label": "OR (lấy trứng)", "value": "OR", "position": 0, "color": "blue"},
                         {"label": "ET (chuyển phôi)", "value": "ET", "position": 1, "color": "purple"},
                         {"label": "FET", "value": "FET", "position": 2, "color": "turquoise"},
                         {"label": "Mổ lấy thai", "value": "C_SECTION", "position": 3, "color": "red"},
                         {"label": "Khác", "value": "KHAC", "position": 4, "color": "sky"}]},
            {"name": "doctor", "label": "Bác sĩ", "type": "TEXT", "icon": "IconStethoscope"},
            {"name": "room", "label": "Phòng", "type": "TEXT", "icon": "IconBuilding"},
            {"name": "satisfaction", "label": "Hài lòng", "type": "SELECT", "icon": "IconMoodSmile",
             "options": [{"label": "Hài lòng", "value": "HAI_LONG", "position": 0, "color": "green"},
                         {"label": "Tiêu cực", "value": "TIEU_CUC", "position": 1, "color": "red"},
                         {"label": "Chưa khảo sát", "value": "CHUA_KHAO_SAT", "position": 2, "color": "sky"}]},
            {"name": "generalNotes", "label": "Ghi chú chung", "type": "TEXT", "icon": "IconNote"},
        ],
        "relation_to_person": {"targetFieldLabel": "Lần nhập viện", "targetFieldIcon": "IconBuildingHospital"},
    },
]

# =============================================================================
# BVHM HOSPITAL DEPARTMENTS (Base data — always seeded)
# =============================================================================

BVHM_COMPANIES = [
    {"name": "Khoa HTSS", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/khoa-htss"}, "employees": 30,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "Khoa Phu san", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/khoa-phu-san"}, "employees": 20,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "Khoa Nam khoa", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/khoa-nam-khoa"}, "employees": 10,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "Phong kham hanh chinh", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-hanh-chinh"}, "employees": 15,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Ho Cao Cuong", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-ho-cao-cuong"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Ly Thai Loc", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-ly-thai-loc"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Le Huy Binh", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-le-huy-binh"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Minh Tam", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-minh-tam"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Vu Minh Ngoc", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-vu-minh-ngoc"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Nam Khoa", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-nam-khoa"}, "employees": 3,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
    {"name": "PK BS Nhan Quoc Thu", "domainName": {"primaryLinkUrl": "https://benhvienhiemmuonsaigon.vn/pk-nhan-quoc-thu"}, "employees": 5,
     "address": {"addressStreet1": "87 Ly Chieu Hoang", "addressCity": "TP Ho Chi Minh", "addressState": "Phuong Binh Phu", "addressCountry": "Viet Nam"}},
]

# =============================================================================
# DEMO DATA (only seeded with --level demo)
# =============================================================================

DEMO_PATIENTS = [
    {"name": {"firstName": "Lan", "lastName": "Nguyen Thi"}, "emails": {"primaryEmail": "lan.nguyenthi@example.com"},
     "phones": {"primaryPhoneNumber": "912345678", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "TP Ho Chi Minh", "jobTitle": "IVF", "companyName": "Khoa HTSS"},
    {"name": {"firstName": "Thanh", "lastName": "Vo Thi"}, "emails": {"primaryEmail": "thanh.vothi@example.com"},
     "phones": {"primaryPhoneNumber": "967345678", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "Dong Nai", "jobTitle": "IUI", "companyName": "Khoa HTSS"},
    {"name": {"firstName": "Minh", "lastName": "Tran Van"}, "emails": {"primaryEmail": "minh.tranvan@example.com"},
     "phones": {"primaryPhoneNumber": "908765432", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "TP Ho Chi Minh", "jobTitle": "Tu van", "companyName": "Khoa Nam khoa"},
    {"name": {"firstName": "Hung", "lastName": "Nguyen Van"}, "emails": {"primaryEmail": "hung.nguyenvan@example.com"},
     "phones": {"primaryPhoneNumber": "923456789", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "TP Ho Chi Minh", "jobTitle": "Tu van", "companyName": "Khoa Nam khoa"},
    {"name": {"firstName": "Hong", "lastName": "Le Thi"}, "emails": {"primaryEmail": "hong.lethi@example.com"},
     "phones": {"primaryPhoneNumber": "935678901", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "Binh Duong", "jobTitle": "Mang thai", "companyName": "Khoa Phu san"},
    {"name": {"firstName": "Ngoc", "lastName": "Dang Thi"}, "emails": {"primaryEmail": "ngoc.dangthi@example.com"},
     "phones": {"primaryPhoneNumber": "956789012", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "Long An", "jobTitle": "Theo doi thai", "companyName": "Khoa Phu san"},
    {"name": {"firstName": "Yen", "lastName": "Hoang Thi"}, "emails": {"primaryEmail": "yen.hoangthi@example.com"},
     "phones": {"primaryPhoneNumber": "978901234", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "TP Ho Chi Minh", "jobTitle": "Sau sinh", "companyName": "Khoa Phu san"},
    {"name": {"firstName": "Mai", "lastName": "Pham Thi"}, "emails": {"primaryEmail": "mai.phamthi@example.com"},
     "phones": {"primaryPhoneNumber": "945012345", "primaryPhoneCountryCode": "VN", "primaryPhoneCallingCode": "+84"},
     "city": "TP Ho Chi Minh", "jobTitle": "Kham", "companyName": "PK BS Ho Cao Cuong"},
]

DEMO_TASKS = [
    {"title": "CS noi tru - Lan Nguyen Thi - xuat vien sau ET", "careType": "NOI_TRU", "callStatus": "CHUA_GOI", "medication": "Progesterone 400mg x2/ngay", "daysFromNow": 0, "patientEmail": "lan.nguyenthi@example.com"},
    {"title": "CS noi tru - Yen Hoang Thi - xuat vien sau sinh", "careType": "NOI_TRU", "callStatus": "DA_GOI", "medication": None, "daysFromNow": -1, "patientEmail": "yen.hoangthi@example.com"},
    {"title": "CS CBNM - Hung Nguyen Van - benh nhan moi", "careType": "CBNM", "callStatus": "CHUA_GOI", "medication": None, "daysFromNow": 1, "patientEmail": "hung.nguyenvan@example.com"},
    {"title": "CS CBNM - Minh Tran Van - benh nhan moi", "careType": "CBNM", "callStatus": "KHONG_LIEN_LAC", "callNote": "Goi 3 lan khong nghe may", "medication": None, "daysFromNow": 1, "patientEmail": "minh.tranvan@example.com"},
    {"title": "Nhac hen thu thuat - Lan - Lay trung ngay mai 7h30", "careType": "THU_THUAT", "callStatus": "DA_GOI", "medication": "Ovitrelle 250mcg tiem 21h", "daysFromNow": 1, "patientEmail": "lan.nguyenthi@example.com"},
    {"title": "Nhac hen thu thuat - Thanh - Bom IUI ngay mai 9h", "careType": "THU_THUAT", "callStatus": "CHUA_GOI", "medication": "Clomiphene 50mg", "daysFromNow": 1, "patientEmail": "thanh.vothi@example.com"},
    {"title": "Goi tai kham - Mai - PK2 BS.Ha 10h", "careType": "TAI_KHAM", "callStatus": "CHUA_GOI", "medication": None, "daysFromNow": 2, "patientEmail": "mai.phamthi@example.com"},
    {"title": "Goi tai kham - Thanh - PK1 BS.Long 14h", "careType": "TAI_KHAM", "callStatus": "CAN_GOI_LAI", "medication": None, "daysFromNow": 2, "patientEmail": "thanh.vothi@example.com"},
    {"title": "CS beta - Lan - IVF 14 ngay sau chuyen phoi", "careType": "BETA_THAI", "callStatus": "CHUA_GOI", "medication": "Progesterone 400mg x2/ngay", "daysFromNow": 3, "patientEmail": "lan.nguyenthi@example.com"},
    {"title": "CS beta - Thanh - IUI ngay sau bom", "careType": "BETA_THAI", "callStatus": "DA_GOI", "medication": None, "daysFromNow": -2, "patientEmail": "thanh.vothi@example.com"},
    {"title": "CS thai ky thang 3 - Hong - Tuan 20", "careType": "THAI_KY", "callStatus": "CHUA_GOI", "medication": "Acid folic 5mg/ngay", "daysFromNow": 5, "patientEmail": "hong.lethi@example.com"},
    {"title": "CS thai ky thang 3 - Ngoc - Tuan 12", "careType": "THAI_KY", "callStatus": "DA_GOI", "medication": "Acid folic 5mg/ngay", "daysFromNow": -3, "patientEmail": "ngoc.dangthi@example.com"},
]

DEMO_NOTES = [
    {"title": "Lan - Ket qua sieu am dau ky", "body": "Sieu am ngay 15/03: Noi mac tu cung 9mm, nang noang trai 18mm. Chi dinh tiem Ovitrelle 21h toi nay, hen lay trung sau 36h.", "patientEmail": "lan.nguyenthi@example.com"},
    {"title": "Thanh - Ghi chu tu van IUI", "body": "BN duoc tu van quy trinh bom IUI. Lich hen: xet nghiem hormone ngay 3 chu ky, sieu am theo doi nang noang tu ngay 10.", "patientEmail": "thanh.vothi@example.com"},
    {"title": "Minh - Ket qua tinh dich do", "body": "Mat do: 15 trieu/ml, di dong A+B: 35%. BS khuyen loc rua tinh trung va IUI ho tro. Hen tai kham sau 2 tuan.", "patientEmail": "minh.tranvan@example.com"},
    {"title": "Hung - Lan kham dau tien", "body": "BN den kham lan dau, than chu: vo chong hiem muon 2 nam. Chi dinh xet nghiem hormone, sieu am, tinh dich do. Hen tra ket qua 1 tuan.", "patientEmail": "hung.nguyenvan@example.com"},
    {"title": "Hong - Theo doi thai tuan 20", "body": "Sieu am hinh thai hoc: thai phat trien binh thuong, can nang uoc tinh 350g. Khong phat hien bat thuong. Hen tai kham 4 tuan.", "patientEmail": "hong.lethi@example.com"},
    {"title": "Ngoc - Ket qua Double Test", "body": "Ket qua Double Test: nguy co thap. PAPP-A va free beta-hCG trong gioi han binh thuong. Tiep tuc theo doi thai ky dinh ky.", "patientEmail": "ngoc.dangthi@example.com"},
    {"title": "Yen - Ghi chu xuat vien sau sinh", "body": "San phu xuat vien ngay 2 sau sinh thuong. Be 3.2kg, bu me tot. Dan do: tai kham sau 1 tuan, theo doi san dich, giu ve sinh.", "patientEmail": "yen.hoangthi@example.com"},
    {"title": "Mai - Ket qua kham phu khoa", "body": "Kham phu khoa dinh ky: PAP smear binh thuong, sieu am tu cung phan phu khong bat thuong. Hen tai kham sau 6 thang.", "patientEmail": "mai.phamthi@example.com"},
]

# =============================================================================
# DEMO: TREATMENT CYCLES (Chu kỳ điều trị)
# =============================================================================

DEMO_TREATMENT_CYCLES = [
    {"cycleType": "IVF", "status": "DANG_DIEU_TRI", "doctor": "BS Hồ Cao Cường", "startDate": "2026-02-01", "procedureDate": "2026-03-15", "patientEmail": "lan.nguyenthi@example.com"},
    {"cycleType": "IUI", "status": "DANG_DIEU_TRI", "doctor": "BS Lý Thái Lộc", "startDate": "2026-03-01", "procedureDate": "2026-03-20", "patientEmail": "thanh.vothi@example.com"},
    {"cycleType": "IVF", "status": "HOAN_THANH", "doctor": "BS Hồ Cao Cường", "startDate": "2025-10-01", "procedureDate": "2025-11-15", "betaResult": "hCG 1250 mIU/mL - Dương tính", "patientEmail": "hong.lethi@example.com"},
    {"cycleType": "IUI", "status": "DA_HUY", "doctor": "BS Minh Tâm", "startDate": "2026-01-15", "cancelReason": "Nang noãn không đáp ứng thuốc", "patientEmail": "ngoc.dangthi@example.com"},
    {"cycleType": "CBNM", "status": "DANG_DIEU_TRI", "doctor": "BS Lê Huy Bình", "startDate": "2026-03-10", "patientEmail": "minh.tranvan@example.com"},
    {"cycleType": "IVF", "status": "HOAN_THANH", "doctor": "BS Vũ Minh Ngọc", "startDate": "2025-08-01", "procedureDate": "2025-09-10", "betaResult": "hCG 890 mIU/mL - Dương tính", "patientEmail": "yen.hoangthi@example.com"},
]

# =============================================================================
# DEMO: INPATIENT STAYS (Lần nhập viện)
# =============================================================================

DEMO_INPATIENT_STAYS = [
    {"stayType": "HTSS", "admissionDate": "2026-03-14", "dischargeDate": "2026-03-16", "procedureType": "OR", "doctor": "BS Hồ Cao Cường", "room": "201", "satisfaction": "HAI_LONG", "patientEmail": "lan.nguyenthi@example.com"},
    {"stayType": "SAN", "admissionDate": "2026-03-10", "dischargeDate": "2026-03-12", "procedureType": "C_SECTION", "doctor": "BS Lê Huy Bình", "room": "305", "satisfaction": "HAI_LONG", "patientEmail": "yen.hoangthi@example.com"},
    {"stayType": "HTSS", "admissionDate": "2026-03-19", "procedureType": "ET", "doctor": "BS Lý Thái Lộc", "room": "203", "satisfaction": "CHUA_KHAO_SAT", "patientEmail": "thanh.vothi@example.com"},
    {"stayType": "PT_TT", "admissionDate": "2026-02-20", "dischargeDate": "2026-02-21", "procedureType": "OR", "doctor": "BS Minh Tâm", "room": "202", "satisfaction": "HAI_LONG", "patientEmail": "ngoc.dangthi@example.com"},
]

# Navigation items to remove (by view name pattern)
NAV_ITEMS_TO_REMOVE = ["Opportunities", "Workflow Runs", "Workflow Versions"]


# =============================================================================
# API CLIENT
# =============================================================================

class TwentyAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(timeout=60)
        self.token = None

    # -- Auth --

    def signup_and_activate(self, email: str, password: str, workspace_name: str = "BVHM"):
        """Sign up a new user and activate the workspace."""
        print(f"   Signing up {email}...")
        r = self._gql_unauth(
            'mutation($email: String!, $password: String!) { signUpWithPassword(email: $email, password: $password) '
            '{ tokens { accessToken { token } } } }',
            {"email": email, "password": password},
        )
        self.token = r["data"]["signUpWithPassword"]["tokens"]["accessToken"]["token"]

        print(f"   Activating workspace '{workspace_name}'...")
        self._gql(
            'mutation($name: String!) { activateWorkspace(data: { displayName: $name }) { id } }',
            {"name": workspace_name},
        )

    def login(self, email: str, password: str):
        """Two-step auth: getLoginToken -> getAuthTokens. Account must exist."""
        origin = self.base_url
        r = self._gql_unauth(
            'mutation($email: String!, $password: String!, $origin: String!) '
            '{ getLoginTokenFromCredentials(email: $email, password: $password, origin: $origin) '
            '{ loginToken { token } } }',
            {"email": email, "password": password, "origin": origin},
        )
        login_token = r["data"]["getLoginTokenFromCredentials"]["loginToken"]["token"]

        r = self._gql_unauth(
            'mutation($loginToken: String!, $origin: String!) '
            '{ getAuthTokensFromLoginToken(loginToken: $loginToken, origin: $origin) '
            '{ tokens { accessOrWorkspaceAgnosticToken { token } } } }',
            {"loginToken": login_token, "origin": origin},
        )
        self.token = r["data"]["getAuthTokensFromLoginToken"]["tokens"]["accessOrWorkspaceAgnosticToken"]["token"]

    def ensure_auth(self, email: str, password: str):
        """Login to existing workspace. Account must be created via UI first."""
        self.login(email, password)
        print("   Logged in OK")

    # -- Low-level --

    def _headers(self, auth: bool = True):
        h = {"Content-Type": "application/json"}
        if auth and self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _gql_unauth(self, query: str, variables: dict = None):
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.client.post(f"{self.base_url}/metadata", json=body, headers=self._headers(auth=False))
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data

    def _gql(self, query: str, variables: dict = None):
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.client.post(f"{self.base_url}/metadata", json=body, headers=self._headers())
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data

    def _core_gql(self, query: str, variables: dict = None):
        body = {"query": query}
        if variables:
            body["variables"] = variables
        r = self.client.post(f"{self.base_url}/graphql", json=body, headers=self._headers())
        data = r.json()
        if "errors" in data and data.get("data") is None:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data

    def rest(self, method: str, path: str, data: dict = None) -> dict:
        url = f"{self.base_url}/rest/{path}"
        r = self.client.request(method, url, json=data, headers=self._headers())
        if r.status_code >= 400:
            raise Exception(f"REST {method} {path} -> {r.status_code}: {r.text[:200]}")
        return r.json() if r.text else {}

    # -- Metadata helpers --

    def get_object_id(self, name: str) -> str:
        r = self._gql('query { objects(paging: { first: 100 }) { edges { node { id nameSingular } } } }')
        for edge in r["data"]["objects"]["edges"]:
            if edge["node"]["nameSingular"] == name:
                return edge["node"]["id"]
        raise Exception(f"Object '{name}' not found")

    def get_fields(self, object_id: str) -> dict[str, str]:
        r = self._gql(f'query {{ object(id: "{object_id}") {{ fields(paging: {{ first: 200 }}) {{ edges {{ node {{ id name }} }} }} }} }}')
        return {e["node"]["name"]: e["node"]["id"] for e in r["data"]["object"]["fields"]["edges"]}

    def create_field(self, object_id: str, field: dict) -> str | None:
        field_input = {
            "objectMetadataId": object_id,
            "name": field["name"],
            "label": field["label"],
            "type": field["type"],
            "icon": field.get("icon", "IconList"),
            "isNullable": True,
            "isLabelSyncedWithName": False,
        }
        if "options" in field:
            field_input["options"] = field["options"]
        if "description" in field:
            field_input["description"] = field["description"]
        try:
            r = self._gql(
                "mutation CreateField($input: CreateOneFieldMetadataInput!) { createOneField(input: $input) { id name } }",
                {"input": {"field": field_input}},
            )
            return r["data"]["createOneField"]["id"]
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                return None
            raise

    def deactivate_object(self, object_id: str):
        self._gql(f'mutation {{ updateOneObject(input: {{ id: "{object_id}", update: {{ isActive: false }} }}) {{ id }} }}')

    def create_view(self, object_id: str, name: str, icon: str, vtype: str = "TABLE", group_by_field_id: str = None) -> str | None:
        extra = ""
        if group_by_field_id:
            extra = f', mainGroupByFieldMetadataId: "{group_by_field_id}"'
        try:
            r = self._gql(f'mutation {{ createView(input: {{ name: "{name}", objectMetadataId: "{object_id}", type: {vtype}, icon: "{icon}"{extra} }}) {{ id }} }}')
            return r["data"]["createView"]["id"]
        except Exception as e:
            if "already exists" in str(e).lower():
                return None
            raise

    def create_view_filter(self, view_id: str, field_id: str, value: str):
        self._gql(
            "mutation($input: CreateViewFilterInput!) { createViewFilter(input: $input) { id } }",
            {"input": {"viewId": view_id, "fieldMetadataId": field_id, "operand": "IS", "value": value}},
        )

    def create_view_field(self, view_id: str, field_id: str, position: int, size: int):
        self._gql(
            "mutation($input: CreateViewFieldInput!) { createViewField(input: $input) { id } }",
            {"input": {"viewId": view_id, "fieldMetadataId": field_id, "position": position, "size": size, "isVisible": True}},
        )

    def get_nav_items(self) -> list[dict]:
        r = self._gql('query { navigationMenuItems { id name type targetObjectMetadataId } }')
        return r["data"]["navigationMenuItems"]

    def get_object_name_map(self) -> dict[str, str]:
        """Returns {objectMetadataId: nameSingular} including inactive objects."""
        r = self._gql('query { objects(paging: { first: 100 }) { edges { node { id nameSingular } } } }')
        return {e["node"]["id"]: e["node"]["nameSingular"] for e in r["data"]["objects"]["edges"]}

    def delete_nav_item(self, item_id: str):
        self._gql(f'mutation {{ deleteNavigationMenuItem(id: "{item_id}") {{ id }} }}')


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

def cleanup_defaults(api: TwentyAPI):
    """Delete ALL existing companies, people, opportunities, tasks, notes."""
    print("\n2. Cleaning up all existing data...")

    for obj_name in ("taskTargets", "noteTargets", "tasks", "notes", "treatmentCycles", "inpatientStays", "opportunities", "people", "companies"):
        total = 0
        while True:
            try:
                resp = api.rest("GET", f"{obj_name}?limit=60")
                records = resp.get("data", {}).get(obj_name, [])
                if not records:
                    break
                for r in records:
                    try:
                        api.rest("DELETE", f"{obj_name}/{r['id']}")
                        total += 1
                    except Exception:
                        pass
                if len(records) < 60:
                    break
            except Exception:
                break
        if total:
            print(f"   Deleted {total} {obj_name}")
        else:
            print(f"   No {obj_name} to delete")


def deactivate_opportunity(api: TwentyAPI):
    """Deactivate the Opportunity object."""
    print("\n3. Deactivating Opportunities...")
    try:
        opp_id = api.get_object_id("opportunity")
        api.deactivate_object(opp_id)
        print("   OK")
    except Exception as e:
        print(f"   Skip: {e}")


def cleanup_navigation(api: TwentyAPI):
    """Remove unwanted navigation menu items."""
    print("\n4. Cleaning up navigation...")
    hide_objects = {"opportunity", "workflowRun", "workflowVersion"}
    removed = 0
    try:
        obj_map = api.get_object_name_map()
        items = api.get_nav_items()
        for item in items:
            obj_name = obj_map.get(item.get("targetObjectMetadataId"), "")
            if obj_name in hide_objects:
                try:
                    api.delete_nav_item(item["id"])
                    removed += 1
                    print(f"   Removed: {obj_name}")
                except Exception as e:
                    print(f"   Failed to remove {obj_name}: {e}")
    except Exception as e:
        print(f"   Navigation cleanup: {e}")
    if not removed:
        print("   No items to remove")


def cleanup_workflows(api: TwentyAPI):
    """Delete default Quick Lead workflow."""
    print("\n4b. Removing default workflows...")
    try:
        resp = api.rest("GET", "workflows?limit=20")
        workflows = resp.get("data", {}).get("workflows", [])
        for wf in workflows:
            if wf.get("name") == "Quick Lead":
                api.rest("DELETE", f"workflows/{wf['id']}")
                print(f"   Removed: Quick Lead")
                return
        print("   No Quick Lead workflow found")
    except Exception as e:
        print(f"   Workflow cleanup: {e}")


def rename_objects(api: TwentyAPI):
    """Rename standard objects to Vietnamese labels."""
    print("\n4c. Renaming objects to Vietnamese...")
    for obj_name, (label_s, label_p) in OBJECT_RENAMES.items():
        try:
            obj_id = api.get_object_id(obj_name)
            api._gql(
                'mutation($input: UpdateOneObjectInput!) { updateOneObject(input: $input) { id } }',
                {"input": {"id": obj_id, "update": {"labelSingular": label_s, "labelPlural": label_p}}},
            )
            print(f"   {obj_name} → {label_s}")
        except Exception as e:
            print(f"   {obj_name}: {e}")


def create_custom_objects(api: TwentyAPI):
    """Create Treatment Cycle and Inpatient Stay custom objects with fields and relations."""
    print(f"\n5b. Creating custom objects ({len(CUSTOM_OBJECTS)})...")
    person_id = api.get_object_id("person")

    for obj_def in CUSTOM_OBJECTS:
        # Create object
        try:
            r = api._gql(
                'mutation($input: CreateOneObjectInput!) { createOneObject(input: $input) { id nameSingular } }',
                {"input": {"object": {
                    "nameSingular": obj_def["nameSingular"],
                    "namePlural": obj_def["namePlural"],
                    "labelSingular": obj_def["labelSingular"],
                    "labelPlural": obj_def["labelPlural"],
                    "icon": obj_def.get("icon", "IconList"),
                    "description": obj_def.get("description", ""),
                }}},
            )
            obj_id = r["data"]["createOneObject"]["id"]
            print(f"   Created: {obj_def['labelSingular']} ({obj_id[:12]}..)")
        except Exception as e:
            err = str(e).lower()
            if "already exists" in err or "duplicate" in err or "validation error" in err:
                try:
                    obj_id = api.get_object_id(obj_def["nameSingular"])
                    print(f"   Exists: {obj_def['labelSingular']}")
                except Exception:
                    print(f"   FAIL creating {obj_def['labelSingular']}: {e}")
                    continue
            else:
                print(f"   FAIL creating {obj_def['labelSingular']}: {e}")
                continue

        # Create fields
        existing = api.get_fields(obj_id)
        created = 0
        for f in obj_def.get("fields", []):
            if f["name"] not in existing:
                if api.create_field(obj_id, f):
                    created += 1
        if created:
            print(f"      + {created} fields")

        # Create relation to Person
        rel = obj_def.get("relation_to_person")
        if rel:
            existing = api.get_fields(obj_id)
            if "person" not in existing:
                try:
                    api._gql(
                        'mutation($input: CreateOneFieldMetadataInput!) { createOneField(input: $input) { id } }',
                        {"input": {"field": {
                            "name": "person",
                            "label": "Bệnh nhân",
                            "type": "RELATION",
                            "objectMetadataId": obj_id,
                            "icon": "IconUser",
                            "relationCreationPayload": {
                                "type": "MANY_TO_ONE",
                                "targetObjectMetadataId": person_id,
                                "targetFieldLabel": rel["targetFieldLabel"],
                                "targetFieldIcon": rel["targetFieldIcon"],
                            },
                        }}},
                    )
                    print(f"      + relation → Bệnh nhân")
                except Exception as e:
                    if "already exists" not in str(e).lower():
                        print(f"      Relation fail: {e}")


def create_workflows(api: TwentyAPI):
    """Create BVHM draft workflows."""
    print("\n8b. Creating BVHM workflows...")
    workflow_defs = [
        ("Thai kỳ Auto-Create", "Tự tạo task CS thai kỳ khi BN chuyển giai đoạn"),
        ("Thai kỳ Recurring", "Tự tạo task mới khi hoàn thành gọi CS thai kỳ"),
        ("Cảnh báo task quá hạn", "Tìm task quá hạn chưa xử lý mỗi ngày"),
    ]

    try:
        existing = api.rest("GET", "workflows?limit=20")
        existing_names = {wf["name"] for wf in existing.get("data", {}).get("workflows", [])}
    except Exception:
        existing_names = set()

    for name, desc in workflow_defs:
        if name in existing_names:
            print(f"   Exists: {name}")
            continue
        try:
            api.rest("POST", "workflows", {"name": name})
            print(f"   Created (draft): {name}")
        except Exception as e:
            print(f"   FAIL: {name} — {e}")


def create_custom_fields(api: TwentyAPI):
    """Create custom fields on Person and Task objects."""
    print(f"\n5. Creating Person fields ({len(PERSON_FIELDS)})...")
    person_id = api.get_object_id("person")
    existing = api.get_fields(person_id)
    created = sum(1 for f in PERSON_FIELDS if f["name"] not in existing and api.create_field(person_id, f))
    print(f"   Created {created}, skipped {len(PERSON_FIELDS) - created}")

    print(f"\n6. Creating Task fields ({len(TASK_FIELDS)})...")
    task_id = api.get_object_id("task")
    existing = api.get_fields(task_id)
    created = sum(1 for f in TASK_FIELDS if f["name"] not in existing and api.create_field(task_id, f))
    print(f"   Created {created}, skipped {len(TASK_FIELDS) - created}")


def create_views(api: TwentyAPI):
    """Create the 7 CS views with filters and columns."""
    print(f"\n7. Creating CS views ({len(CS_VIEWS)})...")
    task_id = api.get_object_id("task")
    task_fields = api.get_fields(task_id)

    for name, icon, vtype, filter_val, columns in CS_VIEWS:
        group_by = task_fields.get("callStatus") if vtype == "KANBAN" else None

        try:
            vid = api.create_view(task_id, name, icon, vtype, group_by)
        except Exception as e:
            print(f"   FAIL: {name} - {e}")
            continue

        if not vid:
            print(f"   SKIP: {name} (exists)")
            continue

        print(f"   OK: {name}")

        if filter_val and "careType" in task_fields:
            try:
                api.create_view_filter(vid, task_fields["careType"], f'["{filter_val}"]')
            except Exception as e:
                print(f"      Filter fail: {e}")

        for pos, (field_name, size) in enumerate(columns):
            fid = task_fields.get(field_name)
            if fid:
                try:
                    api.create_view_field(vid, fid, pos, size)
                except Exception as e:
                    print(f"      Column {field_name} fail: {e}")


def seed_companies(api: TwentyAPI):
    """Seed BVHM hospital departments."""
    print(f"\n8. Seeding BVHM departments ({len(BVHM_COMPANIES)})...")
    created = 0
    for company in BVHM_COMPANIES:
        try:
            api.rest("POST", "companies", company)
            created += 1
        except Exception as e:
            if "duplicate" in str(e).lower() or "already" in str(e).lower():
                continue
            print(f"   FAIL: {company['name']} - {e}")
    print(f"   Created {created} departments")


def seed_demo_data(api: TwentyAPI):
    """Seed demo patients, tasks, and notes."""
    # Build company name -> id map
    companies_resp = api.rest("GET", "companies?limit=50")
    company_map = {c["name"]: c["id"] for c in companies_resp.get("data", {}).get("companies", [])}

    # Seed patients
    print(f"\n9. Seeding demo patients ({len(DEMO_PATIENTS)})...")
    patient_map = {}  # email -> id
    for p in DEMO_PATIENTS:
        data = {
            "name": p["name"],
            "emails": p["emails"],
            "phones": p["phones"],
            "city": p["city"],
            "jobTitle": p["jobTitle"],
        }
        company_id = company_map.get(p["companyName"])
        if company_id:
            data["companyId"] = company_id
        try:
            result = api.rest("POST", "people", data)
            pid = result.get("data", {}).get("createPerson", {}).get("id") or result.get("data", {}).get("person", {}).get("id")
            if not pid:
                # Try alternative response format
                pid = result.get("id")
            if pid:
                patient_map[p["emails"]["primaryEmail"]] = pid
        except Exception as e:
            print(f"   FAIL: {p['name']['firstName']} - {e}")
    print(f"   Created {len(patient_map)} patients")

    # Seed tasks
    print(f"\n10. Seeding demo tasks ({len(DEMO_TASKS)})...")
    now = datetime.utcnow()
    task_ids = []
    for t in DEMO_TASKS:
        due = now + timedelta(days=t["daysFromNow"])
        data = {
            "title": t["title"],
            "status": "TODO",
            "dueAt": due.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "careType": t["careType"],
            "callStatus": t["callStatus"],
        }
        if t.get("callNote"):
            data["callNote"] = t["callNote"]
        if t.get("medication"):
            data["medication"] = t["medication"]
        try:
            result = api.rest("POST", "tasks", data)
            tid = result.get("data", {}).get("createTask", {}).get("id") or result.get("id")
            if tid:
                task_ids.append((tid, t.get("patientEmail")))
        except Exception as e:
            print(f"   FAIL: {t['title'][:40]} - {e}")
    print(f"   Created {len(task_ids)} tasks")

    # Link tasks to patients via taskTargets
    print("\n11. Linking tasks to patients...")
    linked = 0
    for task_id, patient_email in task_ids:
        patient_id = patient_map.get(patient_email)
        if patient_id:
            try:
                api.rest("POST", "taskTargets", {"taskId": task_id, "targetPersonId": patient_id})
                linked += 1
            except Exception as e:
                print(f"   Link fail: {e}")
    print(f"   Linked {linked} task-patient pairs")

    # Seed notes
    print(f"\n12. Seeding demo notes ({len(DEMO_NOTES)})...")
    note_ids = []
    for n in DEMO_NOTES:
        try:
            result = api.rest("POST", "notes", {"title": n["title"], "bodyV2": {"markdown": n["body"]}})
            nid = result.get("data", {}).get("createNote", {}).get("id") or result.get("id")
            if nid:
                note_ids.append((nid, n["patientEmail"]))
        except Exception as e:
            print(f"   FAIL: {n['title'][:40]} - {e}")
    print(f"   Created {len(note_ids)} notes")

    # Link notes to patients
    print("\n13. Linking notes to patients...")
    linked = 0
    for note_id, patient_email in note_ids:
        patient_id = patient_map.get(patient_email)
        if patient_id:
            try:
                api.rest("POST", "noteTargets", {"noteId": note_id, "targetPersonId": patient_id})
                linked += 1
            except Exception as e:
                print(f"   Link fail: {e}")
    print(f"   Linked {linked} note-patient pairs")

    # Seed treatment cycles
    print(f"\n14. Seeding treatment cycles ({len(DEMO_TREATMENT_CYCLES)})...")
    created_cycles = 0
    for tc in DEMO_TREATMENT_CYCLES:
        patient_id = patient_map.get(tc["patientEmail"])
        data = {k: v for k, v in tc.items() if k != "patientEmail" and v is not None}
        if patient_id:
            data["personId"] = patient_id
        try:
            api.rest("POST", "treatmentCycles", data)
            created_cycles += 1
        except Exception as e:
            print(f"   FAIL: {tc['cycleType']} for {tc['patientEmail']}: {e}")
    print(f"   Created {created_cycles} treatment cycles")

    # Seed inpatient stays
    print(f"\n15. Seeding inpatient stays ({len(DEMO_INPATIENT_STAYS)})...")
    created_stays = 0
    for stay in DEMO_INPATIENT_STAYS:
        patient_id = patient_map.get(stay["patientEmail"])
        data = {k: v for k, v in stay.items() if k != "patientEmail" and v is not None}
        if patient_id:
            data["personId"] = patient_id
        try:
            api.rest("POST", "inpatientStays", data)
            created_stays += 1
        except Exception as e:
            print(f"   FAIL: {stay['stayType']} for {stay['patientEmail']}: {e}")
    print(f"   Created {created_stays} inpatient stays")


def create_dashboard(api: TwentyAPI):
    """Create BVHM CSKH Dashboard with charts."""
    print("\n16. Creating BVHM Dashboard...")

    # Get field IDs we need for charts
    task_obj_id = api.get_object_id("task")
    person_obj_id = api.get_object_id("person")
    task_fields = api.get_fields(task_obj_id)
    person_fields = api.get_fields(person_obj_id)

    care_type_field = task_fields.get("careType")
    call_status_field = task_fields.get("callStatus")
    due_at_field = task_fields.get("dueAt")
    task_id_field = task_fields.get("id")
    person_id_field = person_fields.get("id")
    treatment_stage_field = person_fields.get("treatmentStage")

    if not all([care_type_field, call_status_field, task_id_field, person_id_field]):
        print("   Missing required fields for dashboard, skipping")
        return

    # Delete existing BVHM dashboards + default dashboard
    try:
        existing = api.rest("GET", "dashboards?limit=10")
        dashboards = existing.get("data", {}).get("dashboards", [])
        for d in dashboards:
            try:
                api.rest("DELETE", f"dashboards/{d['id']}")
            except Exception:
                pass
        if dashboards:
            print(f"   Cleaned {len(dashboards)} existing dashboards")
    except Exception:
        pass

    # Step 1: Create PageLayout via metadata API
    try:
        layout_r = api._gql(
            'mutation($input: CreatePageLayoutInput!) { createPageLayout(input: $input) { id } }',
            {"input": {
                "name": "Báo cáo CSKH",
                "type": "DASHBOARD",
            }},
        )
        layout_id = layout_r["data"]["createPageLayout"]["id"]
    except Exception as e:
        print(f"   Failed to create page layout: {e}")
        return

    # Step 2: Create tab
    try:
        tab_r = api._gql(
            'mutation($input: CreatePageLayoutTabInput!) { createPageLayoutTab(input: $input) { id } }',
            {"input": {
                "pageLayoutId": layout_id,
                "title": "Tổng quan",
                "position": 0,
            }},
        )
        tab_id = tab_r["data"]["createPageLayoutTab"]["id"]
    except Exception as e:
        print(f"   Failed to create tab: {e}")
        return

    # Step 3: Create widgets
    widgets = [
        # Row 0: KPI cards
        {
            "title": "Tổng bệnh nhân",
            "type": "GRAPH",
            "objectMetadataId": person_obj_id,
            "gridPosition": {"row": 0, "column": 0, "rowSpan": 2, "columnSpan": 3},
            "configuration": {
                "configurationType": "AGGREGATE_CHART",
                "aggregateFieldMetadataId": person_id_field,
                "aggregateOperation": "COUNT",
                "displayDataLabel": True,
            },
        },
        {
            "title": "Tổng công việc CS",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 0, "column": 3, "rowSpan": 2, "columnSpan": 3},
            "configuration": {
                "configurationType": "AGGREGATE_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "displayDataLabel": True,
            },
        },
        {
            "title": "Chưa gọi",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 0, "column": 6, "rowSpan": 2, "columnSpan": 3},
            "configuration": {
                "configurationType": "AGGREGATE_CHART",
                "aggregateFieldMetadataId": call_status_field,
                "aggregateOperation": "COUNT_EMPTY",
                "displayDataLabel": True,
                "label": "Chưa gọi",
            },
        },
        # Row 2: Charts
        {
            "title": "Công việc theo loại chăm sóc",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 2, "column": 0, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "PIE_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "groupByFieldMetadataId": care_type_field,
                "displayDataLabel": True,
                "displayLegend": True,
                "showCenterMetric": True,
            },
        },
        {
            "title": "Trạng thái cuộc gọi",
            "type": "GRAPH",
            "objectMetadataId": task_obj_id,
            "gridPosition": {"row": 2, "column": 6, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "BAR_CHART",
                "aggregateFieldMetadataId": task_id_field,
                "aggregateOperation": "COUNT",
                "primaryAxisGroupByFieldMetadataId": call_status_field,
                "layout": "VERTICAL",
                "displayDataLabel": True,
                "displayLegend": False,
            },
        },
    ]

    # Add treatmentStage chart if field exists
    if treatment_stage_field:
        widgets.append({
            "title": "Bệnh nhân theo giai đoạn điều trị",
            "type": "GRAPH",
            "objectMetadataId": person_obj_id,
            "gridPosition": {"row": 8, "column": 0, "rowSpan": 6, "columnSpan": 6},
            "configuration": {
                "configurationType": "PIE_CHART",
                "aggregateFieldMetadataId": person_id_field,
                "aggregateOperation": "COUNT",
                "groupByFieldMetadataId": treatment_stage_field,
                "displayDataLabel": True,
                "displayLegend": True,
                "showCenterMetric": True,
            },
        })

    created_widgets = 0
    for w in widgets:
        try:
            widget_input = {
                "pageLayoutTabId": tab_id,
                "title": w["title"],
                "type": w["type"],
                "gridPosition": w["gridPosition"],
                "configuration": w["configuration"],
            }
            if w.get("objectMetadataId"):
                widget_input["objectMetadataId"] = w["objectMetadataId"]
            api._gql(
                'mutation($input: CreatePageLayoutWidgetInput!) { createPageLayoutWidget(input: $input) { id } }',
                {"input": widget_input},
            )
            created_widgets += 1
        except Exception as e:
            print(f"   Widget '{w['title']}': {e}")

    # Step 4: Create dashboard record linking to page layout
    try:
        api.rest("POST", "dashboards", {"title": "Báo cáo CSKH", "pageLayoutId": layout_id})
        print(f"   Created dashboard with {created_widgets} widgets")
    except Exception as e:
        print(f"   Dashboard record: {e}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="BVHM Hospital CRM Setup")
    parser.add_argument("--url", default="http://localhost:3000", help="Twenty server URL")
    parser.add_argument("--email", default="admin@bvhm.vn", help="Admin email")
    parser.add_argument("--password", default=None, help="Admin password (default: same as email)")
    parser.add_argument("--level", choices=["base", "demo"], default="demo", help="Setup level: base (no patient data) or demo (with sample data)")
    args = parser.parse_args()

    password = args.password or args.email
    api = TwentyAPI(args.url)

    print("=" * 50)
    print("BVHM Hospital CRM Setup")
    print("=" * 50)
    print(f"Server: {args.url}")
    print(f"Level:  {args.level}")

    # 1. Auth
    print("\n1. Authenticating...")
    api.ensure_auth(args.email, password)

    # Base setup (always runs)
    cleanup_defaults(api)
    cleanup_workflows(api)
    deactivate_opportunity(api)
    cleanup_navigation(api)
    rename_objects(api)
    create_custom_fields(api)
    create_custom_objects(api)
    create_views(api)
    seed_companies(api)
    create_workflows(api)

    # Demo data (only with --level demo)
    if args.level == "demo":
        seed_demo_data(api)

    # Dashboard (always)
    create_dashboard(api)

    print("\n" + "=" * 50)
    print(f"Setup complete! Level: {args.level}")
    print(f"Open: {args.url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
