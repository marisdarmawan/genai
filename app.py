import streamlit as st
from openai import OpenAI
import io

# Import library untuk berbagai tipe file (pastikan ini ada dan sesuai)
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None
try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None
try:
    from pptx import Presentation
except ImportError:
    Presentation = None
try:
    import pandas as pd
except ImportError:
    pd = None

# --- App Configuration ---
st.set_page_config(
    page_title="🤖 Chatbot Assistant",
    page_icon="🐑",
    layout="centered", # Bisa juga "wide" jika ingin lebih banyak ruang
)

# --- Secrets Management ---
api_key = st.secrets.get("OPENROUTER_API_KEY", None)

# --- OpenAI Client Initialization ---
client = None
if api_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
else:
    st.error("API Key OpenRouter tidak ditemukan. Harap atur di Streamlit Secrets.")

# --- UI Elements ---
st.title("🤖 Chatbot Assistant")

# --- Anchor untuk navigasi scroll ---
st.markdown("<a id='upload_section_anchor'></a>", unsafe_allow_html=True) # Jangkar HTML tidak terlihat

st.caption("Unggah dokumen untuk dibahas atau langsung ketik pesan Anda di bawah.")

# Inisialisasi session state jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hai! Aku adalah Chatbot yang siap membantu kamu!"}
    ]
if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# --- File Uploader ---
supported_file_types = ["txt", "md"]
if PdfReader: supported_file_types.append("pdf")
if DocxDocument: supported_file_types.extend(["docx", "doc"])
if Presentation: supported_file_types.append("pptx")
if pd: supported_file_types.extend(["xlsx", "xls"])

uploaded_file = st.file_uploader(
    f"Unggah dokumen (opsional, .{', .'.join(supported_file_types)})",
    type=supported_file_types,
    help="Unggah file untuk dibahas dengan chatbot."
    # Anda bisa memberikan 'key' unik jika diperlukan untuk referensi lain, misal: key="file_uploader_widget"
)

# --- Tombol untuk Kembali ke Awal/Upload Dokumen Baru (YANG MEMBERSIHKAN CHAT) ---
# Tombol ini tetap ada jika Anda masih menginginkannya
if st.button("🔄 Mulai Baru / Ganti Dokumen (Bersihkan Chat)"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Hai! Silakan unggah dokumen baru atau ketik pesanmu."}
    ]
    st.session_state.uploaded_file_content = None
    st.session_state.uploaded_file_name = None
    st.rerun()

st.markdown("---") # Pemisah visual

# --- Logika Pemrosesan File ---
# (Logika pemrosesan file Anda dari contoh sebelumnya diletakkan di sini)
# ...
if uploaded_file is not None:
    st.session_state.uploaded_file_name = uploaded_file.name
    extracted_text = ""
    file_processed_successfully = False
    try:
        file_content_bytes = uploaded_file.getvalue()
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == "txt" or uploaded_file.type == "text/plain" or file_extension == "md" or uploaded_file.type == "text/markdown":
            extracted_text = file_content_bytes.decode("utf-8", errors="replace")
            file_processed_successfully = True
        elif file_extension == "pdf" and PdfReader:
            try:
                pdf_reader = PdfReader(io.BytesIO(file_content_bytes))
                for page in pdf_reader.pages: extracted_text += page.extract_text() + "\n"
                file_processed_successfully = True
            except Exception as e: st.error(f"Gagal membaca PDF: {e}")
        elif (file_extension == "docx" or file_extension == "doc") and DocxDocument:
            if file_extension == "docx":
                try:
                    doc = DocxDocument(io.BytesIO(file_content_bytes))
                    for para in doc.paragraphs: extracted_text += para.text + "\n"
                    for table in doc.tables:
                        for row in table.rows:
                            for cell in row.cells: extracted_text += cell.text + "\t"
                            extracted_text += "\n"
                    file_processed_successfully = True
                except Exception as e: st.error(f"Gagal membaca DOCX: {e}")
            else: st.warning(".doc mungkin tidak didukung penuh. Coba konversi ke .docx.")
        elif file_extension == "pptx" and Presentation:
            try:
                prs = Presentation(io.BytesIO(file_content_bytes))
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"): extracted_text += shape.text + "\n"
                file_processed_successfully = True
            except Exception as e: st.error(f"Gagal membaca PPTX: {e}")
        elif (file_extension == "xlsx" or file_extension == "xls") and pd:
            try:
                xls_file = pd.ExcelFile(io.BytesIO(file_content_bytes))
                for sheet_name in xls_file.sheet_names:
                    df = xls_file.parse(sheet_name)
                    extracted_text += f"--- Sheet: {sheet_name} ---\n{df.to_string(index=False)}\n\n"
                file_processed_successfully = True
            except Exception as e: st.error(f"Gagal membaca Excel: {e}")
        else:
            if uploaded_file.name:
                st.warning(f"Tipe file '{file_extension}' tidak didukung atau library yang dibutuhkan tidak terinstal.")

        if file_processed_successfully and extracted_text.strip():
            st.session_state.uploaded_file_content = extracted_text
            user_upload_message = f"Saya telah mengunggah file: '{st.session_state.uploaded_file_name}'. Mohon gunakan konteks dari file ini untuk pertanyaan saya selanjutnya."
            assistant_ack_message = f"Baik, saya telah menerima file '{st.session_state.uploaded_file_name}'. Silakan ajukan pertanyaan Anda terkait dokumen ini."
            
            last_user_message = ""
            if len(st.session_state.messages) > 1 and st.session_state.messages[-2]["role"] == "user":
                last_user_message = st.session_state.messages[-2]["content"]
            
            if not last_user_message.startswith("Saya telah mengunggah file:") or st.session_state.uploaded_file_name not in last_user_message:
                st.session_state.messages.append({"role": "user", "content": user_upload_message})
                st.session_state.messages.append({"role": "assistant", "content": assistant_ack_message})
        elif file_processed_successfully and not extracted_text.strip():
            st.info(f"File '{st.session_state.uploaded_file_name}' berhasil diproses tetapi tidak ada teks yang bisa diekstrak.")
            st.session_state.uploaded_file_content = None
        elif not file_processed_successfully and uploaded_file:
             st.session_state.uploaded_file_content = None
             st.session_state.uploaded_file_name = None

    except Exception as e:
        st.error(f"Terjadi kesalahan umum saat memproses file '{uploaded_file.name}': {e}")
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_name = None

# --- Tampilkan Pesan Chat yang Sudah Ada ---
# Gunakan st.container untuk mengelompokkan pesan chat jika perlu, atau biarkan seperti ini
chat_container = st.container() # Opsional, tapi bisa membantu jika ingin mengontrol tinggi
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- Tombol Scroll ke Atas (TIDAK MEMBERSIHKAN CHAT) ---
# Diletakkan sebelum chat_input agar mudah diakses jika chat sudah panjang
st.link_button("⬆️ Ke Bagian Upload Dokumen", "#upload_section_anchor")

# --- Input Chat ---
user_prompt = st.chat_input("Ketik pesanmu untuk chatbot di sini...")

# --- Logika Chat (setelah user_prompt) ---
# (Logika chat input dan interaksi dengan LLM Anda tetap sama seperti sebelumnya)
# ...
if user_prompt and client:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user", avatar="👤"): # Menambahkan avatar contoh
        st.markdown(user_prompt)

    with st.chat_message("assistant", avatar="🤖"): # Menambahkan avatar contoh
        message_placeholder = st.empty()
        full_response = ""
        try:
            payload_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-0528:free",
                messages=payload_messages,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Oops! Terjadi kesalahan: {e}")
            full_response = "Maaf, aku sedang tidak bisa membantumu saat ini. 🥺"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

elif not client and user_prompt:
    st.warning("Chatbot tidak aktif karena API Key belum dikonfigurasi dengan benar.")


# --- Sidebar ---
with st.sidebar:
    st.header("Tentang Bot Ini")
    # ... (konten sidebar lainnya tetap sama) ...
    st.markdown("---")
    # Tombol "Mulai Percakapan Baru" di sidebar (yang membersihkan chat)
    if st.button("Mulai Percakapan Baru (Sidebar)"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hai! Silahkan unggah dokumen baru atau ketik pesanmu."}
        ]
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_name = None
        st.rerun()
    st.markdown("---")
    st.markdown("Dibuat oleh Mohammad Aris Darmawan")
