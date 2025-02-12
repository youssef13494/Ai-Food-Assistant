from dotenv import load_dotenv
load_dotenv()

import streamlit as st 
import os
from PIL import Image
import google.generativeai as genai
from crewai import Agent,Task,Crew,LLM
from googleapiclient.discovery import build
from crewai_tools import ScrapeWebsiteTool
from IPython.display import Markdown
                         
# from crewai_tools import FileReadTool
# from pathlib import Path
# from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource


# json_source = JSONKnowledgeSource(#
#    file_paths=[Path("D:/NTI_FINAL_PROJECT/Omar/data.json")]
# )

# json_source = JSONKnowledgeSource(
#     file_paths=[Path("D:/NTI_FINAL_PROJECT/Omar/data.json").resolve()]  # Ensure absolute path
# )
# json_knowledge_sources = [json_source] if isinstance(json_source, JSONKnowledgeSource) else []
#docs_scrape_tool = ScrapeWebsiteTool(
#website_url="C:/Users/Hagar/AppData/Local/Temp/aca67d69-fada-4673-84df-6e34a688bee6_دليل_السعرات_الحراريه_للطعام.zip.ee6/3738.htm")


import json

# Specify the file path and encoding
file_path = "data.json"
encoding_type = "utf-8"  # Change this if needed (e.g., "utf-16", "latin-1")

# Read JSON file
with open(file_path, "r", encoding=encoding_type) as file:
    data = json.load(file)  # Load JSON content into a Python dictionary


# Set up the API key for Gemini
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")
os.environ["YOUTUBE_API_KEY"] = os.getenv("YOUTUBE_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.environ["GEMINI_API_KEY"]
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
def create_first_crew():
    # وكيل استخراج المكونات من اسم الطبق
      ingredients_extraction_agent = Agent(
        role="وكيل استخراج المكونات",
        goal="استخراج المكونات الأساسية للطبق من اسمه، ومقارنة المكونات بالمخزون باللغة العربية{data} المتاح عند المستخدم.",
        backstory="أنت مسؤول عن تحليل اسم الطبق، استخراج قائمة المكونات الرئيسيةو كمياتهاعلى حسب اسم الطبق وعدد الأشخاص{people}{الطبق}، والتحقق من توفرها لدى المستخدم من {data}. إذا كانت بعض المكونات ناقصة، وعرض بدائب ببمكونات الغير موجودة.",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    # وكيل تعليمات الطهي للطبق
      cooking_instructions_agent = Agent(
        role="وكيل تعليمات الطهي",
        goal="توفير تعليمات الطهي خطوة بخطوة للطبق.",
        backstory="تقدم تعليمات مفصلة حول كيفية تحضير الطبق بناءً على مكوناته، مع نصائح لتحسين تجربة الطهي.",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    # مهام
      extract_ingredients_task = Task(
        description="استخراج قائمة المكونات الأساسية من اسم {الطبق}.",
        expected_output="عرض قائمة بالمكونات المستخدمة في الطبق وكمياتها باللغة العربية وعرض قائمة بالمكونات الغير موجودة",
        agent=ingredients_extraction_agent
    )

      cooking_instructions_task = Task(
        description="توفير تعليمات طهي خطوة بخطوة ل {الطبق} مع نصائح لتحسين الطهي.",
        expected_output="تعليمات طهي مفصلة للطبق باللغة العربية.",
        agent=cooking_instructions_agent
    )

    # تكوين فريق العمل
      crew = Crew(
        agents=[ingredients_extraction_agent, cooking_instructions_agent],
        tasks=[extract_ingredients_task, cooking_instructions_task]
    )
      return crew
  
# #def create_second_crew():
#         # وكيل حساب السعرات الحرارية بناءً على المكونات
#     recipe_recommendation_agent = Agent(
#         role="وكيل توصيات الوصفات",
#         goal="اقتراح وصفة تلبي عدد السعرات الحرارية التي يرغب بها المستخدم",
#         backstory=(
#             "أنت خبير تغذية ممتاز، قادر على اقتراح وصفات بديلة ل{الطبق} إما عن طريق تغيير المكونات بالكامل لتكون أكثر صحة، "
#             "أو باستخدام كميات مختلفة من المكونات الحالية بناءً على عدد السعرات الحرارية المطلوبة من قبل المستخدم {calories}."
#         ),
#         allow_delegation=False,
#         verbose=True,
#         llm=llm
#     )

#     # أداة البحث عن السعرات الحرارية
#     docs_scrape_tool = ScrapeWebsiteTool(
#         website_url="C:/Users/Hagar/AppData/Local/Temp/aca67d69-fada-4673-84df-6e34a688bee6_دليل_السعرات_الحراريه_للطعام.zip.ee6/3738.htm"
#     )

#     recipe_recommendation_task = Task(
#         description="اقترح طريقة بديلة لتحضير نفس الطبق مع مراعاة عدد السعرات الحرارية المطلوبة.",
#         expected_output="قائمة جديدة بالمكونات والكميات المناسبة.",
#         agent=recipe_recommendation_agent,
#         tools=[docs_scrape_tool]
#     )

#     crew = Crew(
#         agents=[recipe_recommendation_agent],
#         tasks=[recipe_recommendation_task]
#     )

#     return crew
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
    st.set_page_config(page_title="Nutritionist-Food-Recognition-APP", page_icon="🍲")
    st.header("Your Dietitian and Nutritionist")

    uploaded_file = st.file_uploader("اختر صورة للطبق ...", type=["jpg", "jpeg", "png"])

    dish_name_input = st.text_input("أو أدخل اسم الطبق مباشرة:", key="dish_name_input")

    number_of_ppl = st.text_input("أدخل عدد الأشخاص:", key="number_of_ppl")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Image", use_column_width=True)

  
    col1, col2, col3 = st.columns(3)

    submit1 = col1.button("اسم الطبق")
    submit2 = col2.button("المكونات")
    submit3 = col3.button("عرض طريقة التحضير")


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
        inputs = {"الطبق": dish_name,
                  "data":data,
                  "people": number_of_ppl
                  }
        
        crew = create_first_crew()
        crew.kickoff(inputs=inputs)  # Kickoff One time only

        if submit2: 
            st.subheader("المكونات:")
            st.write(crew.tasks[0].output.raw) 

        if submit3:
            st.subheader("طريقة التحضير:")
            st.write(crew.tasks[1].output.raw)

            video_link = get_youtube_video_link(dish_name)
            st.subheader("فيديو طريقة التحضير:")
            st.video(video_link)


if __name__ == "__main__":
    main()


