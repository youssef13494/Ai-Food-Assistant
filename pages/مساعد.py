import os
import streamlit as st
import google.generativeai as genai
from crewai import Agent, Task, Crew, LLM

from dotenv import load_dotenv
load_dotenv()
# 🔹 Set API Keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_BASE"] = os.getenv("OPENAI_API_BASE")
os.environ["OPENAI_MODEL_NAME"] = os.getenv("OPENAI_MODEL_NAME")


llm = LLM(
    model=os.environ["OPENAI_MODEL_NAME"],
    temperature=0.4,
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_API_BASE"]
)


# Streamlit UI
st.title("🍽️ مساعد السعرات الحرارية الذكي")

# User Input Fields
dish_name = st.text_input("ادخل اسم الطبق")
quan = st.text_input("عدد الافراد")
calories = st.text_input("عدد السعرات للفرد")

def my_crew(llm):
    # Define Agents
    ingredients_identifier_agent = Agent(
        role="Ingredients Identifier",
        goal="Retrieve ingredients for a given dish with quantities",
        backstory=(
            "You are a famous chef, you can get the ingredients required to make any dish in arabic {dish_name} "
            "and the quantity based on how many people are going to eat {quan}."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    calories_calculator_agent = Agent(
        role="Calories Calculator",
        goal="Determine the calorie count of each ingredient",
        backstory="You are a nutritionist who calculates the calorie content of ingredients while considering quantity.",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    
    recipe_recommendation_agent = Agent(
        role="Recipe Recommendation",
        goal="Suggest a healthier alternative while maintaining the requested calorie intake.",
        backstory=(
            "You are a skilled dietitian. You can suggest alternative recipes by either changing the ingredients completely "
            "to be healthier or adjusting the quantity of existing ingredients based on the user's requested calories {calories}."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm,
        max_execution_time= 60
    )
    
    # Define Tasks
    ingredients_identification_task = Task(
        description="Identify the ingredients and their quantities for the given dish.",
        expected_output="A structured list of ingredients with quantities in arabic.",
        agent=ingredients_identifier_agent,
    )
    
    calories_calculator_task = Task(
        description="Calculate the calorie content of each ingredient.",
        expected_output="A breakdown of calorie content per ingredient in arabic.",
        agent=calories_calculator_agent,
    )
    
    recipe_recommendation_task = Task(
        description="Suggest an alternative version of the dish while maintaining calorie requirements.",
        expected_output="An optimized recipe with adjusted ingredients and quantities in arabic.",
        agent=recipe_recommendation_agent,
    )
    
    # Initialize Crew
    crew = Crew(
        agents=[ingredients_identifier_agent, calories_calculator_agent, recipe_recommendation_agent],
        tasks=[ingredients_identification_task, calories_calculator_task, recipe_recommendation_task]
    )
    
    return crew
inputs = {
                "dish_name": dish_name,
                "calories": calories,
                "quan": quan
            }

st.subheader("تشغيل المساعد")
crew = my_crew(llm)
if st.button("الحصول علي الوصفة"):
    task_output = crew.kickoff(inputs=inputs)
    with st.spinner("Identifying ingredients..."):
        ingredients_result = crew.tasks[0].output.raw
    st.success("Ingredients Identified!")
    st.write(ingredients_result)
    st.subheader("السعرات الحرارية للمكونات:")
    st.write(crew.tasks[1].output.raw)  # Display the result # Fetching the first (and only) task's output
    st.subheader("الوصفة الجديدة:")
    st.write(crew.tasks[2].output.raw)  # Display the result # Fetching the first (and only) task's output

