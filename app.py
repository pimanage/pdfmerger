import io
import streamlit as st
from pypdf import PdfReader, PdfWriter

# 1. กำหนดโครงสร้างหมวดหมู่
CATEGORIES = {
    "หมวดหลัก_A": ["หมวดย่อย_1.1", "หมวดย่อย_1.2", "หมวดย่อย_1.3"],
    "หมวดหลัก_B": ["หมวดย่อย_2.1", "หมวดย่อย_2.2"],
    "หมวดหลัก_C": ["หมวดย่อย_3.1", "หมวดย่อย_3.2"]
}

# 2. ตั้งค่าหน้าตา Web App
st.set_page_config(
    page_title="✿ PDF Merger & Naming Tool ✿",
    page_icon="✿",
    layout="centered"
)

# Custom CSS ตกแต่งสีพาสเทล
st.markdown("""
<style>
    .stApp {
        background-color: #FFF5F5;
    }
    .stButton>button {
        background-color: #FFC6FF;
        color: #5A4B4B;
        border-radius: 8px;
        border: none;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("✿ PDF Merger & Naming Tool ✿")
st.write("❤ ลากไฟล์ PDF มาวางในกล่องด้านล่างได้เลยค่ะ ❤")

# สร้าง Session State สำหรับเก็บไฟล์ที่ใช้งานจริง
if "pdf_files" not in st.session_state:
    st.session_state.pdf_files = []

# ฟังก์ชันอัปเดตไฟล์จากกล่อง Upload
def sync_uploaded_files():
    # ดึงไฟล์ทั้งหมดจาก Widget
    raw_files = st.session_state.get("uploader_widget", [])
    st.session_state.pdf_files = list(raw_files)

# 3. รวมการจัดการไฟล์ไว้จุดเดียว (อัปโหลด / ลบ / ดูรายการ)
uploaded_raw = st.file_uploader(
    "หรือคลิกเลือกไฟล์ที่นี่ (เลือกได้หลายไฟล์พร้อมกัน)",
    type=["pdf"],
    accept_multiple_files=True,
    key="uploader_widget",
    on_change=sync_uploaded_files
)

# แสดงปุ่มจัดลำดับเฉพาะเมื่อมีไฟล์ในระบบมากกว่า 1 ไฟล์
if len(st.session_state.pdf_files) > 1:
    st.write("---")
    st.subheader("📋 จัดลำดับการรวมไฟล์")
    
    for idx, file in enumerate(st.session_state.pdf_files):
        col_name, col_up, col_down = st.columns([6, 1, 1])
        col_name.text(f"{idx + 1}. {file.name}")
        
        # ปุ่มเลื่อนขึ้น
        if col_up.button("▲", key=f"up_{idx}"):
            if idx > 0:
                st.session_state.pdf_files[idx], st.session_state.pdf_files[idx-1] = st.session_state.pdf_files[idx-1], st.session_state.pdf_files[idx]
                st.rerun()
                
        # ปุ่มเลื่อนลง
        if col_down.button("▼", key=f"down_{idx}"):
            if idx < len(st.session_state.pdf_files) - 1:
                st.session_state.pdf_files[idx], st.session_state.pdf_files[idx+1] = st.session_state.pdf_files[idx+1], st.session_state.pdf_files[idx]
                st.rerun()

st.write("---")

# 4. Dropdown เลือกหมวดหมู่หลัก และหมวดย่อย
selected_main = st.selectbox(
    "🎀 1. เลือกหมวดหลัก:",
    options=list(CATEGORIES.keys())
)

sub_options = CATEGORIES.get(selected_main, [])
selected_sub = st.selectbox(
    "🎀 2. เลือกหมวดย่อย:",
    options=sub_options
)

# 5. คำนวณชื่อไฟล์ตั้งต้น และช่องให้แก้ไข
default_filename = f"{selected_main}_{selected_sub}_[ระบุรายละเอียด]"

final_filename = st.text_input(
    "✏ 3. ชื่อไฟล์ระบบตั้งให้ (แก้ไขเพิ่มเติมตรงนี้ได้เลยค่ะ):",
    value=default_filename
)

st.write("---")

# 6. ปุ่มรวมไฟล์และดาวน์โหลด
if st.button("★  เริ่มบันทึกและรวมไฟล์  ★", use_container_width=True):
    # ดึงไฟล์ล่าสุดจาก Session State
    active_files = st.session_state.pdf_files
    
    if not active_files:
        st.error("แจ้งเตือน: ยังไม่มีไฟล์ PDF ในระบบเลยค่ะ")
    elif not final_filename.strip():
        st.error("แจ้งเตือน: กรุณาใส่ชื่อไฟล์ด้วยนะคะ")
    else:
        save_filename = final_filename.strip()
        if not save_filename.lower().endswith(".pdf"):
            save_filename += ".pdf"
            
        try:
            with st.spinner("ระบบกำลังรวมไฟล์ให้อยู่นะคะ..."):
                writer = PdfWriter()
                for pdf_file in active_files:
                    reader = PdfReader(pdf_file)
                    for page in reader.pages:
                        writer.add_page(page)
                
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                output_pdf.seek(0)
                
            st.success("ระบบรวมไฟล์และตั้งชื่อให้เรียบร้อยแล้วนะคะ ✿")
            
            st.download_button(
                label=f"⬇️ บันทึกไฟล์ {save_filename}",
                data=output_pdf,
                file_name=save_filename,
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด ระบบหลังบ้านมีปัญหา: {str(e)}")
