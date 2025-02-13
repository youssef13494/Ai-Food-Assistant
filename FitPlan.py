import streamlit as st 
import os
import google.generativeai as genai
from crewai import Agent,Task,Crew,LLM
from crewai_tools import PDFSearchTool
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://api.sambanova.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "sambanova/Qwen2.5-72B-Instruct"

# تهيئة LLM باستخدام SambaNova API
llm = LLM(
    model=os.environ["OPENAI_MODEL_NAME"],
    temperature=0.4,
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"],
    max_tokens=1000
)

def calculate_calories(fat, weight, activity_factor, goal):
    lean_mass = (1 - fat / 100) * weight
    bmr = lean_mass * 21.6 + 370
    total_calories = bmr * activity_factor
    
    # تعديل السعرات بناءً على الهدف
    if goal == "التنشيف (Fat Loss)":
        total_calories -= 500
    elif goal == "التضخيم (Muscle Gain)":
        total_calories += 500
    
    return int(total_calories)

# pdf_tool = PDFSearchTool(file_path="tool.pdf")

diet_planner_agent = Agent(
    role="خبير تغذية",
    goal="{calories_needed}إنشاء نظام غذائي متوازن بناءً على السعرات الحرارية المطلوبة.",
    backstory="خبير تغذية ذكي يقوم بحساب وتقسيم السعرات الحرارية إلى وجبات مناسبة.",
    llm=llm
)
gym_trainer = Agent(
    role="مدرب رياضي",
    goal="تصميم برنامج تدريبي بناءً على {goal} المستخدم ومستواه في الجيم {gym_level}",
    backstory="مدرب محترف يساعد المستخدمين في تحقيق أهدافهم من خلال برامج تدريب فعالة.",
    llm=llm,
    # tools=[pdf_tool]
)

diet_plan_task = Task(
        description="""قم بإنشاء نظام غذائي يومي يحتوي على {calories_needed} سعرة حرارية.
        - يجب أن يحتوي على 3 وجبات رئيسية ووجبتين خفيفتين.
        - توزيع السعرات:
          * 40% كربوهيدرات 🍞
          * 40% بروتين 🍗
          * 20% دهون 🥑
        - يجب أن تكون الوجبات متوازنة ومغذية    .
        """,
        expected_output="نظام غذائي يومي متكامل.",
        agent=diet_planner_agent,
        output_file="diet_plan.txt"
    )

training_plan_task = Task(
    description="قم بإنشاء برنامج تدريبي بناءً على هدف المستخدم {goal} ومستواه في الجيم {gym_level}.",
    expected_output="برنامج تدريبي مفصل بناءً على الهدف ومستوى في الجيم.",
    agent=gym_trainer,
    output_file="training_plan.txt"
    # tools=[pdf_tool]
)
# إنشاء Crew يحتوي على الـ Agent
crew = Crew(agents=[diet_planner_agent,gym_trainer], tasks=[diet_plan_task,training_plan_task])

st.title("🔥 حساب السعرات الحرارية اليومية")

# إدخال نسبة الدهون والوزن
fat = st.number_input("أدخل نسبة الدهون في جسمك (%)", min_value=0.0, max_value=100.0, value=15.0, step=0.1)
weight = st.number_input("أدخل وزنك بالكيلوغرام (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)

# اختيار مستوى النشاط
activity_levels = {
    "قليل جدًا (بدون تمارين)": 1.2,
    "تمارين خفيفة (1-3 أيام في الأسبوع)": 1.375,
    "تمارين متوسطة (3-5 أيام في الأسبوع)": 1.55,
    "تمارين مكثفة (6-7 أيام في الأسبوع)": 1.725,
    "تمارين مكثفة جدًا (مرتين يوميًا)": 1.9
}

activity_choice = st.selectbox("اختر مستوى نشاطك:", list(activity_levels.keys()))
activity_factor = activity_levels[activity_choice]

# اختيار الهدف (تضخيم / تنشيف / ثبات الوزن)
goal_options = ["التنشيف (Fat Loss)", "الثبات (Maintenance)", "التضخيم (Muscle Gain)"]
goal = st.selectbox("🎯 اختر هدفك:", goal_options)

gym_levels = ["مبتدئ (Beginner)", "متوسط (Intermediate)", "متقدم (Advanced)"]
gym_level = st.radio("🏋️‍♂️ اختر مستواك في الجيم:", gym_levels)

# حساب السعرات وعرض النتيجة
calories_needed = calculate_calories(fat, weight, activity_factor, goal)

if st.button("🔍 احسب السعرات الحرارية"):
    st.success(f"🔥 تحتاج إلى {calories_needed} سعرة حرارية يوميًا لتحقيق هدفك ({goal}).")

if st.button("🍽️ احصل على نظامك غذائي المناسب"):
    diet_plan=crew.kickoff(inputs={'calories_needed': calories_needed,'goal':goal, 'gym_level':gym_level})
    with open("diet_plan.txt", "r", encoding="utf-8") as file:
            diet_content = file.read()
    st.write("✅ **نظامك الغذائي:**")
    st.write(diet_content)

if st.button("🍽️ احصل على نظامك التدريبي المناسب"):
    with open("training_plan.txt", "r", encoding="utf-8") as file:
            training_content = file.read()
    st.write("💪 **نظامك التدريبي:**")
    st.write(training_content)
