import os
import json
from crewai import Agent, Crew, Task, LLM
from dotenv import load_dotenv
from Rag import run_rag  # ✅ استيراد أداة RAG

# ✅ تحميل متغيرات البيئة
load_dotenv()

# ✅ تعيين مفتاح API لـ Gemini
# ✅ ضبط مفتاح API الصحيح لـ Google Gemini
os.environ["GOOGLE_API_KEY"] = "AIzaSyClLpm4UDEj8aivUHMC55_fn_NrTwCSo7g"  # ✅ تأكد من أنه صحيح
os.environ["OPENAI_API_KEY"] = "2245e4b2-354f-4b40-b323-72cb59e42354"
os.environ["OPENAI_API_BASE"] = "https://api.sambanova.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "sambanova/Meta-Llama-3.3-70B-Instruct"

# ✅ تعريف نموذج الذكاء الاصطناعي باستخدام Google Gemini
llm = LLM(
    model=os.environ["OPENAI_MODEL_NAME"],
    temperature=0.4,
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"]
)

# ✅ تحميل بيانات JSON (للمخزون، إذا كنت تريد استخدامه مستقبلاً)
def load_text_file(file_path="data.json"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)  # ✅ قراءة JSON
            return json.dumps(json_data, indent=4, ensure_ascii=False)  # ✅ تحويل JSON إلى نص منسق
    except FileNotFoundError:
        return "⚠️ لا توجد بيانات متاحة."
    except json.JSONDecodeError:
        return "⚠️ خطأ في تحميل البيانات."

# ✅ تعريف الوكيل (Agent) المسؤول عن المعلومات الغذائية باستخدام RAG
def create_food_info_agent():
    return Agent(
        role="Food Expert",
        goal="تقديم معلومات غذائية دقيقة بناءً على المعلومات المتاحة فقط في المستندات.",
        backstory="مختص في علوم الأغذية والتغذية، يساعد في تقديم نصائح صحية باستخدام المعلومات المستخرجة من الوثائق.",
        verbose=True,
        memory=True,
        tools=[run_rag]
    )

# ✅ إنشاء المهمة (Task) بحيث تمرر `query` إلى `run_rag()`
def create_food_info_task(agent):
    return Task(
        description=(
            "🍽️ أنت مساعد غذائي ذكي، مهمتك الإجابة على الأسئلة المتعلقة بالغذاء والتغذية بناءً على المعلومات المتاحة في الوثائق فقط."
            " لا تحاول تقديم إجابات خارج نطاق المعلومات المتوفرة لديك."
            " ابحث في الوثائق واستخرج فقط الأجزاء ذات الصلة للإجابة على السؤال التالي:\n\n"
            "❓ **السؤال:** {query}\n\n"  # ✅ `query` سيتم تمريره كمدخل ديناميكي
            "📄 تأكد من أن إجابتك تستند فقط إلى المحتوى المستخرج باستخدام RAG."
        ),
        expected_output="إجابة دقيقة تعتمد على المعلومات المستخرجة من المستندات باستخدام RAG.",
        agent=agent,
        tools=[run_rag],  # ✅ تأكيد استخدام أداة RAG داخل المهمة
        inputs=["query"],  # ✅ التأكد من تمرير `query`
    )

# ✅ إنشاء الـ Crew وتشغيله
def kickoff(prompt):
    food_info_agent = create_food_info_agent()
    food_info_task = create_food_info_task(food_info_agent)  # ✅ يمرر `agent` فقط

    pantry_crew = Crew(
        agents=[food_info_agent],
        tasks=[food_info_task],
        goal="الإجابة على الأسئلة الغذائية باستخدام المعلومات المسترجعة من المستندات فقط."
    )

    return pantry_crew.kickoff(inputs={"query": prompt})  # ✅ تمرير `query` بشكل صحيح

# ✅ وظيفة التعامل مع الاستعلامات
def handle_chat(user_query):
    response = kickoff(user_query)  # ✅ إرسال السؤال إلى CrewAI
    return response

# ✅ تجربة الاستعلام مع البيانات النصية
if __name__ == "__main__":
    user_prompt = input("📝 أدخل استفسارك: ")
    response = kickoff(user_prompt)  # ✅ تشغيل الـ CrewAI والـ RAG Tool
    print(response)
