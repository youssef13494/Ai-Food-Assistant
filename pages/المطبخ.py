import streamlit as st
from crew_pantry import kickoff  # ✅ استدعاء CrewAI مباشرةً
import pantry_manager
from streamlit_mic_recorder import speech_to_text
import json
import pandas as pd
import altair as alt
import base64

st.set_page_config(page_title="📦 إدارة المخزن الذكي", layout="wide")

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
add_bg_from_local(r"Images\\home2.jpg")  # تأكد أن الصورة في نفس مجلد الكود

# ✅ وظيفة تسجيل الصوت
def record_voice(language="ar"):
    text = speech_to_text(
        start_prompt="🎤 اضغط للتحدث واسأل عن المخزن",
        stop_prompt="⚠️ توقف عن التسجيل",
        language=language,
        use_container_width=True,
        just_once=True,
    )
    return text if text else None

# ✅ عنوان الصفحة
st.title("🤖 إدارة المخزن الذكي")

# ✅ تخزين المحادثات في الجلسة (Session State)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # ✅ تخزين المحادثات السابقة

# ✅ تنظيم الصفحة باستخدام الشريط الجانبي (Sidebar)
with st.sidebar:
    st.markdown("## 📥 **إضافة / تحديث منتج**")
        # ✅ قسم اختيار اللغة للصوت
    with st.expander("🎙️ **خيارات الصوت**"):
        language = st.selectbox("🌐 **اختر لغة التسجيل**", ["ar", "en", "fr", "de", "es"])
    product_name = st.text_input("📝 **اسم المنتج**:")
    current_quantity = st.number_input("📊 **الكمية المتاحة:**", min_value=0, step=1)
    min_quantity = st.number_input("⚠️ **الحد الأدنى للمنتج:**", min_value=1, step=1)
    price_per_unit = st.number_input("💰 **السعر لكل وحدة / كيلو:**", min_value=0.0, step=0.1)

    if st.button("✅ **إضافة / تحديث المنتج**"):
        if product_name and current_quantity >= 0 and min_quantity >= 1 and price_per_unit >= 0:
            pantry_manager.add_product(product_name, min_quantity, current_quantity, price_per_unit)
            st.success("✅ **تم تحديث المخزن بنجاح!**")
        else:
            st.warning("⚠️ **يرجى إدخال جميع البيانات بشكل صحيح!**")
    st.markdown("## 🔻 **استهلاك منتج**")

    consumed_product = st.text_input("📝 **اسم المنتج المستهلك:**")
    consumed_quantity = st.number_input("⚠️ **الكمية المستهلكة:**", min_value=1, step=1)

    if st.button("❌ **استهلاك المنتج**"):
        if consumed_product and consumed_quantity > 0:
            success = pantry_manager.consume_product(consumed_product, consumed_quantity)
            if success:
                st.success(f"✅ **تم استهلاك {consumed_quantity} من {consumed_product} بنجاح!**")
            else:
                st.warning("⚠️ **الكمية المتاحة غير كافية أو المنتج غير موجود!**")
        else:
            st.warning("⚠️ **يرجى إدخال اسم المنتج والكمية المستهلكة بشكل صحيح!**")

# ✅ عرض المحادثات مثل ChatGPT
st.markdown("### 💬 **محادثة مع الذكاء الاصطناعي**")


# ✅ عرض تقرير المخزن فقط
st.markdown("### 📊 **تقرير المخزن**")


with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


items = []
for item_name, details in data.items():
    details['item'] = item_name  
    items.append(details)
df = pd.DataFrame(items)
df['color'] = df.apply(
    lambda row: 'red' if row['current_quantity'] <= row['min_quantity'] * 1.1 else 'green',
    axis=1
)

st.write("Inventory Data")

chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('item:N', title='المكونات'),
    y=alt.Y('current_quantity:Q', title='الكمية'),
    color=alt.Color('color:N', scale=None)
).properties(
    title='المخزن'
).configure_title(
    anchor='middle',
    fontSize=30 
).configure_axis(
    titleFontSize=20,   
    labelFontSize=16    
)
st.altair_chart(chart, use_container_width=True)

from tools import update_user_info  # ✅ استيراد دالة تحديث بيانات المستخدم

# ✅ واجهة اختيار بيانات المستخدم
st.sidebar.markdown("## 👤 **معلومات المستخدم**")
age = st.sidebar.number_input("📅 **العمر:**", min_value=1, max_value=120, step=1)
weight = st.sidebar.number_input("⚖️ **الوزن (كجم):**", min_value=1.0, max_value=300.0, step=0.1)
height = st.sidebar.number_input("📏 **الطول (سم):**", min_value=50, max_value=250, step=1)
status = st.sidebar.selectbox("🏥 **الحالة الصحية:**", ["طفل", "سيدة", "شاب","سيدة حامل", "صاحب امراض مزمنة", "رياضي/رياضية","كبار سن"])

if st.sidebar.button("✅ **حفظ البيانات**"):
    update_user_info(age, weight, height, status)
    st.sidebar.success("✅ **تم حفظ بيانات المستخدم!**")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.chat_input("💡 اسأل عن المخزن، المنتجات الناقصة، أو قائمة التسوق:")

with col2:
    voice_input = record_voice(language=language)
    if voice_input:
        st.success("🎤 تم تسجيل الصوت بنجاح!")


# ✅ معالجة إدخال المستخدم (نص أو صوت)
if voice_input:
    final_input = voice_input
    st.chat_message("user").markdown(final_input)
    user_input=final_input

if user_input:
    # ✅ عرض رسالة المستخدم مباشرةً
    st.chat_message("user").markdown(user_input)
    
    # ✅ إرسال السؤال إلى CrewAI
    response = kickoff(user_input)  
    
    # ✅ عرض رد الذكاء الاصطناعي مباشرةً
    with st.chat_message("assistant"):
        st.markdown(response)

    # ✅ حفظ المحادثة في الجلسة حتى تبقى معروضة
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

