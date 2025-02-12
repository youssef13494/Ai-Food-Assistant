from pantry_manager import load_pantry

def generate_shopping_list():
    """توليد قائمة تسوق بناءً على الكميات المتوفرة"""
    pantry = load_pantry()
    return {
        name: max(0, data["min_quantity"] - data["current_quantity"])  # ✅ التأكد من عدم ظهور قيم سالبة
        for name, data in pantry.items() if data["current_quantity"] < data["min_quantity"]
    }
