from dotenv import load_dotenv
load_dotenv()

import streamlit as st 
import os
from PIL import Image
import google.generativeai as genai
from crewai import Agent,Task,Crew,LLM

# Set up the API key for Gemini
os.environ["GEMINI_API_KEY"] = 'AIzaSyBeUOLiWjMI-lzYrpxmG8IKyn9nKQyrlfg'
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

# Define the agents for analyzing the response
def create_agents(response_text):
    # First agent to extract the dish name
    cooking_instruction_agent = Agent(
    role="وكيل تعليمات الطهي",
    goal="توفير تعليمات الطهي خطوة بخطوة للطبق.",
    backstory="أنت تقدم تعليمات طهي مفصلة للطبق بناءً على مكوناته واسمه. هدفك هو تبسيط عملية الطهي وتوضيحها بطريقة سهلة وواضحة وجذابة للمستخدم.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Recommendation Agent - Recommend similar dishes based on ingredients
    recommendation_agent = Agent(
    role="وكيل التوصيات",
    goal="توصية بأطباق مشابهة بناءً على مكونات الطبق.",
    backstory="أنت تحلل مكونات الطبق المرفق وتوصي بأطباق مشابهة يمكن تحضيرها باستخدام مكونات مماثلة أو نفسها.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

    # Create tasks for both agents
    recommend_dish_task = Task(
        description=(
        "ل {الطبق}١.  اقتراح ٢ إلى ٣ أطباق مشابهة بناءً على المكونات المستخرجة.\n"
        "٢. تقديم وصف مختصر لكل طبق موصى به."
    ),
    expected_output="قائمة بالأطباق المشابهة مع أوصاف.",
    agent=recommendation_agent,
    input_data=response_text
    )

    cooking_instructions_task = Task(
        description=(
        "١. تقديم تعليمات طهي مفصلة ل{الطبق}، خطوة بخطوة.\n"
        "٢. تضمين نصائح وحيل مفيدة لتحسين تجربة الطهي."
    ),
    expected_output="تعليمات طهي خطوة بخطوة للطبق.",
    agent=cooking_instruction_agent,
    )

    # Create a crew with both agents and tasks
    crew = Crew(
        agents=[cooking_instruction_agent, recommendation_agent],
        tasks=[recommend_dish_task, cooking_instructions_task]
    )

    return crew

def main():
    st.set_page_config(page_title="Nutritionist-Food-Recognition-APP", page_icon="🍲")
    st.header("Your Dietitian and Nutritionist")
    
    language_options = ["Arabic"]
    selected_language = st.selectbox("Select Language:", language_options)
    
    if selected_language == "Arabic":
        input_prompt1 = """
        "استخرج اسم الطبق فقط من المرفقة."
        """
        
    input_text = st.text_input("Input Prompt: ", key="input")
    
    uploaded_file = st.file_uploader("Choose an image ...", type=["jpg", "jpeg", "png"])
    image = ""
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image.", use_column_width=True)
        
    col1, col2 = st.columns(2)
    submit1 = col1.button("Get Dish Name and Ingredients")
    
    if submit1:
        if uploaded_file is not None:
            pdf_content = input_image_setup(uploaded_file)
            response = get_gemini_response(input_prompt1, pdf_content, input_text)
            st.subheader("The Response is")
            st.write(response)
            
            # Create and kickoff the agents after getting the response
            crew = create_agents(response)
            inputs = {
                "الطبق": response
                    }
            result = crew.kickoff(inputs=inputs)
            
            st.subheader("The Final Response from Agents")
            st.write(result)
        else:
            st.write("Please upload the dish image.")

if __name__ == "__main__":
    main()


