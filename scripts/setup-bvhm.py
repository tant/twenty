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
    {"name": "pid", "label": "PID", "type": "TEXT", "icon": "IconId", "description": "Ma benh nhan tu HIS"},
    {"name": "yearOfBirth", "label": "Nam sinh", "type": "NUMBER", "icon": "IconCalendar"},
    {"name": "dateOfBirth", "label": "Ngay sinh", "type": "DATE", "icon": "IconCake"},
    {"name": "gender", "label": "Gioi tinh", "type": "SELECT", "icon": "IconGenderBigender",
     "options": [{"label": "Nam", "value": "NAM", "position": 0, "color": "blue"},
                 {"label": "Nu", "value": "NU", "position": 1, "color": "red"}]},
    {"name": "cccd", "label": "CCCD", "type": "TEXT", "icon": "IconIdBadge2"},
    {"name": "patientSource", "label": "Nguon", "type": "SELECT", "icon": "IconRoute",
     "options": [{"label": "Marketing", "value": "MARKETING", "position": 0, "color": "blue"},
                 {"label": "Benh vien", "value": "BENH_VIEN", "position": 1, "color": "green"},
                 {"label": "Bac si hop tac", "value": "BAC_SI_HOP_TAC", "position": 2, "color": "turquoise"},
                 {"label": "Khac", "value": "KHAC", "position": 3, "color": "sky"}]},
    {"name": "referralPartner", "label": "Doi tac", "type": "TEXT", "icon": "IconUsersGroup"},
    {"name": "diagnosis", "label": "Chan doan", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "contactPerson", "label": "Nguoi lien he", "type": "TEXT", "icon": "IconUser"},
    {"name": "contactPhone", "label": "SDT lien he", "type": "TEXT", "icon": "IconPhone"},
    {"name": "spouseName", "label": "Ten vo/chong", "type": "TEXT", "icon": "IconHeart"},
    {"name": "spousePid", "label": "PID vo/chong", "type": "TEXT", "icon": "IconId"},
    {"name": "spousePhone", "label": "SDT vo/chong", "type": "TEXT", "icon": "IconPhone"},
    {"name": "medication", "label": "Thuoc dang dung", "type": "TEXT", "icon": "IconPill"},
    {"name": "currentCycle", "label": "Chu ky hien tai", "type": "TEXT", "icon": "IconRepeat"},
    {"name": "iuiDate", "label": "Ngay bom IUI", "type": "DATE_TIME", "icon": "IconCalendar"},
    {"name": "embryoTransferDate", "label": "Ngay chuyen phoi", "type": "DATE_TIME", "icon": "IconCalendar"},
    {"name": "betaResult", "label": "Ket qua Beta", "type": "TEXT", "icon": "IconHeartbeat"},
    {"name": "cancelReason", "label": "Ly do huy chu ky", "type": "TEXT", "icon": "IconAlertTriangle"},
    {"name": "clinicRoom", "label": "Phong kham", "type": "TEXT", "icon": "IconBuilding"},
    {"name": "doctorName", "label": "BS phu trach", "type": "TEXT", "icon": "IconStethoscope"},
]

TASK_FIELDS = [
    {"name": "appointmentType", "label": "Loai lich hen", "type": "SELECT", "icon": "IconCalendarEvent",
     "options": [{"label": "Tai kham", "value": "TAI_KHAM", "position": 0, "color": "blue"},
                 {"label": "IUI", "value": "IUI", "position": 1, "color": "green"},
                 {"label": "Lay trung", "value": "LAY_TRUNG", "position": 2, "color": "orange"},
                 {"label": "Chuyen phoi", "value": "CHUYEN_PHOI", "position": 3, "color": "purple"},
                 {"label": "Phau thuat", "value": "PHAU_THUAT", "position": 4, "color": "red"},
                 {"label": "PRP", "value": "PRP", "position": 5, "color": "turquoise"},
                 {"label": "Sinh nhat", "value": "SINH_NHAT", "position": 6, "color": "yellow"}]},
    {"name": "appointmentTime", "label": "Gio hen", "type": "TEXT", "icon": "IconClock"},
    {"name": "arrivalTime", "label": "Gio co mat", "type": "TEXT", "icon": "IconClockHour3"},
    {"name": "reminderDate", "label": "Ngay nhac lich", "type": "DATE_TIME", "icon": "IconBell"},
    {"name": "examCode", "label": "Ma kham", "type": "TEXT", "icon": "IconBarcode"},
    {"name": "doctorAdvice", "label": "Loi dan BS", "type": "TEXT", "icon": "IconMessageDots"},
    {"name": "clinicRoom", "label": "Phong kham", "type": "TEXT", "icon": "IconBuilding"},
    {"name": "careType", "label": "Loai cham soc", "type": "SELECT", "icon": "IconHeartHandshake",
     "options": [{"label": "Noi tru", "value": "NOI_TRU", "position": 0, "color": "blue"},
                 {"label": "CBNM", "value": "CBNM", "position": 1, "color": "green"},
                 {"label": "Thu thuat", "value": "THU_THUAT", "position": 2, "color": "orange"},
                 {"label": "Tai kham", "value": "TAI_KHAM", "position": 3, "color": "purple"},
                 {"label": "Beta-thai", "value": "BETA_THAI", "position": 4, "color": "red"},
                 {"label": "Thai ky", "value": "THAI_KY", "position": 5, "color": "turquoise"}]},
    {"name": "callStatus", "label": "Trang thai goi", "type": "SELECT", "icon": "IconPhoneCall",
     "options": [{"label": "Chua goi", "value": "CHUA_GOI", "position": 0, "color": "sky"},
                 {"label": "Da goi", "value": "DA_GOI", "position": 1, "color": "green"},
                 {"label": "Can goi lai", "value": "CAN_GOI_LAI", "position": 2, "color": "orange"},
                 {"label": "Khong lien lac duoc", "value": "KHONG_LIEN_LAC", "position": 3, "color": "red"}]},
    {"name": "callNote", "label": "Ghi chu cuoc goi", "type": "TEXT", "icon": "IconNote"},
    {"name": "medication", "label": "Thuoc", "type": "TEXT", "icon": "IconPill"},
    {"name": "doctorName", "label": "BS phu trach", "type": "TEXT", "icon": "IconStethoscope"},
    {"name": "approvalStatus", "label": "Trang thai duyet", "type": "SELECT", "icon": "IconCheck",
     "options": [{"label": "Chua duyet", "value": "CHUA_DUYET", "position": 0, "color": "sky"},
                 {"label": "Da duyet", "value": "DA_DUYET", "position": 1, "color": "green"},
                 {"label": "Tu choi", "value": "TU_CHOI", "position": 2, "color": "red"}]},
]

# View definitions: (name, icon, type, filter_value, columns[(fieldName, size)])
CS_VIEWS = [
    ("CS noi tru", "IconBuildingHospital", "TABLE", "NOI_TRU",
     [("title", 220), ("taskTargets", 180), ("callStatus", 130), ("dueAt", 120), ("callNote", 200), ("medication", 150)]),
    ("CS CBNM", "IconStethoscope", "TABLE", "CBNM",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("medication", 150), ("callStatus", 130), ("callNote", 200)]),
    ("CS thu thuat", "IconNeedle", "TABLE", "THU_THUAT",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS tai kham", "IconCalendar", "TABLE", "TAI_KHAM",
     [("title", 220), ("taskTargets", 180), ("doctorName", 120), ("medication", 150), ("callStatus", 130), ("callNote", 200), ("dueAt", 120)]),
    ("CS beta-thai", "IconHeartbeat", "TABLE", "BETA_THAI",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("approvalStatus", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS thai ky", "IconMoodKid", "TABLE", "THAI_KY",
     [("title", 220), ("taskTargets", 180), ("dueAt", 120), ("callStatus", 130), ("callNote", 200)]),
    ("CS theo trang thai", "IconLayoutKanban", "KANBAN", None, []),
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
        """Returns {objectMetadataId: nameSingular}"""
        r = self._gql('query { objects { edges { node { id nameSingular } } } }')
        return {e["node"]["id"]: e["node"]["nameSingular"] for e in r["data"]["objects"]["edges"]}

    def delete_nav_item(self, item_id: str):
        self._gql(f'mutation {{ deleteNavigationMenuItem(id: "{item_id}") {{ id }} }}')


# =============================================================================
# SETUP FUNCTIONS
# =============================================================================

def cleanup_defaults(api: TwentyAPI):
    """Delete ALL existing companies, people, opportunities, tasks, notes."""
    print("\n2. Cleaning up all existing data...")

    for obj_name in ("taskTargets", "noteTargets", "tasks", "notes", "opportunities", "people", "companies"):
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

    # 2-8. Base setup (always runs)
    cleanup_defaults(api)
    deactivate_opportunity(api)
    cleanup_navigation(api)
    create_custom_fields(api)
    create_views(api)
    seed_companies(api)

    # 9-13. Demo data (only with --level demo)
    if args.level == "demo":
        seed_demo_data(api)

    print("\n" + "=" * 50)
    print(f"Setup complete! Level: {args.level}")
    print(f"Open: {args.url}")
    print("=" * 50)


if __name__ == "__main__":
    main()
