import os
from crewai.tools import tool
from crewai_tools import PDFSearchTool
import google.generativeai as genai
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
import json

token = "AIzaSyDpcS2ySvzyHoGdK1zfJ3rYynWIBTrNAtY"

genai.configure(api_key=token)
model = genai.GenerativeModel("gemini-1.5-flash")


# Load an Arabic-compatible embedding model
model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
model_kwargs = {"device": "cuda"}  # Use CUDA if available

embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

def encode_pdfs(paths, chunk_size=2000, chunk_overlap=200):
    """
    Load and encode multiple PDF files into a single FAISS vector store.
    
    :param paths: List of PDF file paths.
    :param chunk_size: Size of text chunks.
    :param chunk_overlap: Overlapping size between chunks.
    :return: FAISS vector store containing indexed document embeddings.
    """
    all_texts = []
    
    for path in paths:
        # Load the PDF
        loader = PyPDFLoader(path)
        documents = loader.load()
        
        # Split the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        # Extract text content
        texts = [chunk.page_content.encode("utf-8", "ignore").decode() for chunk in chunks]
        all_texts.extend(texts)  # Collect all texts from different books

    # Create a single FAISS vector store from all documents
    vectorstore = FAISS.from_texts(all_texts, embeddings)
    
    return vectorstore

# Paths of the three books
pdf_paths = [r'books\\Book1.pdf', r'books\\Book2.pdf']

# Encode all books into a single vector store
chunks_vector_store = encode_pdfs(pdf_paths, chunk_size=2000, chunk_overlap=200)

# Create a retriever from the combined vector store
chunks_query_retriever = chunks_vector_store.as_retriever(search_kwargs={"k": 5})

def prompt_template(context: str) -> str:
    prompt = f""" 
    أنت مساعد غذائي ذكي، مهمتك تقديم نظام غذائي صحي موضح فيه السعرات الحراريةالمناسبة للمستخدم بناءً على عمر المستخدم، وزنه، ومن الممكن ان يكون له تاريخ مرضي في البداية اطلب منه هذه المعلومات حتي تقدم نتائج فعالة.
    اذا رفض اعطاء الملعومات الشخصية يمكنك ان تقدم نصائح عامة للتغذية الصحية.
    وذا اعطاك المعلومات الشخصية يمكنك ان تقدم نصائح تغذية مخصصة له.
    🔹 ضع في اعتبارك توازن العناصر الغذائية، وقدم اقتراحًا يحتوي على البروتين، الكربوهيدرات، والدهون الصحية.
    🔹 إذا كانت الوجبة غير مناسبة لصحة المستخدم، اقترح بديلاً صحيًا مشابهًا.
    🔹 اجعل الإجابة واضحة وموجزة في **خمس جمل** فقط.

    📝 معلومات مرجعية:
    {context}

    🍽️ اقتراح وجبة صحية:
    """
    return prompt

@tool
def run_rag(prompet: str)->str:
  """🔍 يسترجع المعلومات من PDF ويستخدم Gemini 1.5 للإجابة على استفسارات المستخدم.

    ✅ يتم البحث في المستندات باستخدام `FAISS` لاسترجاع المعلومات الغذائية المرتبطة بالسؤال،
    ثم يتم تمرير البيانات إلى `Gemini 1.5` لإنشاء إجابة مخصصة.

    🔹 **المعطيات**:
    - `query` (str): استفسار المستخدم.

    🔹 **المخرجات**:
    - (str): إجابة تحتوي على نظام غذائي او توصية غذائية مبنية على المعلومات المسترجعة من المستندات.
    """
  results = chunks_query_retriever.get_relevant_documents(prompet)
  response = model.generate_content(prompt_template(results))
  return response.text


@tool 
def load_json_file(file_path="data.json"):
    """
    يقوم بتحميل بيانات من ملف JSON وإرجاعها كسلسلة نصية منسقة.
    
    :param file_path: مسار ملف JSON.
    :return: محتوى JSON كسلسلة نصية.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)  # ✅ قراءة JSON
            return json.dumps(json_data, indent=4, ensure_ascii=False)  # ✅ تحويل JSON إلى نص منسق
    except FileNotFoundError:
        return "⚠️ الملف غير موجود."
    except json.JSONDecodeError:
        return "⚠️ خطأ في تحميل بيانات JSON."

