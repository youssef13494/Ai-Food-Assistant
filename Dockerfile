# استخدم صورة Python الرسمية كأساس
FROM python:3.10

# تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع إلى الحاوية
COPY . /app

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تعيين المنفذ الافتراضي لتطبيق Streamlit
EXPOSE 8501

# تشغيل التطبيق
CMD ["streamlit", "run", "غذائك.py", "--server.port=8501", "--server.address=0.0.0.0"]

# ===============================
# Dockerfile for Streamlit App
# ===============================

# 3. Build the Docker Image
# To build the Docker image, run the following command in the terminal:
# docker build -t streamlit-app .
#
# This command will build the Docker image using the Dockerfile in the current directory 
# and tag it with the name "streamlit-app".
#
# 4. Run the Docker Container
# To run the Docker container, execute the following command:
# docker run -p 8501:8501 streamlit-app
#
# This command will run the Docker container and map port 8501 of the host machine 
# to port 8501 of the container.
#
# 5. Access the Streamlit App
# Open your web browser and navigate to http://localhost:8501 to access the 
# Streamlit app running inside the Docker container.
#
# ===============================
# Conclusion
# ===============================
# In this tutorial, you learned how to deploy a Streamlit app using Docker.
# You created a Streamlit app, created a Dockerfile to package the app, built a Docker image, 
# and ran a Docker container to host the Streamlit app.
#
# To learn more about Streamlit, check out the official documentation.
#
# If you have any questions or feedback, feel free to leave a comment.
#
# Share this: Twitter | Facebook
#
# Like this: Like   Loading...
