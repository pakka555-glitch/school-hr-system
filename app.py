# app.py
# -*- coding: utf-8 -*-

import os
import json
import base64
import streamlit as st
import pandas as pd

# ====== (ออปชัน) Google Sheets backend ======
# ตั้งค่า ENV ดังนี้ หากต้องการดึงผู้ใช้จากชีต
# GOOGLE_SHEETS_ID=<Spreadsheet ID>
# GOOGLE_SERVICE_ACCOUNT_JSON=<service-account-json ทั้งก้อน>
USE_SHEETS = bool(os.getenv("GOOGLE_SHEETS_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
SHEET_ID    = os.getenv("GOOGLE_SHEETS_ID", "")
SHEET_TAB   = os.getenv("GOOGLE_SHEETS_TAB", "users")  # แท็บชื่อ users
CSV_FALLBACK_PATH = "teachers.csv"                      # สำรองกรณีไม่มีชีต

# ====== Branding ======
APP_TITLE     = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL = "pakka555@gmail.com"
BRAND_PRIMARY = "#0a2342"
BRAND_MUTED   = "#445b66"

ASSETS_DIR   = "assets"
BANNER_PATH  = os.path.join(ASSETS_DIR, "banner.jpg")

# ====== Session Defaults ======
if "menu" not in st.session_state:
    st.session_state["menu"] = "หน้าแรก"

# route ใช้สำหรับหน้าเฉพาะ เช่น ฝ่ายบริหาร
if "route" not in st.session_state:
    st.session_state["route"] = "home"   # home | executive

# ====== Utilities: load users from Google Sheets or CSV ======
def load_users_df() -> pd.DataFrame:
    required_cols = [
        "teacher_id", "name", "email", "department", "pin", "role", "admin_modules"
    ]
    if USE_SHEETS:
        try:
            import gspread
            from google.oauth2.service_account import Credentials

            creds_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
            scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
            credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
            client = gspread.authorize(credentials)
            sh = client.open_by_key(SHEET_ID)
            ws = sh.worksheet(SHEET_TAB)
            rows = ws.get_all_records()  # list[dict]

            df = pd.DataFrame(rows)
            for c in required_cols:
                if c not in df.columns:
                    df[c] = ""
            return df.fillna("")
        except Exception as e:
            st.error(f"อ่านข้อมูลจาก Google Sheets ไม่สำเร็จ: {e}")
            # ตกลงไปใช้ CSV แทน
    # fallback -> CSV
    try:
        df = pd.read_csv(CSV_FALLBACK_PATH, dtype=str).fillna("")
        for c in required_cols:
            if c not in df.columns:
                df[c] = ""
        return df
    except Exception as e:
        st.error(f"อ่าน {CSV_FALLBACK_PATH} ไม่สำเร็จ: {e}")
        return pd.DataFrame(columns=required_cols)

def get_user_by_id(tid: str):
    df = load_users_df()
    m = df[df["teacher_id"].astype(str).str.strip() == str(tid).strip()]
    return m.iloc[0].to_dict() if not m.empty else None

def check_login(tid: str, pin: str):
    if not tid or not pin:
        return False, None, "กรุณากรอกให้ครบ"
    u = get_user_by_id(tid)
    if not u:
        return False, None, "ไม่พบรหัสผู้ใช้"
    if str(u.get("pin","")).strip() != str(pin).strip():
        return False, None, "PIN ไม่ถูกต้อง"
    return True, u, None

# ====== UI: Global CSS / Fonts ======
def inject_fonts_and_css():
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;500;700&display=swap" rel="stylesheet">

        <style>
          :root {{
            --brand: {BRAND_PRIMARY};
            --muted: {BRAND_MUTED};
            --bg-card: #ffffff;
            --bg-soft: #f5f8fb;
            --shadow: 0 10px 30px rgba(10,35,66,0.08);
            --radius: 14px;
          }}
          html, body, [class*="css"] {{
            font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif;
          }}
          .block-container {{ max-width: 1240px !important; }}

          .kys-banner {{
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            margin: 6px 0 18px 0;
          }}

          .kys-title h1 {{
            margin:0; font-size: clamp(28px, 2.6vw, 38px); color: var(--brand); font-weight:800; text-align:center;
          }}
          .kys-title p {{
            margin:6px 0 0 0; color: var(--muted); text-align:center; font-size:18px;
          }}

          .kys-grid {{
            display:grid; grid-template-columns: repeat(3, 1fr);
            gap: 26px; margin-top:14px;
          }}
          @media (max-width: 1100px) {{ .kys-grid{{ grid-template-columns: repeat(2, 1fr); }} }}
          @media (max-width: 760px)  {{ .kys-grid{{ grid-template-columns: 1fr; }} }}

          .kys-card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px 22px;
            display:flex; flex-direction: column; min-height: 320px;
          }}
          .kys-card h3 {{ margin:0 0 6px 0; font-weight:800; color: var(--brand); }}
          .kys-card h4 {{ margin:0 0 10px 0; font-weight:600; color: var(--muted); }}
          .kys-card ul {{ margin: 8px 0 0 18px; color:#314657; line-height:1.6; }}

          .kys-btn {{
            display:inline-flex; align-items:center; justify-content:center; gap:8px;
            padding: 12px 16px; border-radius: 12px;
            background: var(--brand); color:#fff !important; text-decoration:none !important;
            box-shadow: var(--shadow); margin-top: 14px; min-height: 48px;
          }}
          .kys-btn:hover {{ filter:brightness(1.06); }}

          .kys-contact {{ width:100%; display:flex; justify-content:flex-end; margin-top:18px; }}
          .kys-contact a {{
            display:inline-flex; align-items:center; gap:8px; padding: 10px 14px;
            border-radius: 999px; background: #0f2748; color: #fff !important; text-decoration:none; box-shadow: var(--shadow);
          }}

          .muted {{ color: var(--muted); }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ====== Pages ======
def show_home():
    inject_fonts_and_css()

    # banner (ถ้ามี)
    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # title
    st.markdown(
        f"""
        <div class="kys-title">
          <h1>{APP_TITLE}</h1>
          <p>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # การ์ด 3 ใบเดิม + ปุ่มไป “ฝ่ายบริหาร” (การ์ดสั้นๆ)
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown(
            """
            <div class="kys-card">
              <div>
                <h3>👩‍🏫 สำหรับครูผู้สอน</h3>
                <h4>Teacher</h4>
                <ul>
                  <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
                  <li>ส่งคำขอ (ลา/ไปราชการ/อบรม ฯลฯ) และตรวจสอบสถานะ</li>
                  <li>อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)</li>
                </ul>
              </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_teacher"):
            tid = st.text_input("Teacher ID", key="t_tid")
            pin = st.text_input("PIN", type="password", key="t_pin")
            submit_t = st.form_submit_button("🔐 เข้าสู่ระบบครู")
            if submit_t:
                ok, u, err = check_login(tid, pin)
                if not ok: st.error(err)
                else:
                    if u.get("role","").strip().lower() in ["teacher","module_admin","superadmin","executive"]:
                        st.success(f"ยินดีต้อนรับคุณ {u.get('name','')}")
                        st.session_state["user"] = u
                    else:
                        st.error("สิทธิ์ไม่พอสำหรับเมนูนี้")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(
            """
            <div class="kys-card">
              <div>
                <h3>⚙️ ผู้ดูแลโมดูล</h3>
                <h4>Module Admin</h4>
                <ul>
                  <li>ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ</li>
                  <li>ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น</li>
                  <li>ดูสรุปสถิติและรายงานในโมดูล</li>
                </ul>
              </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_module_admin"):
            tid2 = st.text_input("User ID", key="m_tid")
            pin2 = st.text_input("PIN", type="password", key="m_pin")
            submit_m = st.form_submit_button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล")
            if submit_m:
                ok, u, err = check_login(tid2, pin2)
                if not ok: st.error(err)
                else:
                    if u.get("role","").strip().lower() in ["module_admin","superadmin"]:
                        st.success(f"ยินดีต้อนรับคุณ {u.get('name','')} (ผู้ดูแลโมดูล)")
                        st.session_state["user"] = u
                    else:
                        st.error("เมนูนี้สำหรับผู้ดูแลโมดูลเท่านั้น")
        st.markdown("</div>", unsafe_allow_html=True)

    with col3:
        st.markdown(
            """
            <div class="kys-card">
              <div>
                <h3>🛡️ แอดมินใหญ่</h3>
                <h4>Superadmin</h4>
                <ul>
                  <li>กำกับดูแลภาพรวมของระบบทั้งหมด</li>
                  <li>จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้</li>
                  <li>ออกรายงานภาพรวมเพื่อการบริหาร</li>
                </ul>
              </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("login_superadmin"):
            tid3 = st.text_input("User ID", key="s_tid")
            pin3 = st.text_input("PIN", type="password", key="s_pin")
            submit_s = st.form_submit_button("🔐 เข้าสู่ระบบแอดมินใหญ่")
            if submit_s:
                ok, u, err = check_login(tid3, pin3)
                if not ok: st.error(err)
                else:
                    if u.get("role","").strip().lower() == "superadmin":
                        st.success(f"ยินดีต้อนรับคุณ {u.get('name','')} (แอดมินใหญ่)")
                        st.session_state["user"] = u
                    else:
                        st.error("เมนูนี้สำหรับแอดมินใหญ่เท่านั้น")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # แถวล่าง: การ์ดปุ่มไป 'ฝ่ายบริหาร'
    ex1, ex2, ex3 = st.columns([1,2,1])
    with ex2:
        st.markdown(
            """
            <div class="kys-card">
              <h3>🏫 ฝ่ายบริหาร (Executive)</h3>
              <p class="muted">สำหรับผู้อำนวยการ / รองผู้อำนวยการ</p>
            """,
            unsafe_allow_html=True,
        )
        if st.button("➡️ ไปยังหน้าฝ่ายบริหาร", use_container_width=True):
            st.session_state["route"] = "executive"
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # footer
    st.markdown(
        f"""
        <div class="kys-contact">
          <a href="mailto:{CONTACT_EMAIL}">📧 ติดต่อผู้ดูแลระบบ</a>
        </div>
        <hr style="margin-top:32px;margin-bottom:12px;border:1px solid #e0e6ec;">
        <div style='text-align:center; color:#445b66; font-size:15px;'>
            พัฒนาโดย <b>กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</b><br>
            เพื่อยกระดับการบริหารจัดการงานบุคคลให้ทันสมัย โปร่งใส และตรวจสอบได้
        </div>
        """,
        unsafe_allow_html=True,
    )

def show_executive_portal():
    """หน้าเฉพาะฝ่ายบริหาร (แยกจากหน้าแรก)"""
    inject_fonts_and_css()

    st.markdown("<h2>🏫 ฝ่ายบริหาร (Executive)</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='muted'>สำหรับผู้อำนวยการ / รองผู้อำนวยการ</p>",
        unsafe_allow_html=True,
    )

    with st.form("login_executive"):
        tid = st.text_input("Executive ID")
        pin = st.text_input("PIN", type="password")
        submit = st.form_submit_button("🔐 เข้าสู่ระบบฝ่ายบริหาร")
        if submit:
            ok, u, err = check_login(tid, pin)
            if not ok:
                st.error(err)
            else:
                role = u.get("role","").strip().lower()
                if role in ["executive", "superadmin"]:
                    st.success(f"สวัสดีคุณ {u.get('name','')} — เข้าสู่พื้นที่ฝ่ายบริหารสำเร็จ")
                    st.session_state["user"] = u
                    # TODO: ต่อยอดเมนู / รายงานของฝ่ายบริหารที่นี่
                else:
                    st.error("เมนูนี้สำหรับฝ่ายบริหารเท่านั้น")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ กลับหน้าแรก"):
        st.session_state["route"] = "home"
        st.experimental_rerun()

def show_teacher_portal():
    inject_fonts_and_css()
    st.title("พื้นที่สำหรับผู้ใช้ (ครู)")
    st.info("หน้านี้ไว้ต่อยอดฟอร์ม/เมนูย่อยสำหรับครูในอนาคตครับ")

def show_admin_portal():
    inject_fonts_and_css()
    st.title("พื้นที่สำหรับผู้ดูแล")
    st.info("หน้านี้ไว้ต่อยอดเมนูย่อยสำหรับผู้ดูแล/แอดมินในอนาคตครับ")

# ====== App Entrypoint ======
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏫", layout="wide")

    # Sidebar menu (ยังคงไว้เหมือนเดิม)
    with st.sidebar:
        st.markdown("### เมนู")
        st.session_state["menu"] = st.radio(
            "ไปหน้า:",
            ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"],
            index=["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"].index(st.session_state["menu"]),
            label_visibility="collapsed",
        )

    # Routing หลัก
    if st.session_state["route"] == "executive":
        show_executive_portal()
        return

    # หน้าในเมนูเดิม
    if st.session_state["menu"] == "หน้าแรก":
        show_home()
    elif st.session_state["menu"] == "สำหรับผู้ใช้":
        show_teacher_portal()
    else:
        show_admin_portal()

if __name__ == "__main__":
    main()
