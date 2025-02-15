import streamlit as st
import base64

def add_bg_from_local(image_file):
    with open(image_file, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
    
    bg_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: 100% auto;  /* Ensures full width while maintaining aspect ratio */
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)



# استدعاء الدالة مع الصورة المحلية
add_bg_from_local(r"Images\\home1.jpg")  # تأكد أن الصورة في نفس مجلد الكود





# تشغيل التطبيقات بناءً على الاختيار
if "page" not in st.session_state:
    st.session_state["page"] = "غذائك"

if st.session_state["page"] == "غذائك":
    pass  # الصفحة الرئيسية معروضة بالفعل
elif st.session_state["page"] == "دكتور التغذية":
    exec(open("pages/app1.py").read())
elif st.session_state["page"] == "الطباخ":
    exec(open("pages/app2.py").read())
elif st.session_state["page"] == "مساعد":
    exec(open("pages/app3.py").read())
elif st.session_state["page"] == "الكابتن":
    exec(open("pages/app4.py").read())

