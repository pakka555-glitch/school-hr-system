import os
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==========================
# 🔧 ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

ASSETS_DIR = "assets"
BANNER_PATH = os.path.join(ASSETS_DIR, "banner.jpg")

# ==========================
# 🎨 CSS และฟอนต์
# ==========================
def inject_fonts_and_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }

    /* โครงการ์ด */
    [data-testid="stContainer"] {
        border-radius: 14px !important;
        padding: 18px 20px !important;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        background: #fff;
        position: relative;
    }

    /* ให้ทุกปุ่มมีสีเข้มชัดแน่นอน */
    .stButton > button {
        width: 100% !important;
        background: #0D47A1 !important;     /* 🔵 น้ำเงินกรมเข้ม */
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 0 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.12) !important;
        transition: all .2s ease !important;
    }
    .stButton > button:hover {
        background: #002171 !important;     /* เข้มขึ้นตอน hover */
        box-shadow: 0 6px 16px rgba(0,0,0,0.22) !important;
        transform: translateY(-1px);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ==========================
# 🔗 เชื่อม Google Sheets
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
    try:
        client = get_gs_client()
        sheet_id = st.secrets["gsheets"]["users_sheet_id"]
        ws_name = st.secrets["gsheets"]["users_worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")
        for col in ["teacher_id", "pin", "role", "name"]:
            if col not in df.columns: df[col] = ""
        df["teacher_id"] = df["teacher_id"].astype(str).str.strip()
        df["pin"] = df["pin"].astype(str).str.strip()
        df["role"] = df["role"].astype(str).str.lower().str.strip()
        return df
    except Exception as e:
        st.error(f"โหลดข้อมูลผู้ใช้ไม่สำเร็จ: {e}")
        return pd.DataFrame(columns=["teacher_id","pin","role","name"])

def check_login(user_id, pin, allowed_roles):
    df = load_users_df()
    user = df[df["teacher_id"] == str(user_id).strip()]
    if user.empty: return False, None, "❌ ไม่พบผู้ใช้"
    u = user.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"
    if allowed_roles and u["role"] not in allowed_roles:
        return False, None, "🚫 ไม่มีสิทธิ์เข้าหน้านี้"
    return True, u, None

# ==========================
# 🏠 หน้าแรก
# ==========================
def page_home():
    if os.path.exists(BANNER_PATH):
        st.image(BANNER_PATH, use_container_width=True)

    st.markdown(
        "<h2 style='text-align:center;color:#0a3a75;'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>"
        "<p style='text-align:center;color:#48617a'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลอย่างโปร่งใสและตรวจสอบได้</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        with st.container(border=True):
            st.subheader("👩‍🏫 สำหรับครูผู้สอน")
            st.markdown(
                """
                <div class="role-body">
                <ul>
                <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
                <li>ส่งคำขอลา/อบรม</li>
                <li>อัปโหลดเอกสาร</li>
                </ul></div>
                """, unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบครูผู้สอน", use_container_width=True):
                st.session_state["route"] = "login_teacher"
                st.rerun()

    with col2:
        with st.container(border=True):
            st.subheader("⚙️ ผู้ดูแลโมดูล")
            st.markdown(
                """
                <div class="role-body">
                <ul>
                <li>ตรวจสอบ/อนุมัติคำขอในโมดูล</li>
                <li>ดูสถิติและรายงานในโมดูล</li>
                </ul></div>
                """, unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล", use_container_width=True):
                st.session_state["route"] = "login_module_admin"
                st.rerun()

    with col3:
        with st.container(border=True):
            st.subheader("🛡️ แอดมินใหญ่")
            st.markdown(
                """
                <div class="role-body">
                <ul>
                <li>จัดการสิทธิ์เข้าระบบ</li>
                <li>ออกรายงานรวมเพื่อบริหาร</li>
                </ul></div>
                """, unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบแอดมินใหญ่", use_container_width=True):
                st.session_state["route"] = "login_superadmin"
                st.rerun()

    with col4:
        with st.container(border=True):
            st.subheader("🏫 ฝ่ายบริหาร (Executive)")
            st.markdown(
                """
                <div class="role-body">
                <ul>
                <li>สำหรับผู้บริหารโรงเรียน</li>
                <li>ดูรายงานภาพรวมทั้งหมด</li>
                </ul></div>
                """, unsafe_allow_html=True)
            if st.button("🔐 เข้าสู่ระบบฝ่ายบริหาร", use_container_width=True):
                st.session_state["route"] = "login_executive"
                st.rerun()

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
        """, unsafe_allow_html=True
    )

# ==========================
# 🔑 Login + Portals
# ==========================
def login_page(title, roles, next_route):
    st.markdown(f"### {title}")
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        if st.form_submit_button("เข้าสู่ระบบ"):
            ok, user, err = check_login(uid, pin, roles)
            if not ok: st.error(err)
            else:
                st.session_state["user"] = dict(user)
                st.session_state["route"] = next_route
                st.rerun()
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state["route"] = "home"
        st.rerun()

def _logout_btn(): st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route":"home","user":None}))

def teacher_portal():
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน"); _logout_btn()
def module_portal():
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล"); _logout_btn()
def superadmin_portal():
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่"); _logout_btn()
def executive_portal():
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)"); _logout_btn()

# ==========================
# 🚦 Route Controller
# ==========================
def main():
    route = st.session_state.get("route", "home")
    if route == "home": page_home()
    elif route == "login_teacher": login_page("👩‍🏫 เข้าสู่ระบบครูผู้สอน", ["teacher","module_admin","superadmin"], "teacher_portal")
    elif route == "login_module_admin": login_page("⚙️ เข้าสู่ระบบผู้ดูแลโมดูล", ["module_admin","superadmin"], "module_portal")
    elif route == "login_superadmin": login_page("🛡️ เข้าสู่ระบบแอดมินใหญ่", ["superadmin"], "superadmin_portal")
    elif route == "login_executive": login_page("🏫 เข้าสู่ระบบฝ่ายบริหาร (Executive)", ["executive","superadmin"], "executive_portal")
    elif route == "teacher_portal": teacher_portal()
    elif route == "module_portal": module_portal()
    elif route == "superadmin_portal": superadmin_portal()
    elif route == "executive_portal": executive_portal()

if __name__ == "__main__":
    main()
