import io
import streamlit as st
from pypdf import PdfReader, PdfWriter

# 1. Define Category Structure
CATEGORIES = {
    "Category_A": ["Sub_Category_1.1", "Sub_Category_1.2", "Sub_Category_1.3"],
    "Category_B": ["Sub_Category_2.1", "Sub_Category_2.2"],
    "Category_C": ["Sub_Category_3.1", "Sub_Category_3.2"]
}

# 2. Page Configuration
st.set_page_config(
    page_title="PDF Merger & Auto-Naming Tool",
    page_icon="📄",
    layout="centered"
)

# Professional & Modern Styling (High-Contrast Text & Hover Gradient)
st.markdown("""
<style>
    /* Main Background & Font Styling */
    .stApp {
        background-color: #FAFAFC;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Title & High-Contrast Dark Text */
    h1 {
        color: #0F172A !important;
        font-weight: 700;
        font-size: 2.1rem !important;
        margin-bottom: 0.2rem !important;
    }
    
    h2, h3, h4, label, p, span, div {
        color: #FFFFFF !important;
        font-weight: 500;
    }

    .stCaption {
        color: #334155 !important;
    }

    /* Primary Action Buttons - Normal State */
    .stButton>button {
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: #FFFFFF !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2);
    }

    /* Primary Action Buttons - Hover State (เปลี่ยนสีไล่ระดับ + ลอยขึ้น) */
    .stButton>button:hover {
        background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%) !important;
        color: #FFFFFF !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -3px rgba(168, 85, 247, 0.35) !important;
    }

    /* Primary Action Buttons - Active */
    .stButton>button:active {
        transform: translateY(0px);
        box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.2) !important;
    }

    /* Download Button Hover State */
    div[data-testid="stDownloadButton"]>button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
    }

    div[data-testid="stDownloadButton"]>button:hover {
        background: linear-gradient(135deg, #06B6D4 0%, #10B981 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -3px rgba(6, 182, 212, 0.35) !important;
    }

    /* Small Control Buttons (Reorder & Delete) - High Contrast Text */
    button[data-testid="baseButton-secondary"] {
        background: #F1F5F9 !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    
    button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%) !important;
        color: #000000 !important;
        transform: translateY(-1px);
    }

    /* File Uploader Container */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 2px dashed #94A3B8;
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #6366F1;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("📄 PDF Merger & Naming Tool")
st.write("Streamline your document workflow: merge multiple PDF files and standardize file names instantly.")

st.divider()

# Session State Management
if "file_list" not in st.session_state:
    st.session_state.file_list = []

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Function to handle uploaded files and auto-clear top container
def process_new_files():
    key_name = f"uploader_{st.session_state.uploader_key}"
    uploaded = st.session_state.get(key_name, [])
    
    if uploaded:
        for f in uploaded:
            if not any(item['name'] == f.name and item['file'].size == f.size for item in st.session_state.file_list):
                st.session_state.file_list.append({'name': f.name, 'file': f})
        st.session_state.uploader_key += 1

# 3. File Upload Area
st.subheader("1. Upload PDF Files")
st.file_uploader(
    "Drag & drop PDF files here or click to browse",
    type=["pdf"],
    accept_multiple_files=True,
    key=f"uploader_{st.session_state.uploader_key}",
    on_change=process_new_files,
    label_visibility="collapsed"
)

# 4. File Queue & Reorder Section
if st.session_state.file_list:
    st.write("---")
    st.subheader("📋 Document Queue & Ordering")
    st.caption("Adjust the merging sequence or remove unwanted files below:")
    
    for idx, item in enumerate(st.session_state.file_list):
        col_num, col_name, col_up, col_down, col_del = st.columns([0.6, 5.4, 1, 1, 1])
        
        col_num.markdown(f"**#{idx + 1}**")
        col_name.write(f"📄 {item['name']}")
        
        # Move Up
        if col_up.button("▲", key=f"up_{idx}", help="Move file up"):
            if idx > 0:
                st.session_state.file_list[idx], st.session_state.file_list[idx-1] = st.session_state.file_list[idx-1], st.session_state.file_list[idx]
                st.rerun()
                
        # Move Down
        if col_down.button("▼", key=f"down_{idx}", help="Move file down"):
            if idx < len(st.session_state.file_list) - 1:
                st.session_state.file_list[idx], st.session_state.file_list[idx+1] = st.session_state.file_list[idx+1], st.session_state.file_list[idx]
                st.rerun()
                
        # Remove File
        if col_del.button("✕", key=f"del_{idx}", help="Remove this file"):
            st.session_state.file_list.pop(idx)
            st.rerun()

    # Clear All Button
    if st.button("Clear All Files", use_container_width=False):
        st.session_state.file_list = []
        st.rerun()

st.divider()

# 5. Metadata & Naming Convention
st.subheader("2. Document Naming & Categorization")

col1, col2 = st.columns(2)

with col1:
    selected_main = st.selectbox(
        "Main Category",
        options=list(CATEGORIES.keys())
    )

with col2:
    sub_options = CATEGORIES.get(selected_main, [])
    selected_sub = st.selectbox(
        "Sub Category",
        options=sub_options
    )

default_filename = f"{selected_main}_{selected_sub}_Details"

final_filename = st.text_input(
    "Standardized Filename Output",
    value=default_filename,
    help="You can edit the final file name here before merging."
)

st.divider()

# 6. Merge & Process Section
if st.button("⚡ Merge & Download PDF", use_container_width=True):
    active_items = st.session_state.file_list
    
    if not active_items:
        st.error("Please upload at least one PDF file before processing.")
    elif not final_filename.strip():
        st.error("Please provide a valid filename.")
    else:
        save_filename = final_filename.strip()
        if not save_filename.lower().endswith(".pdf"):
            save_filename += ".pdf"
            
        try:
            with st.spinner("Merging documents, please wait..."):
                writer = PdfWriter()
                for item in active_items:
                    reader = PdfReader(item['file'])
                    for page in reader.pages:
                        writer.add_page(page)
                
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                output_pdf.seek(0)
                
            st.success("PDF merged and named successfully!")
            
            st.download_button(
                label=f"⬇️ Download {save_filename}",
                data=output_pdf,
                file_name=save_filename,
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Processing Error: {str(e)}")

st.caption("Designed for automated document management and workflow efficiency.")
