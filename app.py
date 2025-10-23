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
# 🎨 CSS และฟอนต์
# ==========================
def inject_fonts_and_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }

    /* === กรอบการ์ด === */
    .kys-card {
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        padding: 24px 22px;
        transition: 0.3s;
        border: 1px solid #e0e0e0;
        min-height: 280px;
    }
    .kys-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-3px);
    }

    /* === ปุ่ม === */
    .kys-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 10px 18px;
        border-radius: 10px;
        background: #0a3a75;
        color: #fff !important;
        font-weight: 600;
        text-decoration: none !important;
    }
    .kys-btn:hover { background: #052956; }

    /* === แบนเนอร์ === */
    .kys-banner {
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 8px 22px rgba(0,0,0,0.10);
        margin-bottom: 18px;
    }

    /* === เครดิต === */
    .footer {
        text-align:center;
        color:gray;
        font-size:14px;
        margin-top:40px;
    }
    .footer img {
        width: 22px;
        vertical-align: middle;
        margin-right: 5px;
        opacity: 0.7;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_fonts_and_css()

# ==========================
# 🔗 ฟังก์ชันเชื่อม Google Sheets
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
        ws_name = st.secrets["gsheets"]["users_worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")
        # ปรับชนิดข้อมูล
        for col in ["teacher_id", "pin", "role", "name", "email"]:
            if col not in df.columns:
                df[col] = ""
        df["teacher_id"] = df["teacher_id"].astype(str).str.strip()
        df["pin"] = df["pin"].astype(str).str.strip()
        df["role"] = df["role"].astype(str).str.lower().str.strip()
        return df
    except Exception as e:
        st.error(f"ไม่สามารถโหลดข้อมูลผู้ใช้ได้: {e}")
        return pd.DataFrame(columns=["teacher_id", "name", "email", "role", "pin"])

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
    # ✅ แบนเนอร์
    if os.path.exists(BANNER_PATH):
        st.markdown('<div class="kys-banner">', unsafe_allow_html=True)
        st.image(BANNER_PATH, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align:center;color:#0a3a75;'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center;color:#48617a'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลอย่างโปร่งใสและตรวจสอบได้</p>",
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4, gap="large")

    # ---- การ์ด: ครูผู้สอน ----
    with col1:
        with st.container(border=True):
            st.subheader("👩‍🏫 สำหรับครูผู้สอน")
            st.write("- จัดการ/ปรับปรุงข้อมูลส่วนบุคคล\n- ส่งคำขอลา/อบรม\n- อัปโหลดเอกสาร")
            if st.button("🔐 เข้าสู่ระบบครูผู้สอน", use_container_width=True):
                st.session_state["route"] = "login_teacher"
                st.rerun()

    # ---- การ์ด: ผู้ดูแลโมดูล ----
    with col2:
        with st.container(border=True):
            st.subheader("⚙️ ผู้ดูแลโมดูล")
            st.write("- ตรวจสอบ/อนุมัติคำขอในโมดูล\n- ดูสถิติและรายงานในโมดูล")
            if st.button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล", use_container_width=True):
                st.session_state["route"] = "login_module_admin"
                st.rerun()

    # ---- การ์ด: แอดมินใหญ่ ----
    with col3:
        with st.container(border=True):
            st.subheader("🛡️ แอดมินใหญ่")
            st.write("- จัดการสิทธิ์เข้าระบบ\n- ออกรายงานรวมเพื่อบริหาร")
            if st.button("🔐 เข้าสู่ระบบแอดมินใหญ่", use_container_width=True):
                st.session_state["route"] = "login_superadmin"
                st.rerun()

    # ---- การ์ด: ฝ่ายบริหาร ----
    with col4:
        with st.container(border=True):
            st.subheader("🏫 ฝ่ายบริหาร (Executive)")
            st.write("- สำหรับผู้บริหารโรงเรียน\n- ดูรายงานภาพรวมทั้งหมด")
            if st.button("🔐 เข้าสู่ระบบฝ่ายบริหาร", use_container_width=True):
                st.session_state["route"] = "login_executive"
                st.rerun()

    # ---- เครดิต ----
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
    # 🧑‍💻 เครดิตผู้พัฒนา (Footer)
    # ==========================
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
# 🔑 หน้าล็อกอิน
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

