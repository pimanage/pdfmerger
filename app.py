import io
import streamlit as st
from pypdf import PdfReader, PdfWriter

st.set_page_config(
    page_title="PDF Merge & Auto-Naming Tool",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF Merge & Auto-Naming Tool")
st.markdown("A workplace solution for merging restricted e-signature PDFs and automating **Veeva Vault** document naming compliance.")

st.divider()

# 1. ส่วนเลือกประเภทเอกสาร (Category Selectors)
st.subheader("1. Document Metadata")

col1, col2 = st.columns(2)

with col1:
    main_category = st.selectbox(
        "Main Category",
        options=["Regulatory", "Clinical Operations", "Ethics Committee", "Site Management"],
        index=0
    )

with col2:
    sub_categories = {
        "Regulatory": ["FDA Approval", "Import License", "Safety Report"],
        "Clinical Operations": ["Protocol Amendment", "Informed Consent", "Monitoring Report"],
        "Ethics Committee": ["EC Approval Letter", "Annual Progress Report", "Submission Form"],
        "Site Management": ["Financial Agreement", "CV Investigator", "Training Log"]
    }
    sub_category = st.selectbox(
        "Sub Category",
        options=sub_categories.get(main_category, ["General"]),
        index=0
    )

doc_detail = st.text_input("Document Detail / Site ID", value="Site101_v1.0")

formatted_main = main_category.replace(" ", "")
formatted_sub = sub_category.replace(" ", "")
generated_filename = f"{formatted_main}_{formatted_sub}_{doc_detail}.pdf"

st.info(f"🏷️ **Target Filename:** `{generated_filename}`")

st.divider()

# 2. ส่วนอัปโหลดและประมวลผล PDF
st.subheader("2. Upload PDFs to Merge")

uploaded_files = st.file_uploader(
    "Select or drag & drop restricted e-signature PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"Selected {len(uploaded_files)} file(s).")
    
    if st.button("⚡ Merge & Rename PDF", type="primary"):
        with st.spinner("Processing files..."):
            try:
                writer = PdfWriter()
                
                for uploaded_file in uploaded_files:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        writer.add_page(page)
                
                output_pdf = io.BytesIO()
                writer.write(output_pdf)
                output_pdf.seek(0)
                
                st.balloons()
                st.success("PDF processing completed!")
                
                st.download_button(
                    label=f"⬇️ Download {generated_filename}",
                    data=output_pdf,
                    file_name=generated_filename,
                    mime="application/pdf"
                )
                
            except Exception as e:
                st.error(f"Processing error: {str(e)}")

st.divider()
st.caption("Designed for Clinical Trial Management Systems (CTMS / eTMF) Compliance.")
