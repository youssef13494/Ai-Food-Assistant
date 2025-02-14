from dotenv import load_dotenv
load_dotenv()

import streamlit as st 
import os
from PIL import Image
import google.generativeai as genai
from crewai import Agent,Task,Crew,LLM
from googleapiclient.discovery import build
import json

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
if not os.environ["OPENAI_API_KEY"]:
    raise ValueError("⚠️ لم يتم تحميل مفتاح API بشكل صحيح! تحقق من ملف .env.")

os.environ["OPENAI_API_BASE"] = "https://api.sambanova.ai/v1"
os.environ["OPENAI_MODEL_NAME"] = "sambanova/Qwen2.5-72B-Instruct"

# SambaNova API
llm = LLM(
    model=os.environ["OPENAI_MODEL_NAME"],
    temperature=0.4,
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"],
    max_tokens=1000
)


# Function to get the response from Gemini
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to handle image upload and return image data
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
                                                            #####################################################
def create_agents():

    ingredients_extraction_agent = Agent(
        role="وكيل استخراج المكونات",
        goal="استخراج المكونات الأساسية للطبق من اسمه، ومقارنة المكونات بالمخزون المتواجد في {data} المتاح عند المستخدم.",
        backstory="أنت مسؤول عن تحليل اسم الطبق، استخراج قائمة المكونات الرئيسية، والتحقق من توفرها لدى المستخدم. إذا كانت بعض المكونات ناقصة، تقترح بدائل إن وجدت.",
        allow_delegation=False,
        verbose=True,
        llm=llm
)

    calories_calculator_agent = Agent(
        role="وكيل حساب السعرات",
        goal=" حساب السعرات الحرارية للطبق بناءً على مكوناته الذي يستخرجها الوكيل الثاني وبناءا علي طبق يكفي شخص واحد.",
        backstory="تحلل المكونات المستخرجة لحساب السعرات الحرارية لكل مكون ثم تحسب إجمالي السعرات للطبق.",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    cooking_instructions_agent = Agent(
        role="وكيل تعليمات الطهي",
        goal="توفير تعليمات الطهي خطوة بخطوة للطبق.",
        backstory="تقدم تعليمات مفصلة حول كيفية تحضير الطبق بناءً على مكوناته، مع نصائح لتحسين تجربة الطهي.",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

                                                                #####################################################
    extract_ingredients_task = Task(
        description="استخراج قائمة المكونات الأساسية من اسم {الطبق}.",
        expected_output="المكونات التي يمكن استخدامها المتواجدة في المخزون و المكونات الناقصة التي يحتاجها مع بدائل للمكونات الناقصة",
        agent=ingredients_extraction_agent,
        output_file="extract_ingredients.txt"
    )

    calculate_calories_task = Task(
        description="حساب السعرات الحرارية ل {الطبق} بناءً على المكونات المستخرجة.",
        expected_output="إجمالي السعرات الحرارية للطبق مع تفاصيل لكل مكون.",
        agent=calories_calculator_agent,
        output_file="calculate_calories.txt"
    )

    cooking_instructions_task = Task(
        description="توفير تعليمات طهي خطوة بخطوة ل {الطبق} مع نصائح لتحسين الطهي.",
        expected_output="تعليمات طهي للطبق.",
        agent=cooking_instructions_agent,
        output_file="cooking_instructions.txt"
    )

    crew = Crew(
        agents=[ingredients_extraction_agent, calories_calculator_agent, cooking_instructions_agent],
        tasks=[extract_ingredients_task, calculate_calories_task, cooking_instructions_task]
    )

    return crew

                                                        #######################################################


# Function to get YouTube video link for a cooking recipe
def get_youtube_video_link(dish_name):

    youtube = build("youtube", "v3", developerKey=os.environ["YOUTUBE_API_KEY"])
    request = youtube.search().list(
        q=f"طريقة عمل {dish_name}",
        part="snippet",
        type="video",
        maxResults=1,
        order="relevance"
    )
    
    response = request.execute()
    
    # Extract video URL
    if response['items']:
        video_url = f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
        return video_url
    else:
        return "لم يتم العثور على فيديو."
    

                                                     ###########################################################
def main():
    st.set_page_config(page_title="الطباخ الذكي", page_icon="🍲")
    st.header("الطباخ الذكي")
    st.markdown("### 📸 حمّل صورة الطبق")  
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")  

    dish_name_input = st.text_input("أو أدخل اسم الطبق مباشرة:", key="dish_name_input")


    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image", use_container_width=True)

  
    col1, col2, col3, col4 = st.columns(4)

    submit1 = col1.button("اسم الطبق")
    submit4 = col2.button("المكونات")
    submit2 = col3.button("حساب السعرات الحرارية")
    submit3 = col4.button("عرض طريقة التحضير")


    if submit1:
        if uploaded_file is not None:
            image_content = input_image_setup(uploaded_file)
            response = get_gemini_response("استخرج اسم الطبق فقط من الصورة.", image_content,dish_name_input)
            dish_name = response
        elif dish_name_input.strip():
            dish_name = dish_name_input.strip()
        else:
            st.warning("يرجى رفع صورة أو إدخال اسم الطبق.")
            return

        st.session_state["dish_name"] = dish_name
        st.subheader("اسم الطبق:")
        st.write(dish_name)

    if "dish_name" in st.session_state:
        dish_name = st.session_state["dish_name"]
        inputs = {"الطبق": dish_name,"data":data}
        crew = create_agents()
        crew.kickoff(inputs=inputs) 

        if submit4: 
            with open("extract_ingredients.txt", "r", encoding="utf-8") as file:
                ingredients = file.read()
            st.write("✅ **المكونات**")
            st.write(ingredients)

        if submit2:
            with open("calculate_calories.txt", "r", encoding="utf-8") as file:
                calories = file.read()
            st.write("✅ **السعرات الحرارية**")
            st.write(calories)

        if submit3:
            with open("cooking_instructions.txt", "r", encoding="utf-8") as file:
                instructions = file.read()
            st.write("✅ **طريقة التحضير*")
            st.write(instructions)

            video_link = get_youtube_video_link(dish_name)
            st.subheader("فيديو طريقة التحضير:")
            st.video(video_link)


if __name__ == "__main__":
    main()


