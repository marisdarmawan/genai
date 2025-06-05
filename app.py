import streamlit as st
from openai import OpenAI
import io

# Import library untuk berbagai tipe file
try:
    from PyPDF2 import PdfReader
except ImportError:
    # st.warning("PyPDF2 tidak terinstal. Fitur upload PDF tidak akan berfungsi.")
    PdfReader = None
try:
    from docx import Document as DocxDocument # Alias untuk menghindari konflik nama jika ada
except ImportError:
    # st.warning("python-docx tidak terinstal. Fitur upload DOC/DOCX tidak akan berfungsi.")
    DocxDocument = None
try:
    from pptx import Presentation
except ImportError:
    # st.warning("python-pptx tidak terinstal. Fitur upload PPT/PPTX tidak akan berfungsi.")
    Presentation = None
try:
    import pandas as pd
except ImportError:
    # st.warning("pandas tidak terinstal. Fitur upload XLS/XLSX tidak akan berfungsi.")
    pd = None


# --- App Configuration ---
st.set_page_config(
    page_title="🤖 Chatbot Assistant",
    page_icon="🐑",
    layout="centered",
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
st.caption("Masukkan Pesan yang Anda Inginkan, atau unggah dokumen untuk dibahas.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hai! Aku adalah Chatbot yang siap membantu kamu!"}
    ]
if "uploaded_file_content" not in st.session_state:
    st.session_state.uploaded_file_content = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# --- File Uploader ---
# Tambahkan tipe file yang didukung ke list
supported_file_types = ["txt", "md", "pdf"]
if DocxDocument:
    supported_file_types.extend(["docx", "doc"]) # doc mungkin perlu konversi atau library lain
if Presentation:
    supported_file_types.append("pptx")
if pd:
    supported_file_types.extend(["xlsx", "xls"])


uploaded_file = st.file_uploader(
    f"Unggah dokumen (opsional, .{', .'.join(supported_file_types)})",
    type=supported_file_types,
    help="Unggah file untuk dibahas dengan chatbot."
)

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
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
                file_processed_successfully = True
            except Exception as e:
                st.error(f"Gagal membaca file PDF: {e}")
        elif (file_extension == "docx" or file_extension == "doc") and DocxDocument:
            # Untuk .doc mungkin perlu pendekatan berbeda atau konversi, .docx lebih mudah
            if file_extension == "docx":
                try:
                    doc = DocxDocument(io.BytesIO(file_content_bytes))
                    for para in doc.paragraphs:
                        extracted_text += para.text + "\n"
                    # Anda juga bisa mencoba mengekstrak teks dari tabel jika perlu
                    for table in doc.tables:
                        for row in table.rows:
                            for cell in row.cells:
                                extracted_text += cell.text + "\t"
                            extracted_text += "\n"
                    file_processed_successfully = True
                except Exception as e:
                    st.error(f"Gagal membaca file DOCX: {e}")
            else: # .doc
                 st.warning("File .doc mungkin tidak didukung sepenuhnya. Coba konversi ke .docx.")
        elif file_extension == "pptx" and Presentation:
            try:
                prs = Presentation(io.BytesIO(file_content_bytes))
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text"):
                            extracted_text += shape.text + "\n"
                file_processed_successfully = True
            except Exception as e:
                st.error(f"Gagal membaca file PPTX: {e}")
        elif (file_extension == "xlsx" or file_extension == "xls") and pd:
            try:
                # Membaca semua sheet dan menggabungkan teksnya
                xls_file = pd.ExcelFile(io.BytesIO(file_content_bytes))
                for sheet_name in xls_file.sheet_names:
                    df = xls_file.parse(sheet_name)
                    # Ubah seluruh dataframe menjadi string, ini mungkin perlu penyesuaian
                    # tergantung bagaimana Anda ingin merepresentasikan data tabel.
                    extracted_text += f"--- Sheet: {sheet_name} ---\n"
                    extracted_text += df.to_string(index=False) + "\n\n"
                file_processed_successfully = True
            except Exception as e:
                st.error(f"Gagal membaca file Excel: {e}")
        else:
            st.warning(f"Tipe file '{file_extension}' tidak didukung atau library yang dibutuhkan tidak terinstal.")


        if file_processed_successfully and extracted_text.strip():
            st.session_state.uploaded_file_content = extracted_text
            user_upload_message = f"Saya telah mengunggah file: '{st.session_state.uploaded_file_name}'. Mohon gunakan konteks dari file ini untuk pertanyaan saya selanjutnya."
            assistant_ack_message = f"Baik, saya telah menerima file '{st.session_state.uploaded_file_name}'. Silakan ajukan pertanyaan Anda terkait dokumen ini."
            
            current_messages_tuple = tuple(m['content'] for m in st.session_state.messages)
            if user_upload_message not in current_messages_tuple and assistant_ack_message not in current_messages_tuple:
                st.session_state.messages.append({"role": "user", "content": user_upload_message})
                st.session_state.messages.append({"role": "assistant", "content": assistant_ack_message})
                # st.rerun() # Hati-hati dengan rerun, bisa menyebabkan re-upload jika state tidak dikelola baik
        elif file_processed_successfully and not extracted_text.strip():
            st.info(f"File '{st.session_state.uploaded_file_name}' berhasil diproses tetapi tidak ditemukan konten teks yang bisa diekstrak.")
            st.session_state.uploaded_file_content = None
        elif not file_processed_successfully and uploaded_file: # Jika proses gagal tapi file ada
             st.session_state.uploaded_file_content = None


    except Exception as e:
        st.error(f"Terjadi kesalahan umum saat memproses file '{uploaded_file.name}': {e}")
        st.session_state.uploaded_file_content = None

# (Sisa kode Anda: display messages, chat input, logic, sidebar, dll. tetap sama)
# Pastikan untuk menyesuaikan bagian display messages dan chat input logic
# jika Anda melakukan perubahan besar pada bagaimana pesan upload ditangani.

# Display existing messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input and Logic ---
user_prompt = st.chat_input("Ketik pesanmu untuk chatbot di sini...")

if user_prompt and client:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Membangun payload pesan untuk API
            # Pastikan menyertakan histori yang relevan dan mungkin konteks file jika diperlukan secara eksplisit
            payload_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

            # Jika ada konten file yang sangat besar dan ingin diprioritaskan,
            # Anda mungkin ingin menyisipkannya secara strategis, misal sebagai pesan sistem
            # atau bagian dari prompt pengguna terbaru, tergantung batas token dan strategi Anda.
            # Untuk saat ini, kita mengandalkan histori chat yang sudah mencakup pesan upload.

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
    st.markdown("""
    Bot ini menggunakan model AI dari OpenRouter untuk membantu kebutuhan Anda.
    Cukup ketik permintaanmu dan lihat hasilnya! 🐐🎉
    """)
    st.subheader("Model Digunakan:")
    st.markdown("Deepseek R1 (via OpenRouter)")

    st.markdown("---")
    if st.button("Mulai Percakapan Baru"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Hai! Silahkan ketik pesanmu di sini!"}
        ]
        st.session_state.uploaded_file_content = None
        st.session_state.uploaded_file_name = None
        # uploaded_file = None # Ini tidak akan mereset widget file_uploader secara langsung
        st.rerun()

    st.markdown("---")
    st.markdown("Dibuat oleh Mohammad Aris Darmawan")
