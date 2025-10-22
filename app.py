
import os, io, datetime as dt
from typing import Dict, Any, List, Set
import streamlit as st
import pandas as pd
from PyPDF2 import PdfMerger
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm

APP_TITLE = "ระบบงานบุคคลโรงเรียน"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
TEACHER_CSV = "teachers.csv"
LOGO_PATH = "assets/school_logo.png"

# ---------- Modules dictionary ----------
MODULES = {
    "profile": "ข้อมูลส่วนตัว",
    "gp7": "ก.พ.7",
    "decorations": "เครื่องราช",
    "awards": "รางวัล",
    "promotion": "เลื่อนขั้นเงินเดือน",
    "leave": "ใบลา",
    "offsite": "อนุญาตนอกสถานศึกษา",
    "pa": "ข้อตกลง PA (Hybrid)",
    "training": "ไปราชการ/อบรม",
    "training_report": "รายงานผลการอบรม",
}

DEFAULT_SECTIONS = [
    "01_ปกหน้า_หลัง",
    "02_บันทึกข้อความ",
    "03_ส่วนต้น_คำนำ_สารบัญ",
    "04_ข้อมูลส่วนตัว",
    "05_ส่วนที่1_ข้อตกลงในการพัฒนางาน",
    "06_ส่วนที่2_ประเด็นท้าทาย",
    "07_ความเห็นผู้บริหาร_ลายเซ็น",
]

# ---------- Data helpers ----------
@st.cache_data
def load_teachers():
    cols = ["teacher_id","name","email","department","pin","role","admin_modules"]
    if not os.path.exists(TEACHER_CSV):
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(TEACHER_CSV, dtype=str).fillna("")
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df[cols]

def get_teacher(tid: str):
    df = load_teachers()
    m = df[df["teacher_id"].astype(str).str.strip()==str(tid).strip()]
    return None if m.empty else m.iloc[0]

def ensure_dirs(tid: str):
    base = os.path.join(DATA_DIR, "uploads", tid)
    os.makedirs(base, exist_ok=True)
    for s in DEFAULT_SECTIONS:
        os.makedirs(os.path.join(base, s), exist_ok=True)

def save_upload(tid: str, section: str, file):
    ensure_dirs(tid)
    fname = f"{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}_{file.name}"
    path = os.path.join(DATA_DIR, "uploads", tid, section, fname)
    with open(path, "wb") as f:
        f.write(file.getbuffer())
    return path

def list_files(tid: str):
    root = os.path.join(DATA_DIR, "uploads", tid)
    rows = []
    for s in DEFAULT_SECTIONS:
        p = os.path.join(root, s)
        if not os.path.exists(p): 
            continue
        for fn in sorted(os.listdir(p)):
            rows.append({"section": s, "filename": fn, "path": os.path.join(p, fn), "uploaded_at": fn[:15]})
    return pd.DataFrame(rows)

def gen_form_pdf_bytes(tid: str, name: str, form: Dict[str, Any]):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.6*cm, bottomMargin=1.6*cm)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("ข้อตกลงในการพัฒนางาน (PA) — จากแบบฟอร์ม", styles["Heading1"]))
    story.append(Paragraph(f"ครู: {name}  |  รหัส: {tid}", styles["Normal"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("สรุปย่อ", styles["Heading2"]))
    story.append(Paragraph(form.get("summary",""), styles["Normal"]))
    doc.build(story); buf.seek(0)
    return buf.read()

def merge_full_book(tid: str, sections: List[str], form_pdf: bytes|None):
    merger = PdfMerger()
    added = False
    if form_pdf: merger.append(io.BytesIO(form_pdf)); added=True
    df = list_files(tid)
    for sec in sections:
        dd = df[df["section"]==sec].sort_values("uploaded_at")
        for _, r in dd.iterrows():
            p = r["path"]
            if p.lower().endswith(".pdf"):
                try: merger.append(p); added=True
                except: pass
    if not added: return None
    out = io.BytesIO(); merger.write(out); merger.close(); out.seek(0)
    return out.read()

# ---------- UI base ----------
st.set_page_config(page_title=APP_TITLE, page_icon="📘", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans Thai', sans-serif; }
.stButton>button { border-radius: .7rem; padding: .6rem 1rem; font-weight: 600; }
.card {border-radius: 16px; padding: 16px; background:#fff; border:1px solid #e5e7eb; box-shadow:0 6px 14px rgba(2,6,23,.06);}
</style>
""", unsafe_allow_html=True)

# Prefill ?tid=
try: qp = st.query_params
except: qp = st.experimental_get_query_params()
prefill_tid = qp.get("tid",[None])[0] if isinstance(qp, dict) else None

# Session
if "role" not in st.session_state: st.session_state.role = None
if "teacher_id" not in st.session_state: st.session_state.teacher_id = None
if "admin_permissions" not in st.session_state: st.session_state.admin_permissions = set()

# Header
c0, c1 = st.columns([1,5])
with c0:
    if os.path.exists(LOGO_PATH): st.image(LOGO_PATH, width=72)
with c1:
    st.title(APP_TITLE)
    st.caption("Starter รองรับบทบาทหลายระดับ — ครู / แอดมินโมดูล / แอดมินใหญ่")

with st.sidebar:
    page = st.radio("เมนู", ["หน้าแรก", "สำหรับผู้ใช้", "สำหรับผู้ดูแล"], index=0)

# -------- หน้าแรก (ใหม่) --------
def show_home():
    import streamlit as st
    from datetime import datetime
    import os

    # ---------- Logo + Title ----------
    col1, col2 = st.columns([1, 4])
    with col1:
        if os.path.exists("logo.png"):
            st.image("logo.png", width=160)
    with col2:
        st.markdown(
            """
            <h1 style='font-size:42px; font-weight:700; color:#0a2342; margin-bottom:0'>
                ระบบบริหารงานบุคคลโรงเรียนอนุบาลวัดคลองใหญ่
            </h1>
            <p style='color:#4f5b66; margin-top:4px; font-size:17px'>
                ช่วยให้ครูและบุคลากรจัดการข้อมูลบุคลากรได้อย่างมีระบบ โปร่งใส และตรวจสอบได้
            </p>
            """,
            unsafe_allow_html=True
        )


# ---------------- Routing (สลับหน้า) ----------------
if page == "หน้าแรก":
    show_home()

elif page == "สำหรับผู้ใช้":
    st.subheader("เข้าสู่ระบบผู้ใช้ (ครู)")
    # TODO: วางโค้ดเดิมส่วนล็อกอินครูของครูหนึ่งไว้ตรงนี้
    # ตัวอย่าง:
    # tid = st.text_input("Teacher ID")
    # pin = st.text_input("PIN", type="password")
    # if st.button("เข้าสู่ระบบ"):
    #     ...

elif page == "สำหรับผู้ดูแล":
    st.subheader("เข้าสู่ระบบผู้ดูแล")
    # TODO: วางโค้ดเดิมส่วนล็อกอินผู้ดูแล / module_admin / superadmin ไว้ตรงนี้

    st.markdown("---")

    
    # ---------- Theme CSS ----------
    st.markdown(
        """
        <style>
        body {
            background-color: #f5f8fb;
        }
        .role-card {
            background-color: #eef4fb;
            border: 1px solid #b5c7e3;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .role-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 5px 12px rgba(0,0,0,0.12);
        }
        .role-title {
            font-size: 22px;
            color: #0a2342;
            font-weight: 700;
        }
        .role-sub {
            color: #333;
            font-size: 16px;
            margin-top: 10px;
        }
        .stButton>button {
            background-color: #1e3a8a;
            color: white !important;
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
            border: none;
            transition: background-color 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #1d4ed8;
        }
        .footer {
            text-align: right;
            color: #555;
            font-size: 14px;
            margin-top: 40px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ---------- Cards Section ----------
    colA, colB, colC = st.columns(3)

    with colA:
        st.markdown(
            """
            <div class="role-card">
                <div class="role-title">👩‍🏫 สำหรับครูผู้สอน</div>
                <div class="role-sub">
                    - จัดการ/ปรับปรุงข้อมูลส่วนบุคคล<br>
                    - ส่งคำขอลา / บันทึกปฏิบัติงาน / ตรวจสอบสถานะ<br>
                    - อัปโหลดแบบฟอร์ม (ใบลา, PA, แฟ้มสะสมผลงาน)<br>
                    - ตรวจสอบผลประเมินและข้อมูลประจำปี
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("➡️ เข้าสู่ระบบครู"):
            st.session_state.menu = "สำหรับผู้ใช้"
            st.experimental_rerun()

    with colB:
        st.markdown(
            """
            <div class="role-card">
                <div class="role-title">🧩 ผู้ดูแลโมดูล</div>
                <div class="role-sub">
                    - ตรวจสอบ/อนุมัติคำขอในโมดูลที่รับผิดชอบ<br>
                    - ปรับแก้ข้อมูลของเอกสารที่เกี่ยวข้อง<br>
                    - สรุปรายงานและสถิติภายในโมดูล
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("➡️ เข้าสู่ระบบผู้ดูแลโมดูล"):
            st.session_state.menu = "สำหรับผู้ดูแล"
            st.experimental_rerun()

    with colC:
        st.markdown(
            """
            <div class="role-card">
                <div class="role-title">🛡️ แอดมินใหญ่</div>
                <div class="role-sub">
                    - ดูแลระบบทั้งหมด กำหนดสิทธิ์และผู้ใช้งาน<br>
                    - จัดการข้อมูลบุคลากร/สิทธิ์เข้าถึงระบบ<br>
                    - ออกรายงานภาพรวมเพื่อการบริหาร
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("➡️ เข้าสู่ระบบแอดมินใหญ่"):
            st.session_state.menu = "สำหรับผู้ดูแล"
            st.experimental_rerun()

    # ---------- Footer ----------
    st.markdown(
        """
        <div class="footer">
            พัฒนาโดย <b>กลุ่มบริหารงานบุคคล โรงเรียนอนุบาลวัดคลองใหญ่ จังหวัดตราด</b><br>
            <span style='font-size:13px'>เพื่อยกระดับการบริหารจัดการบุคลากรให้ทันสมัย โปร่งใส และตรวจสอบได้</span>
        </div>
        """,
        unsafe_allow_html=True
    )


if page == "หน้าแรก":
    show_home()

# ---------- ผู้ใช้ (ครู) ----------
elif page == "สำหรับผู้ใช้":
    st.subheader("เข้าสู่ระบบผู้ใช้ (ครู)")
    tid = st.text_input("Teacher ID", value=prefill_tid or "")
    pin = st.text_input("PIN", type="password")
    if st.button("เข้าสู่ระบบครู"):
        row = get_teacher(tid)
        if row is None or str(row["pin"]).strip()!=pin.strip():
            st.error("รหัสหรือ PIN ไม่ถูกต้อง")
        elif row["role"] not in ["teacher", "module_admin", "superadmin"]:
            st.error("บทบาทบัญชีนี้ไม่ใช่ผู้ใช้")
        else:
            st.session_state.role = row["role"]
            st.session_state.teacher_id = tid.strip()
            # ถ้าเป็น module_admin/superadmin ก็ยังเข้าโหมดครูได้
            st.success(f"ยินดีต้อนรับ {row['name']}")
            st.rerun()

    if st.session_state.teacher_id:
        row = get_teacher(st.session_state.teacher_id)
        name = row["name"]
        st.markdown(f"### เมนูหลักสำหรับครู — {name} ({st.session_state.teacher_id})")

        # grid buttons
        colA, colB = st.columns(2)
        with colA:
            if st.button("👤 ข้อมูลส่วนตัว", use_container_width=True): st.session_state.view = "profile"
            if st.button("📜 ก.พ.7", use_container_width=True): st.session_state.view = "gp7"
            if st.button("🏅 เครื่องราช", use_container_width=True): st.session_state.view = "decorations"
            if st.button("🏆 รางวัล", use_container_width=True): st.session_state.view = "awards"
            if st.button("💰 เลื่อนขั้นเงินเดือน", use_container_width=True): st.session_state.view = "promotion"
        with colB:
            if st.button("📝 ใบลา", use_container_width=True): st.session_state.view = "leave"
            if st.button("🚶 อนุญาตนอกสถานศึกษา", use_container_width=True): st.session_state.view = "offsite"
            if st.button("📘 ข้อตกลง PA (Hybrid)", use_container_width=True): st.session_state.view = "pa"
            if st.button("🧳 ไปราชการ/อบรม", use_container_width=True): st.session_state.view = "training"
            if st.button("📄 รายงานผลการอบรม", use_container_width=True): st.session_state.view = "training_report"

        view = st.session_state.get("view","pa")
        st.divider()

        if view == "pa":
            st.subheader("PA — Hybrid")
            form = st.session_state.get("pa_form", {})
            summary = st.text_area("สรุปย่อ/หัวข้อสำคัญของ PA", value=form.get("summary",""), height=150)
            if st.button("บันทึกแบบฟอร์ม PA"):
                st.session_state["pa_form"] = {"summary": summary}
                st.success("บันทึกแล้ว")
            st.markdown("##### แนบไฟล์ตามหมวด (PDF)")
            section = st.selectbox("เลือกหมวด", DEFAULT_SECTIONS)
            files = st.file_uploader("เลือกไฟล์", accept_multiple_files=True)
            if st.button("บันทึกไฟล์"):
                if files:
                    for f in files: save_upload(st.session_state.teacher_id, section, f)
                    st.success(f"บันทึก {len(files)} ไฟล์แล้ว")
                else:
                    st.warning("กรุณาเลือกไฟล์")
            st.markdown("##### รวมเป็นเล่ม")
            include_form = st.checkbox("รวม PDF จากฟอร์มเป็นหน้าแรก", value=True)
            if st.button("รวมเป็นเล่ม PDF"):
                form_pdf = None
                if include_form:
                    form_pdf = gen_form_pdf_bytes(st.session_state.teacher_id, name, st.session_state.get("pa_form",{}))
                book = merge_full_book(st.session_state.teacher_id, DEFAULT_SECTIONS, form_pdf)
                if book:
                    st.download_button("ดาวน์โหลดรูปเล่ม PDF", data=book, file_name=f"{st.session_state.teacher_id}_PA_book.pdf", mime="application/pdf")
                else:
                    st.error("ยังไม่มีไฟล์ PDF ให้รวม")
        else:
            st.info("โมดูลนี้เป็นตัวอย่าง/วางโครงไว้พร้อมต่อยอด")

# ---------- ผู้ดูแล ----------
elif page == "สำหรับผู้ดูแล":
    st.subheader("เข้าสู่ระบบผู้ดูแล (ใช้บัญชีใน teachers.csv)")
    tid = st.text_input("Admin ID")
    pin = st.text_input("PIN", type="password")
    if st.button("เข้าสู่ระบบผู้ดูแล"):
        row = get_teacher(tid)
        if row is None or str(row["pin"]).strip()!=pin.strip():
            st.error("Admin ID / PIN ไม่ถูกต้อง")
        elif row["role"] not in ["module_admin","superadmin"]:
            st.error("บัญชีนี้ไม่ได้เป็นผู้ดูแล")
        else:
            st.session_state.role = row["role"]
            st.session_state.teacher_id = tid.strip()
            # เก็บสิทธิ์โมดูล (comma separated)
            mods = [m.strip() for m in row.get("admin_modules","").split(",") if m.strip()]
            st.session_state.admin_permissions = set(mods) if row["role"]=="module_admin" else set(MODULES.keys())
            st.success(f"เข้าสู่ระบบผู้ดูแลสำเร็จ — บทบาท: {row['role']} | โมดูลที่ดูแล: {', '.join(sorted(st.session_state.admin_permissions)) if st.session_state.admin_permissions else 'ทั้งหมด'}")
            st.rerun()

    if st.session_state.role in ["module_admin","superadmin"]:
        df = load_teachers()
        st.markdown("### แดชบอร์ด")
        st.dataframe(df[["teacher_id","name","email","department","role","admin_modules"]], use_container_width=True)

        # ลิงก์เฉพาะครู
        st.markdown("#### ลิงก์เฉพาะครู (?tid=)")
        base = st.text_input("ฐานลิงก์ (เช่น https://your-app.streamlit.app)")
        if base:
            for _, r in df.iterrows():
                st.write(f"- {r['name']} ({r['teacher_id']}): {base}?tid={r['teacher_id']}")

        # เลือกโมดูลที่ต้องการจัดการ (ตามสิทธิ์)
        st.markdown("#### จัดการตามโมดูล")
        allowed: Set[str] = st.session_state.admin_permissions if st.session_state.role=="module_admin" else set(MODULES.keys())
        mods = [ (k,v) for k,v in MODULES.items() if k in allowed ]
        mod_key = st.selectbox("เลือกโมดูล", mods, format_func=lambda x: x[1]) if mods else None

        if mod_key:
            key = mod_key[0]
            st.markdown(f"##### โมดูล: {MODULES[key]}")
            if key == "pa":
                # สรุปไฟล์ PA ต่อครู
                rows = []
                for _, r in df.iterrows():
                    tid = r["teacher_id"]
                    files_df = list_files(tid)
                    rows.append({"teacher_id": tid, "name": r["name"], "ไฟล์ทั้งหมด": len(files_df)})
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.info("โครงสำหรับโมดูลนี้พร้อมต่อยอด (ฟอร์ม/อนุมัติ/รายงาน)")
