import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==========================
# 🔧 ตั้งค่าหน้าเว็บ
# ==========================
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

# ==========================
# 🎨 CSS และฟอนต์
# ==========================
def inject_fonts_and_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Noto Sans Thai', sans-serif;
    }
    .kys-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.1);
        padding: 24px 22px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 280px;
    }
    .kys-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 10px 18px;
        border-radius: 10px;
        background: #0056b3;
        color: #fff !important;
        font-weight: 600;
        text-decoration: none !important;
    }
    .kys-btn:hover { background: #003d80; }
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

route = st.session_state["route"]

# ==========================
# 🏠 หน้าแรก (Home)
# ==========================
def page_home():
    st.image("https://i.imgur.com/IybX4sn.jpeg", use_column_width=True)
    st.markdown("<h2 style='text-align:center;color:#003366;'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>", unsafe_allow_html=True)
    st.markdown("ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลอย่างโปร่งใสและตรวจสอบได้")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.subheader("👩‍🏫 สำหรับครูผู้สอน")
        st.write("- จัดการ/ปรับปรุงข้อมูลส่วนบุคคล\n- ส่งคำขอลา/อบรม\n- อัปโหลดเอกสาร")
        if st.button("🔐 เข้าสู่ระบบครูผู้สอน"):
            st.session_state["route"] = "login_teacher"
            st.rerun()

    with col2:
        st.subheader("⚙️ ผู้ดูแลโมดูล")
        st.write("- ตรวจสอบ/อนุมัติคำขอในโมดูล\n- ดูสถิติและรายงานในโมดูล")
        if st.button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล"):
            st.session_state["route"] = "login_module_admin"
            st.rerun()

    with col3:
        st.subheader("🛡️ แอดมินใหญ่")
        st.write("- จัดการสิทธิ์เข้าระบบ\n- ออกรายงานรวมเพื่อบริหาร")
        if st.button("🔐 เข้าสู่ระบบแอดมินใหญ่"):
            st.session_state["route"] = "login_superadmin"
            st.rerun()

    with col4:
        st.subheader("🏫 ฝ่ายบริหาร (Executive)")
        st.write("- สำหรับผู้บริหารโรงเรียน\n- ดูรายงานภาพรวมทั้งหมด")
        if st.button("🔐 เข้าสู่ระบบฝ่ายบริหาร"):
            st.session_state["route"] = "login_executive"
            st.rerun()

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
def teacher_portal():
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับครู")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

def module_portal():
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับผู้ดูแลโมดูล")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

def superadmin_portal():
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับแอดมินใหญ่")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

def executive_portal():
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)")
    st.write("นี่คือตัวอย่างหน้า Portal สำหรับฝ่ายบริหาร")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

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

# จุดเริ่มต้นของโปรแกรม
if __name__ == "__main__":
    main()
