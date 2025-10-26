# =========================================================
# School HR System — Streamlit + Local CSV (RBAC)
# =========================================================

import base64
from pathlib import Path

import pandas as pd
import streamlit as st

# ======================
# ตั้งค่าหน้าเว็บ
# ======================
st.set_page_config(page_title="School HR System", page_icon="🏫", layout="wide")

BASE = Path(__file__).parent.resolve()
ASSETS_DIR = BASE / "assets"
BANNER_PATH = ASSETS_DIR / "banner.jpg"
LOGO_PATH = ASSETS_DIR / "logo.jpg"
CSV_PATH = BASE / "teachers.csv"

# ======================
# Utilities (Banner/Logo)
# ======================
def _img_to_data_uri(path: Path) -> str:
    try:
        if not path.exists():
            return ""
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        ext = path.suffix.lower().replace(".", "")
        mime = "image/jpeg" if ext in {"jpg", "jpeg"} else "image/png"
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""

def show_banner():
    banner_uri = _img_to_data_uri(BANNER_PATH)
    logo_uri = _img_to_data_uri(LOGO_PATH)
    if not banner_uri:
        st.warning("⚠️ ไม่พบไฟล์แบนเนอร์ (assets/banner.jpg)")
        return
    st.markdown(
        f"""
        <div class="hero">
          <img class="hero-img" src="{banner_uri}" alt="banner"/>
          {"<img class='hero-logo' src='"+logo_uri+"' alt='logo'/>" if logo_uri else ""}
          <div class="hero-title">โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ======================
# CSS / Fonts
# ======================
def inject_css():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@300;400;600;700&display=swap');
      html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }

      :root{
        --brand:#0a2342; --muted:#445b66; --soft:#f5f8fb;
        --shadow:0 10px 30px rgba(10,35,66,.10); --radius:14px;
      }

      .page-wrap{ max-width: 1080px; margin: 0 auto; }
      .kys-title{ text-align:center; color:var(--brand); font-weight:800; margin: 12px 0 6px 0; }
      .kys-sub{ text-align:center; color:var(--muted); font-size:14.5px; margin-bottom: 18px; }

      /* ===== HERO ===== */
      .hero{ position: relative; width: 100%; border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); margin: 6px 0 14px 0; }
      .hero-img{ width: 100%; display: block; }
      .hero-logo{ position: absolute; left: 14px; top: 14px; width: 72px; height: auto; border-radius: 12px;
        box-shadow: 0 6px 16px rgba(0,0,0,.25); background: #fff; padding: 6px; }
      .hero-title{ position: absolute; left: 50%; bottom: 22px; transform: translateX(-50%);
        color: #fff; font-weight: 800; font-size: clamp(18px, 2.2vw, 28px);
        text-shadow: 0 6px 16px rgba(0,0,0,.6); background: rgba(0,0,0,.22);
        padding: 8px 14px; border-radius: 12px; }

      /* ===== CARD (อยู่กึ่งกลางจริง ๆ) ===== */
      .kys-card-v2{
        background:#fff; border-radius:var(--radius); box-shadow:var(--shadow);
        padding:24px 28px; margin: 20px auto;
        width:100%; max-width:1080px;

        display:flex;
        flex-direction:column;
        align-items:center;
        justify-content:center;
        text-align:center;
      }

      .kys-card-v2 h3{
        margin-bottom:8px;
        color:var(--brand);
        font-weight:800;
        text-align:center;
      }

      .kys-card-v2 .kys-role{
        color:#5b6b7a;
        margin-bottom:6px;
        font-weight:600;
        text-align:center;
      }

      .kys-card-v2 ul{
        list-style-position: inside;
        padding-left:0;
        margin:8px 0;
        text-align:center;
        line-height:1.6;
        color:#2f4759;
      }
      .kys-card-v2 li{ margin-bottom:6px; text-align:center; }

      /* ===== BUTTON ===== */
      .stButton>button{
        width:80% !important;
        background:#0f57c7 !important; color:#fff !important;
        border-radius:12px !important; padding:10px 12px !important;
        border:0 !important; box-shadow:var(--shadow) !important;
        display:block; margin:0 auto;
        font-weight:600; transition:all 0.2s ease;
      }
      .stButton>button:hover{ filter:brightness(1.07); transform:scale(1.03); }

      .kys-footer{ text-align:center; color:#5b6b7a; font-size:13px; margin-top:20px; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ======================
# โหลดข้อมูลผู้ใช้จาก CSV
# ======================
@st.cache_data(ttl=30)
def load_users_df():
    try:
        df = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8").fillna("")
        df.columns = [c.strip().lower() for c in df.columns]
        for c in ("teacher_id", "pin", "role"):
            if c in df:
                df[c] = df[c].astype(str).str.strip()
        return df
    except Exception as e:
        st.error("🚫 โหลดข้อมูลผู้ใช้จาก teachers.csv ไม่สำเร็จ")
        st.exception(e)
        return pd.DataFrame(columns=["teacher_id", "name", "email", "role", "pin"])

# ======================
# ตรวจสอบการล็อกอิน
# ======================
def check_login(uid, pin, allowed_roles):
    df = load_users_df()
    user = df[df["teacher_id"] == str(uid).strip()]
    if user.empty:
        return False, None, "❌ ไม่พบผู้ใช้"
    u = user.iloc[0]
    if str(u["pin"]) != str(pin).strip():
        return False, None, "🔒 PIN ไม่ถูกต้อง"
    u_roles = [r.strip() for r in str(u["role"]).lower().split(",") if r.strip()]
    if allowed_roles and not any(r in allowed_roles for r in u_roles):
        return False, None, "🚫 ไม่มีสิทธิ์เข้าหน้านี้"
    return True, u, None

# ======================
# Layout helpers
# ======================
def contact_block():
    col = st.columns([1,6,1])[1]
    with col:
        st.markdown(
            "<div style='text-align:center; margin-top:10px;'>"
            "<a href='mailto:pakka555@gmail.com' "
            "style='display:inline-block;background:#0f2748;color:#fff;"
            "padding:8px 14px;border-radius:999px;text-decoration:none;box-shadow:0 8px 18px rgba(10,35,66,.18)'>"
            "📧 ติดต่อผู้ดูแลระบบ</a></div>",
            unsafe_allow_html=True,
        )

def footer_once():
    if st.session_state.get("_footer_done"):
        return
    st.session_state["_footer_done"] = True
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("""
        <div class="kys-footer">
          พัฒนาโดย <b>ครูสุพจน์ นามโคตร</b> กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br/>
          School HR System v2 | Powered by Streamlit + CSV
        </div>
    """, unsafe_allow_html=True)

# ----- การ์ดแนวตั้ง (ห่อด้วยคอลัมน์กลางให้กึ่งกลางทั้งบล็อก) -----
def role_card(title_icon, title_text, role_label, bullets, button_text, route_name, key):
    # คอลัมน์ [ซ้าย, กลาง, ขวา] เพื่อบังคับให้การ์ดอยู่กลางหน้าเสมอ
    center_col = st.columns([1, 8, 1])[1]
    with center_col:
        st.markdown('<div class="kys-card-v2">', unsafe_allow_html=True)

        st.markdown(f'<h3>{title_icon} {title_text}</h3>', unsafe_allow_html=True)
        if role_label:
            st.markdown(f'<div class="kys-role">{role_label}</div>', unsafe_allow_html=True)

        if bullets:
            st.markdown("<ul>" + "".join([f"<li>{b}</li>" for b in bullets]) + "</ul>", unsafe_allow_html=True)

        # ปุ่มก็กว้างเต็มคอลัมน์กลาง
        if st.button(f"🔐 {button_text}", key=key, use_container_width=True, type="primary"):
            st.session_state["route"] = route_name
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ======================
# Pages
# ======================
def page_home():
    show_banner()

    st.markdown("<div class='page-wrap'>", unsafe_allow_html=True)
    st.markdown("<h2 class='kys-title'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>", unsafe_allow_html=True)
    st.markdown("<div class='kys-sub'>ครูทุกคนสามารถเข้าสู่ระบบเพื่อจัดการข้อมูลส่วนตัวและงานบุคคลได้</div>", unsafe_allow_html=True)

    # การ์ด: ครูผู้สอน
    role_card(
        title_icon="🧑‍🏫", title_text="สำหรับครูผู้สอน", role_label="Teacher",
        bullets=[
            "จัดการ/ปรับปรุงข้อมูลส่วนบุคคล",
            "ส่งคำขอลา (ลา/ไปราชการ/อบรม ฯลฯ) และตรวจสอบสถานะ",
            "อัปโหลดเอกสารงานบุคคล (ฟอร์ม/ใบอนุญาต/แฟ้มสะสมงาน)"
        ],
        button_text="เข้าสู่ระบบครู",
        route_name="login_teacher",
        key="btn_teacher_card"
    )

    # การ์ด: ผู้ดูแลโมดูล
    role_card(
        title_icon="⚙️", title_text="ผู้ดูแลโมดูล", role_label="Module Admin",
        bullets=[
            "ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ",
            "ติดตามเอกสาร ปรับแก้ข้อมูลที่จำเป็น",
            "ดูสรุปสถิติและรายงานในโมดูล"
        ],
        button_text="เข้าสู่ระบบผู้ดูแลโมดูล",
        route_name="login_module_admin",
        key="btn_module_card"
    )

    # การ์ด: แอดมินใหญ่
    role_card(
        title_icon="🛡️", title_text="แอดมินใหญ่", role_label="Superadmin",
        bullets=[
            "กำกับดูแลภาพรวมของระบบทั้งหมด",
            "จัดการข้อมูลบุคลากร/สิทธิ์การเข้าใช้",
            "ออกรายงานภาพรวมเพื่อการบริหาร"
        ],
        button_text="เข้าสู่ระบบแอดมินใหญ่",
        route_name="login_superadmin",
        key="btn_superadmin_card"
    )

    # การ์ด: ผู้บริหาร
    role_card(
        title_icon="🏛️", title_text="ฝ่ายบริหาร (Executive)", role_label="Executive",
        bullets=[
            "สำหรับผู้บริหารโรงเรียน",
            "เข้าดูภาพรวมสรุป/รายงานสำคัญ"
        ],
        button_text="เข้าสู่ระบบฝ่ายบริหาร",
        route_name="login_executive",
        key="btn_exec_card"
    )

    contact_block()
    footer_once()
    st.markdown("</div>", unsafe_allow_html=True)

def login_page(title, roles, next_route):
    st.markdown(f"<h3 class='kys-title'>{title}</h3>", unsafe_allow_html=True)
    with st.form("login_form"):
        uid = st.text_input("User ID / Teacher ID")
        pin = st.text_input("PIN", type="password")
        if st.form_submit_button("เข้าสู่ระบบ"):
            ok, user, err = check_login(uid, pin, [r.lower() for r in roles])
            if not ok:
                st.error(err)
            else:
                st.success(f"ยินดีต้อนรับคุณ {user.get('name','')}")
                st.session_state["user"] = dict(user)
                st.session_state["route"] = next_route
                st.rerun()
    st.button("⬅️ กลับหน้าหลัก", on_click=lambda: st.session_state.update({"route": "home"}))
    footer_once()

def teacher_portal():
    st.success("เข้าสู่ระบบในบทบาท: ครูผู้สอน")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของครู เช่น ใบลา/ข้อมูลส่วนตัว")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()

def module_portal():
    st.success("เข้าสู่ระบบในบทบาท: ผู้ดูแลโมดูล")
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูงานบุคคล/อนุมัติคำขอ")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()

def superadmin_portal():
    st.success("เข้าสู่ระบบในบทบาท: แอดมินใหญ่")
    st.info("หน้าตัวอย่างสำหรับต่อยอดระบบภาพรวมและสิทธิ์การใช้งาน")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()

def executive_portal():
    st.success("เข้าสู่ระบบในบทบาท: ฝ่ายบริหาร (Executive)")
    st.info("หน้าตัวอย่างสำหรับต่อยอดรายงาน/สถิติภาพรวมโรงเรียน")
    st.button("ออกจากระบบ", on_click=lambda: st.session_state.update({"route": "home", "user": None}))
    footer_once()

# ======================
# Route Controller
# ======================
def main():
    if "route" not in st.session_state:
        st.session_state["route"] = "home"
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
