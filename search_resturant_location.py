import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# موقع طلبات مصر
url = "https://www.talabat.com/ar/egypt"

# إعدادات المتصفح
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # إلغاء تعليق هذا السطر إذا أردت تشغيل المتصفح في الخلفية
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-web-security")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# تشغيل WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# فتح الموقع
driver.get(url)
time.sleep(3)  # انتظار تحميل الصفحة

# **الخطوة 1: الضغط على زر "تحديد موقعي"**
locate_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//img[@data-testid="btn-locate-me"]'))
)
locate_button.click()
time.sleep(2)

# **الخطوة 2: البحث عن خانة إدخال الموقع**
search_input = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, 'placeSearch'))
)

# **إدخال الموقع حرفًا حرفًا لمحاكاة الإدخال اليدوي**
location_name = "كومبرة"
for char in location_name:
    search_input.send_keys(char)
    time.sleep(0.3)  # تأخير بسيط لكل حرف

time.sleep(2)  # انتظار ظهور الاقتراحات

# **الخطوة 3: اختيار أول اقتراح**
search_input.send_keys(Keys.ARROW_DOWN)
time.sleep(1)
search_input.send_keys(Keys.RETURN)

# **الخطوة 4: انتظار تحميل الصفحة الجديدة**
time.sleep(3)

# **🔹 التأكد من اختفاء الـ Overlay**
WebDriverWait(driver, 10).until(
    EC.invisibility_of_element_located((By.XPATH, '//div[@style="z-index: 3; position: absolute; height: 100%; width: 100%;"]'))
)

# **البحث عن زر "وصِّل هنا"**
connect_button = WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, '//button[contains(@class, "button-module_button-primary__i52py")]'))
)

# التأكد من أن الزر مرئي
if connect_button.is_displayed():
    print("✅ الزر مرئي")
else:
    print("⚠️ الزر غير مرئي")

# البحث عن العنصر الذي يغطي الزر
overlay = driver.find_element(By.CLASS_NAME, "modal-backdrop")

# إزالته من الصفحة حتى لا يمنع النقر
driver.execute_script("arguments[0].remove();", overlay)

# انتظار لحظة للتأكد من إزالة الطبقة
time.sleep(1)

# المحاولة مجددًا للنقر على الزر
driver.execute_script("arguments[0].click();", connect_button)



# **الخطوة 5: طباعة الرابط الجديد بعد تحديث الموقع**
time.sleep(5)  # انتظار تحميل الصفحة

try:
    # البحث عن عنصر جديد يظهر بعد النقر
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//h1[contains(text(), "المطاعم")]'))
    )
    print("✅ تم النقر بنجاح! ظهرت قائمة المطاعم.")
except:
    print("⚠️ لم يظهر العنصر المتوقع، قد يكون النقر لم ينجح.")


new_page_url = driver.current_url
print("✅ New page URL:", new_page_url)

# **حفظ الرابط الجديد في ملف JSON**
with open("talabat_location.json", "w", encoding="utf-8") as file:
    json.dump({"location": location_name, "url": new_page_url}, file, ensure_ascii=False, indent=4)
print("✅ تم حفظ الرابط الجديد في ملف talabat_location.json")

# **إغلاق المتصفح**
driver.quit()
