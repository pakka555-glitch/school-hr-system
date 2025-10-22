import os
import pandas as pd
import streamlit as st

# ====================================================
# Safe Config & Offline Mode Helpers
# ====================================================
import pandas as pd

def sheets_config_ready() -> tuple[bool, str]:
    """เช็คว่าตั้งค่า Google Sheets พร้อมหรือยัง"""
    try:
        if "SHEET_ID" not in st.secrets:
            return False, "ไม่มี SHEET_ID ใน secrets"
        if "gcp_service_account" not in st.secrets:
            return False, "ไม่มี gcp_service_account ใน secrets"
        from google.oauth2.service_account import Credentials
        return True, "ok"
    except Exception as e:
        return False, f"{e}"

def get_users_df_offline() -> pd.DataFrame:
    """อ่าน users จากไฟล์ csv ภายในโปรเจ็กต์ (fallback)"""
    try:
        return pd.read_csv("teachers.csv", dtype=str).fillna("")
    except Exception:
        return pd.DataFrame(columns=[
            "teacher_id","name","email","department","pin","role","admin_modules"
        ])

def get_users_df_online() -> pd.DataFrame:
    """อ่าน users จาก Google Sheets (ต้องตั้งค่าเสร็จก่อน)"""
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(st.secrets["SHEET_ID"])
    ws = sh.sheet1
    data = ws.get_all_records()
    return pd.DataFrame(data, dtype=str).fillna("")

def load_users_safe() -> pd.DataFrame:
    """พยายามอ่านจาก Sheets ถ้าตั้งค่าไม่พร้อมจะ fallback เป็น CSV"""
    ok, reason = sheets_config_ready()
    if ok:
        try:
            return get_users_df_online()
        except Exception as e:
            st.warning(f"อ่าน Google Sheets ไม่สำเร็จ → ใช้โหมดออฟไลน์แทน ({e})")
            return get_users_df_offline()
    else:
        st.info(f"ยังไม่ได้ตั้งค่า Google Sheets → ใช้โหมดออฟไลน์ ({reason})")
        return get_users_df_offline()


# ==============================
# Settings & Branding
# ==============================
APP_TITLE = "ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่"
CONTACT_EMAIL = "pakka555@gmail.com"  # ครูสุพจน์
BRAND_PRIMARY = "#0a2342"            # น้ำเงินกรมท่า
BRAND_MUTED = "#445b66"              # เทาอมฟ้า

ASSETS_DIR = "assets"
BANNER_PATH = os.path.join(ASSETS_DIR, "banner.jpg")
DATA_PATH = "teachers.csv"           # ไฟล์บัญชีผู้ใช้

# ==============================
# Utils: Query params (รองรับทั้ง API เก่า/ใหม่)
# ==============================
def get_qp():
    try:
        return dict(st.query_params)
    except Exception:
        return st.experimental_get_query_params()

def set_qp(**kwargs):
    try:
        st.query_params.clear()
        st.query_params.update(kwargs)
    except Exception:
        st.experimental_set_query_params(**kwargs)

# ==============================
# Auth helpers (load users, check pin)
# ==============================
def load_users():
    """อ่าน users จาก teachers.csv -> DataFrame"""
    try:
        df = pd.read_csv(DATA_PATH, dtype=str).fillna("")
        required = {"teacher_id","name","email","department","pin","role","admin_modules"}
        missing = required - set(df.columns)
        if missing:
            st.error(f"teachers.csv ไม่มีคอลัมน์: {', '.join(missing)}")
        return df
    except Exception as e:
        st.error(f"อ่านไฟล์ users ไม่ได้: {e}")
        return pd.DataFrame(columns=["teacher_id","name","email","department","pin","role","admin_modules"])

def get_user(tid: str):
    df = load_users_safe()
    m = df[df["teacher_id"].astype(str).str.strip() == str(tid).strip()]
    return m.iloc[0].to_dict() if not m.empty else None

def check_login(tid: str, pin: str):
    """คืน (bool,user_dict|None, error_text|None)"""
    if not tid or not pin:
        return False, None, "กรุณากรอกให้ครบ"

    u = get_user(tid)
    if not u:
        return False, None, "ไม่พบรหัสผู้ใช้"
    if str(u["pin"]).strip() != str(pin).strip():
        return False, None, "PIN ไม่ถูกต้อง"
    return True, u, None

# ==============================
# Load Google Font + Global CSS
# ==============================
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
            --shadow: 0 10px 30px rgba(10,35,66,0.08);
            --radius: 14px;
          }}

          html, body, [class*="css"] {{
            font-family: 'Noto Sans Thai', system-ui, -apple-system, Segoe UI, Roboto, 'Helvetica Neue', Arial, sans-serif;
          }}
          .block-container {{ max-width: 1240px !important; }}

          /* Banner */
          .kys-banner {{
            border-radius: var(--radius);
            overflow: hidden;
            box-shadow: var(--shadow);
            margin: 6px 0 18px 0;
          }}

          /* Title */
          .kys-title h1 {{
            margin: 0;
            font-size: clamp(28px, 2.6vw, 38px);
            color: var(--brand);
            font-weight: 800;
          }}
          .kys-title p {{
            margin: 6px 0 0 0;
            color: var(--muted);
          }}

          /* Grid การ์ด — 3 ใบเรียงแนวนอน */
          .kys-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(320px, 1fr));
            gap: 26px;
            margin-top: 14px;
          }}
          @media (max-width: 1200px) {{
            .kys-grid {{ grid-template-columns: repeat(2, minmax(320px, 1fr)); }}
          }}
          @media (max-width: 760px) {{
            .kys-grid {{ grid-template-columns: 1fr; }}
          }}

          .kys-card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 24px 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 360px;
          }}
          .kys-card h3 {{
            margin: 0 0 6px 0;
            font-weight: 800;
            color: var(--brand);
          }}
          .kys-card h4 {{
            margin: 0 0 10px 0;
            font-weight: 600;
            color: var(--muted);
          }}
          .kys-card ul {{
            margin: 8px 0 0 18px;
            color: #314657;
            line-height: 1.6;
          }}

          /* ปุ่มสวย */
          .kys-actions {{ margin-top: auto; display: flex; }}
          .kys-btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            min-height: 52px;
            padding: 12px 18px;
            border-radius: 12px;
            background: var(--brand);
            color: #fff !important;
            text-decoration: none !important;
            font-weight: 700;
            box-shadow: var(--shadow);
            transition: transform .05s ease, filter .15s ease;
          }}
          .kys-btn:hover {{
            filter: brightness(1.06);
            transform: translateY(-1px);
          }}

          /* ปุ่มติดต่อผู้ดูแล */
          .kys-contact {{
            width: 100%;
            display: flex;
            justify-content: flex-end;
            margin-top: 18px;
          }}
          .kys-contact a {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 14px;
            border-radius: 999px;
            background: #0f2748;
            color: #fff !important;
            text-decoration: none;
            box-shadow: var(--shadow);
          }}

          /* กล่องฟอร์ม */
          .kys-form {{
            background: #fff; border-radius: var(--radius); box-shadow: var(--shadow);
            padding: 22px; margin-top: 16px;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================
# Pages
# ==============================
def show_home():
    inject_fonts_and_css()

    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="kys-title" style="text-align:center; margin-top:10px;">
          <h1>{APP_TITLE}</h1>
          <p style="color:{BRAND_MUTED}; font-size:18px;">
            ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kys-grid">', unsafe_allow_html=True)

    st.markdown("""
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
        <div class="kys-actions">
          <a class="kys-btn" href="?page=login_teacher">🔐 เข้าสู่ระบบครู</a>
        </div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown("""
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
        <div class="kys-actions">
          <a class="kys-btn" href="?page=login_module">🔐 เข้าสู่ระบบผู้ดูแลโมดูล</a>
        </div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown("""
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
        <div class="kys-actions">
          <a class="kys-btn" href="?page=login_super">🔐 เข้าสู่ระบบแอดมินใหญ่</a>
        </div>
      </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
      <div class="kys-contact">
        <a href="mailto:{CONTACT_EMAIL}">📧 ติดต่อผู้ดูแลระบบ</a>
      </div>
      <hr style="margin-top:32px;margin-bottom:12px;border:1px solid #e0e6ec;">
      <div style='text-align:center; color:#445b66; font-size:15px;'>
          พัฒนาโดย <b>กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</b><br>
          เพื่อยกระดับการบริหารจัดการงานบุคคลให้ทันสมัย โปร่งใส และตรวจสอบได้
      </div>
    """, unsafe_allow_html=True)

# ---------- Login Pages ----------
def show_login(role_key: str, title: str, allow_roles: list, success_target: str):
    """หน้าล็อกอินร่วม: role_key -> teacher|module|super"""
    inject_fonts_and_css()

    st.markdown(f"<h2>🔐 เข้าสู่ระบบ: {title}</h2>", unsafe_allow_html=True)
    st.markdown('<div class="kys-form">', unsafe_allow_html=True)
    with st.form(f"form_login_{role_key}"):
        tid = st.text_input("User / Teacher ID")
        pin = st.text_input("PIN", type="password")
        okbtn = st.form_submit_button("เข้าสู่ระบบ")

        if okbtn:
            ok, u, err = check_login(tid, pin)
            if not ok:
                st.error(err)
            else:
                role = u.get("role","").strip().lower()
                if role in [r.lower() for r in allow_roles]:
                    st.success(f"ยินดีต้อนรับคุณ {u.get('name','')}")
                    st.session_state["user"] = u
                    set_qp(page=success_target)  # redirect
                    st.rerun()
                else:
                    st.error("สิทธิ์ไม่พอสำหรับเมนูนี้")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    st.link_button("← กลับหน้าแรก", "?page=home")

# ---------- Dashboards ----------
def show_dashboard(title: str, required_roles: list):
    inject_fonts_and_css()
    user = st.session_state.get("user")
    if not user:
        st.warning("กรุณาเข้าสู่ระบบก่อน")
        st.link_button("ไปยังหน้าแรก", "?page=home")
        return
    if user.get("role","").strip().lower() not in [r.lower() for r in required_roles]:
        st.error("สิทธิ์ไม่พอสำหรับหน้าแดชบอร์ดนี้")
        st.link_button("กลับหน้าแรก", "?page=home")
        return

    st.markdown(f"<h2>📊 {title}</h2>", unsafe_allow_html=True)
    st.info(
        f"สวัสดีคุณ **{user.get('name','')}**  "
        f"บทบาท: **{user.get('role','').title()}**  | แผนก: **{user.get('department','')}**"
    )
    st.success("พื้นที่นี้ไว้ต่อยอดเมนู/ฟอร์มการทำงานจริงในเฟสถัดไป")

    col1, col2 = st.columns(2)
    with col1:
        st.link_button("🏠 กลับหน้าแรก", "?page=home")
    with col2:
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            st.session_state.pop("user", None)
            set_qp(page="home")
            st.rerun()

# ==============================
# Router
# ==============================
def route():
    qp = get_qp()
    page = (qp.get("page") or qp.get("page", ["home"]))  # compatibility for old API list return
    if isinstance(page, list):
        page = page[0] if page else "home"
    page = page or "home"

    if page == "home":
        show_home()
    elif page == "login_teacher":
        show_login("teacher", "ครูผู้สอน", ["teacher","module_admin","superadmin"], "dashboard_teacher")
    elif page == "login_module":
        show_login("module", "ผู้ดูแลโมดูล", ["module_admin","superadmin"], "dashboard_module")
    elif page == "login_super":
        show_login("super", "แอดมินใหญ่", ["superadmin"], "dashboard_super")
    elif page == "dashboard_teacher":
        show_dashboard("แดชบอร์ดครูผู้สอน", ["teacher","module_admin","superadmin"])
    elif page == "dashboard_module":
        show_dashboard("แดชบอร์ดผู้ดูแลโมดูล", ["module_admin","superadmin"])
    elif page == "dashboard_super":
        show_dashboard("แดชบอร์ดแอดมินใหญ่", ["superadmin"])
    else:
        set_qp(page="home")
        show_home()

# ==============================
# Main
# ==============================
def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🏫", layout="wide")
    route()

if __name__ == "__main__":
    main()
