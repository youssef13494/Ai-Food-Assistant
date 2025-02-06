import os
import streamlit as st
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Set up API keys
os.environ["GEMINI_API_KEY"] = "AIzaSyBeUOLiWjMI-lzYrpxmG8IKyn9nKQyrlfg"
os.environ["SERPER_API_KEY"] = "4a57770b81c885e1be49f0027894c99ff4ce710f"

# ✅ Set up the LLM model
llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GEMINI_API_KEY"]
)

# ✅ Initialize search and scrape tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# ✅ Define the recommendation agent
recommendation_agent = Agent(
    role="وكيل التوصيات",
    goal="البحث عن أفضل المطاعم في Talabat بناءً على الموقع واسم الطبق، ثم اقتراح الأفضل من حيث السعر والتقييم.",
    backstory="تحلل الطبق المدخل والموقع، ثم تبحث عن المطاعم باستخدام Google Search ثم تستخرج تفاصيل الأسعار والتقييمات.",
    allow_delegation=False,
    verbose=True,
    llm=llm,
    tools=[search_tool, scrape_tool]
)

# ✅ Define the recommendation task
recommend_dish_task = Task(
    description=(
        "١. استخدم SerperDevTool للبحث عن {الطبق} في Talabat داخل {الموقع} عبر Google.\n"
        "٢. استخدم ScrapeWebsiteTool لاستخراج قائمة المطاعم التي تقدم الطبق مع الأسعار والتقييمات.\n"
        "٣. قم بترتيب المطاعم وفقًا لأفضل سعر وأعلى تقييم، ثم قدم أفضل ٣ توصيات."
    ),
    expected_output="قائمة بأفضل المطاعم التي تقدم {الطبق} في {الموقع}، مرتبة حسب السعر والتقييم.",
    agent=recommendation_agent,
    tools=[search_tool, scrape_tool]
)

# ✅ Function to create CrewAI agents and tasks
def create_agents(dish_name, location):
    crew = Crew(
        agents=[recommendation_agent],
        tasks=[recommend_dish_task]
    )
    return crew

# ✅ Streamlit UI
def main():
    st.set_page_config(page_title="Talabat Food Finder", page_icon="🍽️")
    st.header("🍕 Find the Best Restaurants on Talabat")

    # ✅ Step 1: Ask user to open Talabat manually
    st.subheader("1️⃣ افتح موقع طلبات واختَر موقعك")
    st.write("👉 **[اضغط هنا لفتح طلبات](https://www.talabat.com/ar/egypt)**")
    
    # ✅ Step 2: User enters the Talabat restaurant page URL manually
    talabat_url = st.text_input("📌 انسخ رابط صفحة المطاعم هنا:", placeholder="مثال: https://www.talabat.com/ar/egypt/restaurants")

    # ✅ Step 3: User inputs dish name
    st.subheader("2️⃣ أدخل اسم الطبق للبحث عن أفضل المطاعم")
    dish_name = st.text_input("🍔 Enter Dish Name:", placeholder="e.g., Shawarma, Pizza, Sushi")

    # ✅ Step 4: Start CrewAI if valid URL and dish name are provided
    if "restaurants" in talabat_url and dish_name:
        st.subheader(f"📌 Searching for {dish_name} in Selected Location...")

        crew = create_agents(dish_name, "Selected Location")  # Replace with detected location
        inputs = {"الطبق": dish_name, "الموقع": "Selected Location"}
        result = crew.kickoff(inputs=inputs)

        st.subheader("✅ Best Restaurant Recommendations:")
        st.write(result)

if __name__ == "__main__":
    main()
