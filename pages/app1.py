import streamlit as st
from crew_pantry import kickoff  # ✅ استدعاء CrewAI مباشرةً
import pantry_manager
from streamlit_mic_recorder import speech_to_text

# ✅ إعداد التطبيق
st.set_page_config(page_title="📦 إدارة المخزن الذكي", layout="wide")
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
# ✅ إدخال المستخدم
# user_input = st.chat_input("💡 اسأل عن المخزن، المنتجات الناقصة، أو أي شيء آخر:")
# ✅ معالجة إدخال المستخدم (نص أو صوت)
if user_input or voice_input:
    final_input = user_input if user_input else voice_input
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

# ✅ عرض تقرير المخزن فقط
st.markdown("### 📊 **تقرير المخزن**")

import streamlit as st
import json
import pandas as pd
import altair as alt

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


# ✅ استدعاء CrewAI لإحضار تقرير المخزن وعرضه كجدول Markdown
inventory_report = kickoff("ممكن تقرير عن المخزن؟")  
st.markdown(inventory_report)
