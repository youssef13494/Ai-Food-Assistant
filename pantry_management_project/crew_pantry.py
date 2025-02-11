import os
import json
from crewai import Agent, Crew, Task, LLM
from dotenv import load_dotenv
from tools import run_rag, load_json_file  # ✅ أدوات تحميل البيانات من الكتب والمخزن

# ✅ تحميل متغيرات البيئة
load_dotenv()

# 🔹 Set API Keys
os.environ["OPENAI_API_KEY"] = "66e99044-a4d8-4a6c-aacd-68f0546ccbca"
os.environ["OPENAI_API_BASE"] = "https://api.sambanova.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "sambanova/Meta-Llama-3.3-70B-Instruct"


llm = LLM(
    model=os.environ["OPENAI_MODEL_NAME"],
    temperature=0.4,
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"]
)

### ✅ إنشاء الوكلاء (Agents)

# 🔹 وكيل 1: جلب المعلومات الغذائية من الكتب 📖
def create_food_info_agent():
    return Agent(
        role="Food Expert",
        goal="استخراج المعلومات الغذائية والسعرات الحرارية من الكتب باستخدام RAG.",
        backstory="خبير تغذية متخصص في تحليل البيانات الغذائية من الكتب والمصادر العلمية باستخدام الذكاء الاصطناعي.",
        verbose=True,
        memory=True,
        tools=[run_rag]
    )

# 🔹 وكيل 2: إعداد النظام الغذائي بناءً على المخزون والسعرات الحرارية 🛒
def create_meal_planner_agent():
    return Agent(
        role="Diet Planner",
        goal="إنشاء نظام غذائي صحي بناءً على السعرات الحرارية المطلوبة والمكونات المتاحة في المخزن.",
        backstory="أخصائي تغذية يساعد المستخدمين على تحقيق أهدافهم الصحية من خلال تقديم وجبات متوازنة تعتمد على السعرات الحرارية والمكونات المتاحة.",
        verbose=True,
        memory=True,
        tools=[run_rag, load_json_file]
    )

# 🔹 وكيل 3: إدارة المخزن والإجابة عن الأسئلة 📦
def create_inventory_manager_agent():
    return Agent(
        role="Inventory Manager",
        goal="إدارة المخزن، والإجابة على الأسئلة حول المكونات المتاحة واقتراح البدائل.",
        backstory="مسؤول عن إدارة المخزن ومراقبة المكونات المتوفرة، ويقوم بتنسيق بيانات المخزن لتكون واضحة وسهلة القراءة.",
        verbose=True,
        memory=True,
        tools=[load_json_file]
    )

### ✅ إنشاء المهام (Tasks)

# 🔹 مهمة 1: البحث عن المعلومات الغذائية من الكتب 📖
def create_food_info_task(agent):
    return Task(
        description="🍽️ استخراج معلومات غذائية دقيقة بناءً على الكتب المتاحة، مع حساب السعرات الحرارية المطلوبة.",
        expected_output="معلومات غذائية دقيقة تعتمد على البيانات المستخرجة من الكتب.",
        agent=agent,
        tools=[run_rag],
        inputs=["query"]
    )

# 🔹 مهمة 2: إعداد خطة وجبات متوازنة بناءً على المخزون والسعرات الحرارية 🛒
def create_meal_planning_task(agent, food_info_agent):
    return Task(
        description=(
            "🍽️ قم بحساب السعرات الحرارية المطلوبة بناءً على عمر ووزن المستخدم ومستوى نشاطه."
            " ثم استخدم هذه المعلومات لإنشاء نظام غذائي يومي يحتوي على وجبات متوازنة."
            " تأكد من أن الوجبات تعتمد على المكونات المتاحة في المخزن قدر الإمكان."
            " لا تقم باستدعاء أي وكيل إضافي بعد ذلك، قم فقط بإرجاع تقرير منسق مباشرة كـ Markdown."
            "\n\n"
            "📊 **تنسيق الإخراج المطلوب:**\n"
            "- إجمالي السعرات الحرارية اليومية في البداية.\n"
            "- جدول يحتوي على الوجبات الرئيسية **(الإفطار، الغداء، العشاء، وجبات خفيفة)**.\n"
            "- عدد السعرات الحرارية لكل وجبة.\n"
            "- المكونات المستخدمة في كل وجبة.\n"
            "- قائمة بالمكونات الناقصة، إن وجدت.\n"
            "- استخدم **Markdown** لعرض المعلومات بطريقة واضحة."
        ),
        expected_output="📊 تقرير النظام الغذائي النهائي كـ Markdown، دون الحاجة إلى استدعاء `Output Formatter`.",
        agent=agent,
        tools=[run_rag, load_json_file],  # ✅ تحميل المعلومات والمخزون مرة واحدة فقط
        inputs=["query"],
        depends_on=[food_info_agent]  # ✅ يعتمد فقط على بيانات `Food Info Agent`
    )

# 🔹 مهمة 3: إدارة المخزن وعرض تقريره 📦
def create_inventory_task(agent):
    return Task(
        description="📦 أجب على الأسئلة المتعلقة بالمخزن والمكونات المتاحة، وقم بعرض البيانات على شكل **جدول Markdown منسق**.",
        expected_output="📊 تقرير المخزن كجدول Markdown يعرض الكميات والمكونات الناقصة.",
        agent=agent,
        tools=[load_json_file],  # ✅ استدعاء بيانات المخزن
        inputs=["query"]
    )



def detect_task_type(prompt):
    food_keywords = ["سعرات", "وجبة", "نظام غذائي", "طعام", "غذاء", "حمية"]
    inventory_keywords = ["مخزن", "مكونات", "المتاح", "المنتجات", "المخزون"]

    prompt_lower = prompt.lower()

    if any(keyword in prompt_lower for keyword in food_keywords):
        return "food"
    elif any(keyword in prompt_lower for keyword in inventory_keywords):
        return "inventory"
    else:
        return "all"


### ✅ تشغيل CrewAI

def kickoff(prompt):
    task_type = detect_task_type(prompt)

    # ✅ إنشاء الوكلاء الأساسيين فقط
    food_info_agent = create_food_info_agent()
    meal_planner_agent = create_meal_planner_agent()
    inventory_manager_agent = create_inventory_manager_agent()

    # ✅ إنشاء المهام
    food_info_task = create_food_info_task(food_info_agent)
    meal_planning_task = create_meal_planning_task(meal_planner_agent, food_info_agent)
    inventory_task = create_inventory_task(inventory_manager_agent)

    # ✅ اختيار المهام بناءً على النوع المكتشف تلقائيًا
    if task_type == "food":
        tasks = [food_info_task, meal_planning_task]  # ✅ النظام الغذائي فقط
    elif task_type == "inventory":
        tasks = [inventory_task]  # ✅ تقرير المخزن فقط
    else:
        tasks = [food_info_task, meal_planning_task, inventory_task]  # ✅ تشغيل الكل لو مش واضح

    # ✅ تشغيل CrewAI بطريقة مبسطة
    pantry_crew = Crew(
        agents=[food_info_agent, meal_planner_agent, inventory_manager_agent],
        tasks=tasks,
        goal="تقديم نظام غذائي صحي بناءً على السعرات الحرارية المطلوبة وإدارة المخزون بفعالية."
    )

    return pantry_crew.kickoff(inputs={"query": prompt})

