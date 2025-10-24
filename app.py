# =========================================================
# School HR System — Streamlit + Local CSV (RBAC)
# =========================================================

import os
import base64
import textwrap
from pathlib import Path

import streamlit as st
import pandas as pd


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
          .hero{ position: relative; width: 100%; border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); margin: 6px 0 14px 0; }
          .hero-img{ width: 100%; display: block; }
          .hero-logo{ position: absolute; left: 14px; top: 14px; width: 72px; height: auto; border-radius: 12px;
            box-shadow: 0 6px 16px rgba(0,0,0,.25); background: #fff; padding: 6px; }
          .hero-title{ position: absolute; left: 50%; bottom: 22px; transform: translateX(-50%);
            color: #fff; font-weight: 800; font-size: clamp(18px, 2.2vw, 28px);
            text-shadow: 0 6px 16px rgba(0,0,0,.6); background: rgba(0,0,0,.22);
            padding: 8px 14px; border-radius: 12px; }
          .kys-card{ background:#fff; border-radius:var(--radius); box-shadow:var(--shadow);
            padding:18px 18px 12px 18px; margin-bottom: 14px; }
          .stButton>button{ width:100% !important; background:#0f57c7 !important; color:#fff !important;
            border-radius:12px !important; padding:10px 12px !important; border:0 !important; box-shadow:var(--shadow) !important; }
          .stButton>button:hover{ filter:brightness(1.06); }
          .kys-footer{ text-align:center; color:#5b6b7a; font-size:13px; margin-top:12px; }
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
# Layout / Pages
# ======================
def footer_once():
    if st.session_state.get("_footer_done"):
        return
    st.session_state["_footer_done"] = True
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("""
        <div class="kys-footer">
          พัฒนาโดย <b>ครูสุพจน์ บ้านกวักดอก</b> โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด<br/>
          School HR System v2 | Powered by Streamlit + CSV
        </div>
    """, unsafe_allow_html=True)


def page_home():
    show_banner()
    st.markdown("<h2 class='kys-title'>ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่</h2>", unsafe_allow_html=True)
    st.markdown("<div class='kys-sub'>ช่วยให้ครูและบุคลากรทางการศึกษาจัดการข้อมูลบุคคลง่าย โปร่งใส และตรวจสอบได้</div>", unsafe_allow_html=True)
    if st.button("👩‍🏫 เข้าสู่ระบบครูผู้สอน"):
        st.session_state["route"] = "login_teacher"
        st.rerun()
    footer_once()


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
    st.info("หน้าตัวอย่างสำหรับต่อยอดเมนูของครู")
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
    elif route == "teacher_portal":
        teacher_portal()


if __name__ == "__main__":
    main()
