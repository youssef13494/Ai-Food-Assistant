import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# رابط صفحة المطاعم في Talabat
url = "https://www.talabat.com/ar/egypt/restaurants/8039/zamalek-26-july"

# إعداد المتصفح
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # تشغيل بدون واجهة
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# تشغيل Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

try:
    # فتح صفحة المطاعم الرئيسية
    driver.get(url)
    time.sleep(5)  # انتظار تحميل الصفحة

    # انتظار تحميل جميع المطاعم
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "vendor-card"))
    )

    # استخراج جميع روابط المطاعم أولاً
    restaurant_links = []
    restaurants = driver.find_elements(By.CLASS_NAME, "vendor-card")

    for restaurant in restaurants:
        try:
            restaurant_link = restaurant.find_element(By.XPATH, "./ancestor::a").get_attribute("href")
            if restaurant_link and restaurant_link not in restaurant_links:
                restaurant_links.append(restaurant_link)
        except:
            continue

    extracted_data = []
    print(restaurant_links)

    # المرور على كل مطعم واحدًا تلو الآخر
    for restaurant_link in restaurant_links:
        driver.get(restaurant_link)
        print(f"🔍 جاري استخراج بيانات المطعم: {restaurant_link}")
        time.sleep(5)  # انتظار تحميل الصفحة

        try:
            # استخراج بيانات المطعم
            name = driver.find_element(By.TAG_NAME, "h1").text.strip()
        except:
            name = "N/A"

        try:
            food_types = driver.find_element(By.CLASS_NAME, "vendor-food-type").text.strip()
        except:
            food_types = "N/A"

        try:
            rating = driver.find_element(By.CLASS_NAME, "rating-word").text.strip()
        except:
            rating = "N/A"

        try:
            delivery_info = [span.text.strip() for span in driver.find_elements(By.TAG_NAME, "span")]
        except:
            delivery_info = []

        try:
            image = driver.find_element(By.CLASS_NAME, "vendor-image").get_attribute("src")
        except:
            image = "No Image"

        # استخراج قائمة الطعام
        menu_items = []
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "sc-a31f9fb2-0"))
            )
            menu_elements = driver.find_elements(By.CLASS_NAME, "sc-a31f9fb2-0")

            for item in menu_elements:
                try:
                    meal_name = item.find_element(By.CLASS_NAME, "f-15").text.strip()
                except:
                    meal_name = "N/A"

                try:
                    description = item.find_element(By.CLASS_NAME, "f-12").text.strip()
                except:
                    description = "N/A"

                try:
                    price = item.find_element(By.CLASS_NAME, "currency").text.strip()
                except:
                    price = "N/A"

                try:
                    meal_image = item.find_element(By.TAG_NAME, "img").get_attribute("src")
                except:
                    meal_image = "No Image"

                menu_items.append({
                    "meal_name": meal_name,
                    "description": description,
                    "price": price,
                    "image": meal_image
                })
        except:
            menu_items = []

        # تجميع البيانات
        extracted_data.append({
            "name": name,
            "food_types": food_types,
            "rating": rating,
            "delivery_info": delivery_info,
            "image": image,
            "restaurant_link": restaurant_link,
            "menu": menu_items
        })

    # حفظ البيانات في ملف JSON
    with open("restaurants_with_menu.json", "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    print("✅ تم حفظ جميع بيانات المطاعم في restaurants_with_menu.json بنجاح!")

finally:
    # إغلاق المتصفح
    driver.quit()
