import streamlit as st
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="PDF Image Watermark Tool", layout="centered")

st.title("📄 PDF Image Watermark Tool")
st.markdown("Upload a PDF and apply your logo watermark to all pages.")

# ----------------------------
# Upload Files
# ----------------------------
pdf_file = st.file_uploader("Upload PDF File", type=["pdf"])
logo_file = st.file_uploader("Upload Logo Image (PNG/JPG)", type=["png", "jpg", "jpeg"])

# ----------------------------
# Controls
# ----------------------------
if pdf_file and logo_file:

    st.subheader("⚙ Watermark Settings")

    size_percent = st.slider("Watermark Size (% of page width)", 10, 80, 40)
    opacity = st.slider("Transparency (0 = Invisible, 1 = Solid)", 0.05, 1.0, 0.2)
    rotation = st.slider("Rotation (Degrees)", -180, 180, 0)

    position = st.selectbox(
        "Position",
        ["Center", "Top Center", "Bottom Center"]
    )

    # ----------------------------
    # Watermark Function
    # ----------------------------
    def add_watermark(input_pdf, watermark_image):

        reader = PdfReader(input_pdf)
        writer = PdfWriter()

        for page in reader.pages:

            packet = BytesIO()

            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            c = canvas.Canvas(packet, pagesize=(page_width, page_height))

            img = ImageReader(watermark_image)

            watermark_width = page_width * (size_percent / 100)
            watermark_height = watermark_width

            # ---- Position Calculation ----
            if position == "Center":
                x = (page_width - watermark_width) / 2
                y = (page_height - watermark_height) / 2
            elif position == "Top Center":
                x = (page_width - watermark_width) / 2
                y = page_height - watermark_height - 50
            else:  # Bottom Center
                x = (page_width - watermark_width) / 2
                y = 50

            # ---- Apply Transparency ----
            c.saveState()
            c.translate(page_width / 2, page_height / 2)
            c.rotate(rotation)
            c.translate(-page_width / 2, -page_height / 2)
            c.setFillAlpha(opacity)

            c.drawImage(
                img,
                x,
                y,
                width=watermark_width,
                height=watermark_height,
                mask='auto'
            )

            c.restoreState()
            c.save()

            packet.seek(0)
            watermark_pdf = PdfReader(packet)
            page.merge_page(watermark_pdf.pages[0])

            writer.add_page(page)

        output = BytesIO()
        writer.write(output)
        output.seek(0)

        return output

    # ----------------------------
    # Process Button
    # ----------------------------
    if st.button("🚀 Apply Watermark"):

        with st.spinner("Applying watermark..."):
            output_pdf = add_watermark(pdf_file, logo_file)

        st.success("Watermark Applied Successfully!")

        st.download_button(
            "⬇ Download Watermarked PDF",
            output_pdf,
            file_name="watermarked_output.pdf",
            mime="application/pdf"
        )

else:
    st.info("Upload both PDF and Logo Image to continue.")