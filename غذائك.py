import streamlit as st

st.set_page_config(page_title="Multi-App", layout="wide")

# إضافة اللوجو واسم المشروع في الأعلى
col_logo, col_title = st.columns([1, 3])  # تخصيص نسبة العرض

with col_logo:
    st.image("Images/logo2.png", width=400)  # استخدم مسار نسبي للصورة

with col_title:
    st.markdown("<h1 style='margin-top: 10px; '>غذائك</h1>", unsafe_allow_html=True)



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

