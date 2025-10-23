import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ==========================
# ⚙️ ตั้งค่าหน้าจอ
# ==========================
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

# ==========================
# 🎨 ฟอนต์ + CSS (ปลอดภัย)
# ==========================
def inject_fonts_and_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }

        /* ---------- Title/Subtitle ---------- */
        .kys-h1 {
            text-align:center; color:#0B3C73;
            font-weight: 800; margin: 6px 0 8px 0;
            font-size: clamp(22px, 2.6vw, 32px);
        }
        .kys-sub {
            text-align:center; color:#4e657a; margin-bottom: 12px;
        }

        /* ---------- Grid Card ---------- */
        .kys-box{
            background:#fff; border-radius:16px; box-shadow: 0 6px 18px rgba(0,0,0,.08);
            padding: 18px 18px 12px 18px; display:block;
        }
        .kys-box h3{
            margin:0 0 8px 0; font-weight:800; color:#0B3C73;
            font-size: clamp(18px, 2.1vw, 24px);
        }
        .kys-body{    /* ความสูงส่วนเนื้อหา ให้เท่ากัน 4 การ์ด */
            min-height: 92px;
        }
        .kys-box ul{ margin: 0 0 6px 18px; line-height:1.55; color:#2b3e50; }

        /* ---------- ปุ่มเข้าใช้งาน ---------- */
        .stButton > button {
            width: 100% !important;
            background: #0D47A1 !important;    /* น้ำเงินกรม */
            color: #fff !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 10px 0 !important;
            font-weight: 700 !important;
            font-size: 15px !important;
            box-shadow: 0 3px 10px rgba(0,0,0,0.12) !important;
            transition: all .18s ease !important;
        }
        .stButton > button:hover{
            background:#002171 !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(0,0,0,.22) !important;
        }

        /* ---------- เครดิต ---------- */
        .kys-credit{
            margin-top: 22px; text-align:center; color:#5c7080; font-size: 13.5px;
        }
        .kys-credit small{color:#7b8a97;}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_fonts_and_css()

# ==========================
# 🔗 เชื่อม Google Sheets (ผ่าน st.secrets)
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

@st.cache_data(ttl=60, show_spinner=False)
def load_users_df():
    """อ่านตาราง users จาก Google Sheets -> DataFrame"""
    try:
        client = get_gs_client()
        sheet_id = st.secrets["gsheets"]["users_sheet_id"]
        ws_name = st.secrets["gsheets"]["users_worksheet"]
        sh = client.open_by_key(sheet_id)
        ws = sh.worksheet(ws_name)
        data = ws.get_all_records()
        df = pd.DataFrame(data).fillna("")
        # มาตรฐานฟิลด์
        for col in ("teacher_id", "pin", "role", "name"):
            if col not in df.columns:
                df[col] = ""
        df["teacher_id"] = df["teacher_id"].astype(str).str.strip()
        df["pin"] = df["pin"].astype(str).str.strip()
        df["role"] = df["role"].astype(str).str.lower().str.strip()
        return df
    except Exception as e:
        st.error(f"โหลดรายชื่อผู้ใช้ไม่ได้: {e}")
        return pd.DataFrame(columns=["teacher_id","name","email","role","pin"])

def check_login(user_id, pin, allowed_roles):
    df = load_users_df()
    r = df[df["teacher_id"] == str(user_id).strip()]
    if r.empty:    return False, None, "❌ ไม่พบผู้ใช้"
    u = r.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"
    if allowed_roles and u["role"] not in allowed_roles:
        return False, None, "🚫 สิทธิ์ไม่พอสำหรับหน้านี้"
    return True, u, None

# ==========================
# 🧭 Routing
# ==========================
if "route" not in st.session_state:
    st.session_state["route"] = "home"
route = st.session_state["route"]

# ==========================
# 🏠 Home
# ==========================
BANNER_URL = ""   # ใส่ลิงก์รูปแบนเนอร์ถ้ามี (ว่างไว้ได้)

def page_home():
    if BANNER_URL:
        st.image(BANNER_URL, use_column_width=True)

    st.markdown("<div class='kys-h1'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</div>", unsafe_allow_html=True)
    st.markdown("<div class='kys-sub'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="kys-box">
          <h3>👩‍🏫 สำหรับครูผู้สอน</h3>
          <div class="kys-body">
            <ul>
              <li>จัดการ/ปรับปรุงข้อมูลส่วนบุคคล</li>
              <li>ส่งคำขอลา/อบรม</li>
              <li>อัปโหลดเอกสาร</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐 เข้าสู่ระบบครูผู้สอน", key="btn_teacher"):
            st.session_state["route"] = "login_teacher"; st.rerun()

    with c2:
        st.markdown("""
        <div class="kys-box">
          <h3>⚙️ ผู้ดูแลโมดูล</h3>
          <div class="kys-body">
            <ul>
              <li>ตรวจสอบ/อนุมัติคำขอในโมดูล</li>
              <li>ดูสถิติและรายงานในโมดูล</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐 เข้าสู่ระบบผู้ดูแลโมดูล", key="btn_mod"):
            st.session_state["route"] = "login_module_admin"; st.rerun()

    with c3:
        st.markdown("""
        <div class="kys-box">
          <h3>🛡️ แอดมินใหญ่</h3>
          <div class="kys-body">
            <ul>
              <li>จัดการสิทธิ์เข้าระบบ</li>
              <li>ออกรายงานรวมเพื่อบริหาร</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐 เข้าสู่ระบบแอดมินใหญ่", key="btn_super"):
            st.session_state["route"] = "login_superadmin"; st.rerun()

    with c4:
        st.markdown("""
        <div class="kys-box">
          <h3>🏫 ฝ่ายบริหาร (Executive)</h3>
          <div class="kys-body">
            <ul>
              <li>สำหรับผู้บริหารโรงเรียน</li>
              <li>ดูรายงานภาพรวมทั้งหมด</li>
            </ul>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔐 เข้าสู่ระบบฝ่ายบริหาร", key="btn_exec"):
            st.session_state["route"] = "login_executive"; st.rerun()

    st.markdown(
        """
        <div class="kys-credit">
            พัฒนาโดย <b>ครูสุพจน์ บ้านกีดกร</b> โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br>
            <small>School HR System v2 | Powered by Streamlit + Google Sheets</small>
        </div>
        """, unsafe_allow_html=True
    )

# ==========================
# 🔑 Login (generic)
# ==========================
def login_page(title: str, roles: list[str], next_route: str):
    st.markdown(f"<div class='kys-h1'>{title}</div>", unsafe_allow_html=True)
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        ok = st.form_submit_button("เข้าสู่ระบบ")
        if ok:
            passed, u, err = check_login(uid, pin, roles)
            if not passed:
                st.error(err)
            else:
                st.success(f"ยินดีต้อนรับคุณ {u.get('name','')}")
                st.session_state["user"] = dict(u)
                st.session_state["route"] = next_route
                st.rerun()
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state["route"] = "home"; st.rerun()

# ==========================
# 🧩 Portal Placeholder
# ==========================
def teacher_portal():
    st.success("คุณกำลังใช้งานในบทบาท: ครูผู้สอน")
    st.info("พื้นที่สำหรับแบบฟอร์ม/งานบุคคลของครู — เติมภายหลังได้")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

def module_portal():
    st.success("คุณกำลังใช้งานในบทบาท: ผู้ดูแลโมดูล")
    st.info("พื้นที่สำหรับงานตรวจคำขอ/สถิติของโมดูล — เติมภายหลังได้")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

def superadmin_portal():
    st.success("คุณกำลังใช้งานในบทบาท: แอดมินใหญ่")
    st.info("พื้นที่สำหรับบริหารสิทธิ์และภาพรวมระบบ — เติมภายหลังได้")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home"}))

def executive_portal():
    st.success("คุณกำลังใช้งานในบทบาท: ฝ่ายบริหาร (Executive)")
    st.info("พื้นที่รายงานภาพรวมสำหรับผู้บริหาร — เติมภายหลังได้")
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

if __name__ == "__main__":
    main()
