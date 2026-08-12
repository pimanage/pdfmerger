import io
import streamlit as st
from pypdf import PdfReader, PdfWriter
from streamlit_drag_drop_sortable import drag_drop_sortable

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

# สร้าง Session State เก็บไฟล์
if "pdf_files_dict" not in st.session_state:
    st.session_state.pdf_files_dict = {}

if "sorted_filenames" not in st.session_state:
    st.session_state.sorted_filenames = []

def sync_uploaded_files():
    uploaded = st.session_state.get("uploader_widget", [])
    current_dict = {f.name: f for f in uploaded}
    st.session_state.pdf_files_dict = current_dict
    
    # อัปเดตรายชื่อไฟล์เพื่อใช้ลากสลับลำดับ
    st.session_state.sorted_filenames = [
        name for name in st.session_state.sorted_filenames if name in current_dict
    ]
    for name in current_dict:
        if name not in st.session_state.sorted_filenames:
            st.session_state.sorted_filenames.append(name)

# 3. อัปโหลดไฟล์
st.file_uploader(
    "หรือคลิกเลือกไฟล์ที่นี่ (เลือกได้หลายไฟล์พร้อมกัน)",
    type=["pdf"],
    accept_multiple_files=True,
    key="uploader_widget",
    on_change=sync_uploaded_files
)

# 4. ส่วน Drag & Drop สลับลำดับไฟล์ด้วยเมาส์
if len(st.session_state.sorted_filenames) > 1:
    st.write("---")
    st.subheader("📋 ลากสลับลำดับการรวมไฟล์ด้านล่างนี้ได้เลยค่ะ")
    
    # ตัวแปลงให้ลากสลับลำดับไฟล์ได้อิสระ
    new_order = drag_drop_sortable(
        st.session_state.sorted_filenames,
        key="pdf_sorter"
    )
    if new_order:
        st.session_state.sorted_filenames = new_order

st.write("---")

# 5. Dropdown เลือกหมวดหมู่หลัก และหมวดย่อย
selected_main = st.selectbox(
    "🎀 1. เลือกหมวดหลัก:",
    options=list(CATEGORIES.keys())
)

sub_options = CATEGORIES.get(selected_main, [])
selected_sub = st.selectbox(
    "🎀 2. เลือกหมวดย่อย:",
    options=sub_options
)

# 6. คำนวณชื่อไฟล์ตั้งต้น และช่องให้แก้ไข
default_filename = f"{selected_main}_{selected_sub}_[ระบุรายละเอียด]"

final_filename = st.text_input(
    "✏ 3. ชื่อไฟล์ระบบตั้งให้ (แก้ไขเพิ่มเติมตรงนี้ได้เลยค่ะ):",
    value=default_filename
)

st.write("---")

# 7. ปุ่มรวมไฟล์และดาวน์โหลด
if st.button("★  เริ่มบันทึกและรวมไฟล์  ★", use_container_width=True):
    ordered_names = st.session_state.sorted_filenames
    files_map = st.session_state.pdf_files_dict
    
    if not ordered_names or not files_map:
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
                # อ่านไฟล์เรียงตามลำดับใหม่ที่ผู้ใช้ลากสลับไว้
                for name in ordered_names:
                    pdf_file = files_map[name]
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
