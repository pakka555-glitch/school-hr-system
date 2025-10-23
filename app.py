import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==========================
# 🔧 ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

# ==========================
# 📁 พาธรูปในโปรเจกต์ (แบนเนอร์)
# ==========================
ASSETS_DIR = "assets"
BANNER_PATH = os.path.join(ASSETS_DIR, "banner.jpg")  # วางรูปชื่อ banner.jpg ในโฟลเดอร์ assets/

# ==========================
# 🎨 CSS และฟอนต์ (ปุ่มสีประจำบทบาท + accent bar + footer)
# ==========================
def inject_fonts_and_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }

    /* ===== การ์ดหลัก ===== */
    [data-testid="stContainer"] {
        border-radius: 14px !important;
        padding: 18px 20px !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        position: relative;
        background: #fff;
    }

    /* ===== แถบสีบทบาท (Accent bar) — อ้างตามลำดับในหน้า ===== */
    [data-testid="stContainer"]:nth-of-type(1)::before,
    [data-testid="stContainer"]:nth-of-type(2)::before,
    [data-testid="stContainer"]:nth-of-type(3)::before,
    [data-testid="stContainer"]:nth-of-type(4)::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 6px;
        border-top-left-radius: 14px; border-top-right-radius: 14px;
    }
    /* ครูผู้สอน */
    [data-testid="stContainer"]:nth-of-type(1)::before { background-color: #1E88E5; }
    /* ผู้ดูแลโมดูล */
    [data-testid="stContainer"]:nth-of-type(2)::before { background-color: #8E24AA; }
    /* แอดมินใหญ่ */
    [data-testid="stContainer"]:nth-of-type(3)::before { background-color: #0277BD; }
    /* ฝ่ายบริหาร */
    [data-testid="stContainer"]:nth-of-type(4)::before { background-color: #43A047; }

    /* ===== ปุ่มเข้าสู่ระบบ (สีตามบทบาท) ===== */
    .stButton>button {
        color: white !important; font-weight: 600; border: none;
        border-radius: 10px; padding: 10px 0px; width: 100% !important;
        transition: all 0.25s ease-in-out;
    }
    /* ไล่ตามลำดับปุ่มในคอลัมน์ 1..4 */
    div.stButton:nth-of-type(1) > button { background-color: #1E88E5; } /* ครู */
    div.stButton:nth-of-type(1) > button:hover { background-color: #1565C0; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

    div.stButton:nth-of-type(2) > button { background-color: #8E24AA; } /* ผู้ดูแลโมดูล */
    div.stButton:nth-of-type(2) > button:hover { background-color: #6A1B9A; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

    div.stButton:nth-of-type(3) > button { background-color: #0277BD; } /* แอดมินใหญ่ */
    div.stButton:nth-of-type(3) > button:hover { background-color: #01579B; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

    div.stButton:nth-of-type(4) > button { background-color: #43A047; } /* ฝ่ายบริหาร */
    div.stButton:nth-of-type(4) > button:hover { background-color: #2E7D32; transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }

    /* ===== แบนเนอร์ ===== */
    .kys-banner { border-radius: 14px; overflow: hidden; box-shadow: 0 8px 22px rgba(0,0,0,0.10); margin-bottom: 18px; }

    /* ===== Footer ===== */
    .footer { text-align:center; color:gray; font-size:14px; margin-top:40px; }
    .footer img { width: 22px; vertical-align: middle; margin-right: 5px; opacity: 0.7; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_fonts_and_css()

# ==========================
# 🔗 ฟังก์ชันเชื่อม Google Sheets (Users)
# ==========================
@st.cache_resource(show_spinner=False)
def get_gs_client():
    info = dict(st.secrets["gcp_service_account"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=60)
def load_users_df():
    """โหลดข้อมูลผู้ใช้จาก Google Sheets"""
    try:
        client = get_gs_client()
        sheet_id = st.secrets["gsheets"]["users_sheet_id"]
        ws_name  = st.secrets["gsheets"]["users_worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")
        # บังคับให้มีคอลัมน์จำเป็น
        for col in ["teacher_id", "pin", "role", "name", "email", "department"]:
            if col not in df.columns:
                df[col] = ""
        df["teacher_id"] = df["teacher_id"].astype(str).str.strip()
        df["pin"]        = df["pin"].astype(str).str.strip()
        df["role"]       = df["role"].astype(str).str.lower().str.strip()
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลผู้ใช้ได้: {e}")
        return pd.DataFrame(columns=["teacher_id", "name", "email", "department", "role", "pin"])

def check_login(user_id, pin, allowed_roles):
    df = load_users_df()
    user = df[df["teacher_id"] == str(user_id).strip()]
    if user.empty:
        return False, None, "❌ ไม่พบผู้ใช้"
    u = user.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"
    if allowed_roles and u["role"] not in allowed_roles:
        return False, None, "🚫 ไม่มีสิทธิ์เข้าหน้านี้"
    return True, u, None

# ==========================
# 🧭 Routing หลัก
# ==========================
if "route" not in st.session_state:
    st.session_state["route"] = "home"

# ==========================
# 🏠 หน้าแรก (Home)
# ==========================
def page_home():
    # ✅ แบนเนอร์ (ถ้ามีไฟล์)
    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ✅ หัวเรื่อง
    st.markdown(
        "<h2 style='text-align:center;color:#0a3a75;'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;color:#48617a'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลอย่างโปร่งใสและตรวจสอบได้</p>",
        unsafe_allow_html=True
    )

    # ✅ การ์ด 4 คอลัมน์
    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        with st.container(border=True):
            st.subheader("👩‍🏫 สำหรับครูผู้สอน")
            st.write("- จัดการ/ปรับปรุงข้อมูลส่วนบุคคล\n- ส่งคำขอลา/อบรม\n- อัปโหลดเอกสาร")
            st.write("")  # เติมช่องว่างให้ปุ่มอยู่ระดับเดียวกัน
            if st.button("🔐 เข้าสู่ระบบครูผู้สอน", use_container_width=True):
                st.session_state["route"] = "login_teacher"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("⚙️ ผู้ดูแลโมดูล")
            st.write("- ตรวจสอบ/อนุมัติคำขอในโมดูล\n- ดูสถิติและรายงานในโมดูล")
            st.write("")
            if st.button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล", use_container_width=True):
                st.session_state["route"] = "login_module_admin"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader("🛡️ แอดมินใหญ่")
            st.write("- จัดการสิทธิ์เข้าระบบ\n- ออกรายงานรวมเพื่อบริหาร")
            st.write("")
            if st.button("🔐 เข้าสู่ระบบแอดมินใหญ่", use_container_width=True):
                st.session_state["route"] = "login_superadmin"
                st.rerun()

    with col4:
        with st.container(border=True):
            st.subheader("🏫 ฝ่ายบริหาร (Executive)")
            st.write("- สำหรับผู้บริหารโรงเรียน\n- ดูรายงานภาพรวมทั้งหมด")
            st.write("")
            if st.button("🔐 เข้าสู่ระบบฝ่ายบริหาร", use_container_width=True):
                st.session_state["route"] = "login_executive"
                st.rerun()

    # ✅ Footer (เครดิตพัฒนา)
    st.markdown("---")
    st.markdown(
        """
        <div class="footer">
            <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png">
            พัฒนาโดย <b>ครูสุพจน์ นามโคตร</b> โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br>
            School HR System v2 | Powered by 
            <img src="https://streamlit.io/images/brand/streamlit-mark-color.png"> Streamlit + 
            <img src="https://www.svgrepo.com/show/373589/google-sheets.svg"> Google Sheets
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================
# 🔑 หน้าล็อกอิน (ฟังก์ชันรวมใช้ได้ทุกบทบาท)
# ==========================
def login_page(title, roles, next_route):
    st.markdown(f"### {title}")
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        submit = st.form_submit_button("เข้าสู่ระบบ")
        if submit:
            ok, user, err = check_login(uid, pin, roles)
            if not ok:
                st.error(err)
            else:
                st.success(f"ยินดีต้อนรับคุณ {user['name']}")
                st.session_state["user"] = dict(user)
                st.session_state["route"] = next_route
                st.rerun()
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state["route"] = "home"
        st.rerun()

# ==========================
# 🧩 Portal ตัวอย่างแต่ละบทบาท
# ==========================
def _logout_btn():
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))

def _require_role(roles):
    u = st.session_state.get("user")
    if not u or u.get("role") not in roles:
        st.warning("โปรดเข้าสู่ระบบด้วยสิทธิ์ที่ถูกต้อง")
        if st.button("กลับหน้าหลัก"):
            st.session_state["route"] = "home"
            st.rerun()
        st.stop()

def teacher_portal():
    _require_role(["teacher", "module_admin", "superadmin"])
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับครู")
    _logout_btn()

def module_portal():
    _require_role(["module_admin", "superadmin"])
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับผู้ดูแลโมดูล")
    _logout_btn()

def superadmin_portal():
    _require_role(["superadmin"])
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับแอดมินใหญ่")
    _logout_btn()

def executive_portal():
    _require_role(["executive", "superadmin"])
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับฝ่ายบริหาร")
    _logout_btn()

# ==========================
# 🚦 Route Controller
# ==========================
def main():
    route = st.session_state.get("route", "home")

    if route == "home":
        page_home()
    elif route == "login_teacher":
        login_page("👩‍🏫 เข้าสู่ระบบครูผู้สอน", ["teacher", "module_admin", "superadmin"], "teacher_portal")
    elif route == "login_module_admin":
        login_page("⚙️ เข้าสู่ระบบผู้ดูแลโมดูล", ["module_admin", "superadmin"], "module_portal")
    elif route == "login_superadmin":
        login_page("🛡️ เข้าสู่ระบบแอดมินใหญ่", ["superadmin"], "superadmin_portal")
    elif route == "login_executive":
        login_page("🏫 เข้าสู่ระบบฝ่ายบริหาร (Executive)", ["executive", "superadmin"], "executive_portal")
    elif route == "teacher_portal":
        teacher_portal()
    elif route == "module_portal":
        module_portal()
    elif route == "superadmin_portal":
        superadmin_portal()
    elif route == "executive_portal":
        executive_portal()

# ==========================
# ▶️ จุดเริ่มต้นของโปรแกรม
# ==========================
if __name__ == "__main__":
    main()

