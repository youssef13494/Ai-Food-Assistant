import streamlit as st

st.set_page_config(page_title="Multi-App", layout="wide")

# إضافة اللوجو واسم المشروع في الأعلى
col_logo, col_title = st.columns([1, 5])  # تخصيص نسبة العرض

with col_logo:
    st.image("Images/logo2.png", width=80)  # استخدم مسار نسبي للصورة

with col_title:
    st.markdown("<h1 style='margin-top: 10px;'>Multi Agent Food Expert</h1>", unsafe_allow_html=True)

st.write("Select an application to proceed:")

# إنشاء الأزرار لفتح التطبيقات
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Store"):
        st.session_state["page"] = "app1"

with col2:
    if st.button("Chef"):
        st.session_state["page"] = "app2"

with col3:
    if st.button("Assistant"):
        st.session_state["page"] = "app3"

# تشغيل التطبيقات بناءً على الاختيار
if "page" not in st.session_state:
    st.session_state["page"] = "home"

if st.session_state["page"] == "home":
    pass  # الصفحة الرئيسية معروضة بالفعل
elif st.session_state["page"] == "app1":
    exec(open("pages/app1.py").read())
elif st.session_state["page"] == "app2":
    exec(open("pages/app2.py").read())
elif st.session_state["page"] == "app3":
    exec(open("pages/app3.py").read())
