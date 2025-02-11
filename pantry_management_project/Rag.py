from crewai.tools import tool
from crewai_tools import PDFSearchTool
import google.generativeai as genai
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

path=r'books\\Book1.pdf'

token = "AIzaSyDpcS2ySvzyHoGdK1zfJ3rYynWIBTrNAtY"

genai.configure(api_key=token)
model = genai.GenerativeModel("gemini-1.5-flash")


# Load an Arabic-compatible embedding model
model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
model_kwargs = {"device": "cuda"}  # Use CUDA if available

embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs)

def encode_pdf(path, chunk_size=2000, chunk_overlap=200):
    # Load PDF documents
    loader = PyPDFLoader(path)
    documents = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    chunks = text_splitter.split_documents(documents)

    texts = [chunk.page_content.encode("utf-8", "ignore").decode() for chunk in chunks]

    # Create vector store using FAISS
    vectorstore = FAISS.from_texts(texts, embeddings)

    return vectorstore

chunks_vector_store = encode_pdf(path, chunk_size=2000, chunk_overlap=200)
chunks_query_retriever = chunks_vector_store.as_retriever(search_kwargs={"k": 5})


def prompt_template(context,age=22, weight=65, meal="العشاء"):
    prompt = f"""
    أنت مساعد غذائي ذكي، مهمتك تقديم نظام غذائي صحي بناءً على عمر المستخدم، وزنه، والوجبة التي يريدها.
    استخدم المعلومات التالية كمرجع لإنشاء اقتراح صحي للوجبة المختارة.

    ✅ العمر: {age} سنة
    ✅ الوزن: {weight} كجم
    ✅ الوجبة المطلوبة: {meal}

    🔹 ضع في اعتبارك توازن العناصر الغذائية، وقدم اقتراحًا يحتوي على البروتين، الكربوهيدرات، والدهون الصحية.
    🔹 إذا كانت الوجبة غير مناسبة لصحة المستخدم، اقترح بديلاً صحيًا مشابهًا.
    🔹 اجعل الإجابة واضحة وموجزة في **ثلاث جمل** فقط.

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
    - (str): إجابة تحتوي على توصية غذائية مبنية على المعلومات المسترجعة من المستندات.
    """
  results = chunks_query_retriever.get_relevant_documents(prompet)
  nutrition_info = results
  response = model.generate_content(prompt_template(nutrition_info))
  return response.text




