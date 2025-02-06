#!pip install --force-reinstall 'httpx<0.28'
#!pip install youtube-search-python
from youtubesearchpython import VideosSearch

def get_first_video_link(dish_name):
    videos_search = VideosSearch(dish_name, limit = 1)
    result = videos_search.result()
    # الحصول على الرابط من النتيجة
    first_video_url = result['result'][0]['link']
    return first_video_url

# استخدام الوظيفة مع اسم الطبق
dish_name = 'بيتزا'
link = get_first_video_link(dish_name)
print("أول فيديو:", link)