import streamlit as st
from crew_pantry import handle_chat
import pantry_manager

# ✅ إعداد التطبيق
st.set_page_config(page_title="📦 إدارة المخزن الذكي", layout="wide")

# ✅ عنوان الصفحة
st.title("🤖 إدارة المخزن الذكي")

# ✅ تخزين المحادثات في الجلسة (Session State)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # ✅ تخزين المحادثات السابقة

# ✅ تنظيم الصفحة باستخدام الأعمدة (Sidebar + Main Content)
with st.sidebar:
    st.markdown("## 📥 **إضافة / تحديث منتج**")
    
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

# ✅ عرض المحادثات مثل ChatGPT
st.markdown("### 💬 **محادثة مع الذكاء الاصطناعي**")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ✅ إدخال المستخدم
user_input = st.chat_input("💡 اسأل عن المخزن، المنتجات الناقصة، أو قائمة التسوق:")

if user_input:
    # ✅ عرض رسالة المستخدم مباشرةً
    st.chat_message("user").markdown(user_input)
    
    # ✅ إرسال السؤال إلى الذكاء الاصطناعي
    response = handle_chat(user_input)
    
    # ✅ عرض رد الذكاء الاصطناعي مباشرةً
    with st.chat_message("assistant"):
        st.markdown(response)

    # ✅ حفظ المحادثة في الجلسة حتى تبقى معروضة
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": response})

# ✅ تقارير المخزن تظهر دائمًا أسفل المحادثة
st.markdown("### 📊 **تقارير المخزن**")

col1, col2, col3 = st.columns(3)  # ✅ توزيع التقارير على 3 أعمدة

with col1:
    st.markdown("#### 📦 **تقرير حالة المخزن**")
    st.markdown(f"🔍 **{handle_chat('المخزن')}**")

with col2:
    st.markdown("#### ⚠️ **المنتجات القريبة من النفاد**")
    st.markdown(f"❗ **{handle_chat('المنتجات الناقصة')}**")

with col3:
    st.markdown("#### 📝 **قائمة التسوق**")
    st.markdown(f"🛒 **{handle_chat('قائمة التسوق')}**")
