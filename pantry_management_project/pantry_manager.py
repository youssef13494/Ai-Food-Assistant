import json
import os

DATA_FILE = "data.json"

def load_pantry():
    """تحميل بيانات المخزن من ملف JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}  # ✅ التعامل مع الملفات الفارغة أو غير الصالحة
    return {}

def save_pantry(data):
    """حفظ بيانات المخزن إلى ملف JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def add_product(name, min_quantity, current_quantity, price_per_unit):
    """إضافة منتج جديد أو تحديث منتج موجود"""
    pantry = load_pantry()
    pantry[name] = {
        "min_quantity": min_quantity,
        "current_quantity": current_quantity,
        "price_per_unit": price_per_unit
    }
    save_pantry(pantry)

def update_quantity(name, new_quantity):
    """تحديث الكمية المتوفرة لمنتج معين"""
    pantry = load_pantry()
    if name in pantry:
        pantry[name]["current_quantity"] = new_quantity
        save_pantry(pantry)

def check_low_stock():
    """التحقق من المنتجات التي أوشكت على النفاد"""
    pantry = load_pantry()
    return {name: data for name, data in pantry.items() if data["current_quantity"] <= data["min_quantity"]}
