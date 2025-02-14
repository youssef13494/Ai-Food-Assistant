import os
from crewai.tools import tool
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


# ✅ متغيرات Global لتخزين بيانات المستخدم
USER_AGE = None
USER_WEIGHT = None
USER_HEIGHT = None
USER_STATUS = None

def update_user_info(age, weight, height, status):
    """تحديث بيانات المستخدم عند اختيارها من واجهة المستخدم."""
    global USER_AGE, USER_WEIGHT, USER_HEIGHT, USER_STATUS
    USER_AGE = age
    USER_WEIGHT = weight
    USER_HEIGHT = height
    USER_STATUS = status
    print(f"✅ تم تحديث بيانات المستخدم: العمر={USER_AGE}, الوزن={USER_WEIGHT}, الطول={USER_HEIGHT}, الحالة الصحية={USER_STATUS}")


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
chunks_query_retriever = chunks_vector_store.as_retriever(search_kwargs={"k": 7})


@tool
def run_rag(prompt: str) -> str:
    """🔍 يسترجع المعلومات الغذائية بناءً على بيانات المستخدم المخزنة كـ `Global Variables`."""
    global USER_AGE, USER_WEIGHT, USER_HEIGHT, USER_STATUS

    # ✅ التأكد من أن القيم غير فارغة قبل تشغيل النموذج
    if None in (USER_AGE, USER_WEIGHT, USER_HEIGHT, USER_STATUS):
        return "⚠️ يرجى تحديد بيانات المستخدم (العمر، الوزن، الطول، الحالة الصحية) قبل الاستفسار."

    print(f"📥 Received in run_rag: prompt={prompt}, age={USER_AGE}, weight={USER_WEIGHT}, height={USER_HEIGHT}, status={USER_STATUS}")  

    results = chunks_query_retriever.get_relevant_documents(prompt)

    formatted_prompt = f""" 
    أنت مساعد غذائي ذكي، مهمتك تقديم نظام غذائي صحي موضح فيه السعرات الحرارية المناسبة للمستخدم بناءً على البيانات الشخصية التالية:
    
    🧑 العمر: {USER_AGE} سنة  
    ⚖️ الوزن: {USER_WEIGHT} كجم  
    📏 الطول: {USER_HEIGHT} سم 
    🏥 الحالة الصحية: {USER_STATUS} 
            
    🔹 ضع في اعتبارك توازن العناصر الغذائية، وقدم اقتراحًا يحتوي على البروتين، الكربوهيدرات، والدهون الصحية.  
    🔹 إذا كانت الوجبة غير مناسبة لصحة المستخدم، اقترح بديلاً صحيًا مشابهًا.  
    🔹 اجعل الإجابة واضحة وموجزة في **خمس جمل** فقط.  

    📝 معلومات مرجعية:  
    {results}

    🍽️ اقتراح وجبة صحية:
    """
    response = model.generate_content(formatted_prompt)
    return response.text

@tool
def run_general_nutrition_query(prompt: str) -> str:
    """🔍 يسترجع معلومات غذائية عامة حول الأطعمة والتغذية بناءً على استفسارات المستخدم."""
    
    print(f"📥 Received in run_general_nutrition_query: prompt={prompt}")  

    # 🔹 استرجاع البيانات ذات الصلة من نظام البحث
    results = chunks_query_retriever.get_relevant_documents(prompt)

    # 🔹 صياغة استعلام الذكاء الاصطناعي لإنتاج إجابة مفيدة
    formatted_prompt = f""" 
    أنت خبير تغذية ذكي، مهمتك هي الإجابة عن الأسئلة العامة حول الأطعمة والتغذية.
    
    ✅ استفسار المستخدم: **{prompt}**  
    ✅ قدم إجابة دقيقة ومختصرة مدعومة بمعلومات علمية.
    ✅ اجعل الإجابة في **خمس جمل فقط** دون تقديم توصيات طبية.

    📝 معلومات مرجعية:  
    {results}

    📢 **إجابة مختصرة:**  
    """
    
    response = model.generate_content(formatted_prompt)
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

