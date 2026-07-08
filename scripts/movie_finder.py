#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 جوینده هوشمند فیلم با TMDB API
هر روز ۲ فیلم متفاوت و غیرتکراری - دریافت از چندین صفحه - تاریخچه نامحدود
"""

import requests
import random
import json
import os
from datetime import datetime
from pathlib import Path
from deep_translator import GoogleTranslator

# ==================================================
# 📁 تنظیمات اولیه
# ==================================================

DATA_DIR = Path('data')
HISTORY_FILE = DATA_DIR / 'movie_history.json'

TMDB_API_KEY = "b720e1c8103f7eb7da831c5268ea5cb0"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    'Accept': 'application/json',
}

# ==================================================
# 🌐 ترجمه به فارسی
# ==================================================

def translate_to_fa(text, max_length=400):
    """ترجمه به فارسی"""
    if not text or len(text.strip()) < 3:
        return text
    
    persian_chars = len([c for c in text if '\u0600' <= c <= '\u06FF'])
    if persian_chars > len(text) * 0.3:
        return text
    
    try:
        translator = GoogleTranslator(source='en', target='fa')
        return translator.translate(text[:max_length])
    except:
        return text

# ==================================================
# 🎬 دریافت فیلم‌ها از TMDB (چندین صفحه)
# ==================================================

def fetch_tmdb(endpoint, params=None):
    """درخواست به TMDB API"""
    url = f"{TMDB_BASE_URL}/{endpoint}"
    default_params = {'api_key': TMDB_API_KEY}
    if params:
        default_params.update(params)
    
    try:
        response = requests.get(url, params=default_params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   ❌ خطا در TMDB: {e}")
        return None

def get_popular_movies(pages=10):
    """دریافت فیلم‌های محبوب از چندین صفحه"""
    print(f"   📡 دریافت فیلم‌های محبوب از {pages} صفحه...")
    all_movies = []
    
    for page in range(1, pages + 1):
        data = fetch_tmdb('movie/popular', {
            'language': 'en-US',
            'page': page
        })
        if data and 'results' in data:
            for item in data['results']:
                all_movies.append({
                    'id': item['id'],
                    'title': item['title'],
                    'rating': round(item['vote_average'], 1),
                    'year': item['release_date'][:4] if item['release_date'] else 'نامشخص',
                    'source': 'TMDB محبوب'
                })
    
    print(f"   ✅ {len(all_movies)} فیلم محبوب دریافت شد")
    return all_movies

def get_top_rated_movies(pages=10):
    """دریافت فیلم‌های برتر از چندین صفحه"""
    print(f"   📡 دریافت فیلم‌های برتر از {pages} صفحه...")
    all_movies = []
    
    for page in range(1, pages + 1):
        data = fetch_tmdb('movie/top_rated', {
            'language': 'en-US',
            'page': page
        })
        if data and 'results' in data:
            for item in data['results']:
                all_movies.append({
                    'id': item['id'],
                    'title': item['title'],
                    'rating': round(item['vote_average'], 1),
                    'year': item['release_date'][:4] if item['release_date'] else 'نامشخص',
                    'source': 'TMDB برتر'
                })
    
    print(f"   ✅ {len(all_movies)} فیلم برتر دریافت شد")
    return all_movies

def get_upcoming_movies(pages=8):
    """دریافت فیلم‌های در حال اکران از چندین صفحه"""
    print(f"   📡 دریافت فیلم‌های جدید از {pages} صفحه...")
    all_movies = []
    
    for page in range(1, pages + 1):
        data = fetch_tmdb('movie/upcoming', {
            'language': 'en-US',
            'page': page
        })
        if data and 'results' in data:
            for item in data['results']:
                all_movies.append({
                    'id': item['id'],
                    'title': item['title'],
                    'rating': round(item['vote_average'], 1) if item['vote_average'] else 'جدید',
                    'year': item['release_date'][:4] if item['release_date'] else 'به‌زودی',
                    'source': 'TMDB جدید'
                })
    
    print(f"   ✅ {len(all_movies)} فیلم جدید دریافت شد")
    return all_movies

def get_now_playing_movies(pages=5):
    """دریافت فیلم‌های در حال اکران از چندین صفحه"""
    print(f"   📡 دریافت فیلم‌های در حال اکران از {pages} صفحه...")
    all_movies = []
    
    for page in range(1, pages + 1):
        data = fetch_tmdb('movie/now_playing', {
            'language': 'en-US',
            'page': page
        })
        if data and 'results' in data:
            for item in data['results']:
                all_movies.append({
                    'id': item['id'],
                    'title': item['title'],
                    'rating': round(item['vote_average'], 1),
                    'year': item['release_date'][:4] if item['release_date'] else 'نامشخص',
                    'source': 'TMDB در حال اکران'
                })
    
    print(f"   ✅ {len(all_movies)} فیلم در حال اکران دریافت شد")
    return all_movies

def get_movie_details(movie_id):
    """دریافت اطلاعات کامل یک فیلم با ID"""
    data = fetch_tmdb(f'movie/{movie_id}', {
        'language': 'en-US',
        'append_to_response': 'credits'
    })
    
    if not data:
        return {}
    
    details = {}
    
    if data.get('overview'):
        details['summary_en'] = data['overview']
        details['summary_fa'] = translate_to_fa(data['overview'], 400)
    else:
        details['summary_fa'] = "خلاصه داستان موجود نیست"
    
    directors = []
    if 'credits' in data and 'crew' in data['credits']:
        for crew in data['credits']['crew']:
            if crew.get('job') == 'Director':
                directors.append(crew['name'])
    details['director'] = ', '.join(directors) if directors else "نامشخص"
    
    cast = []
    if 'credits' in data and 'cast' in data['credits']:
        for actor in data['credits']['cast'][:5]:
            cast.append(actor['name'])
    details['cast'] = cast if cast else ["نامشخص"]
    
    genre_fa_map = {
        'Action': 'اکشن', 'Comedy': 'کمدی', 'Drama': 'درام',
        'Horror': 'ترسناک', 'Science Fiction': 'علمی تخیلی', 'Romance': 'عاشقانه',
        'Thriller': 'هیجانی', 'Mystery': 'معمایی', 'Animation': 'انیمیشن',
        'Crime': 'جنایی', 'Adventure': 'ماجراجویی', 'Fantasy': 'فانتزی',
        'War': 'جنگی', 'History': 'تاریخی', 'Documentary': 'مستند',
        'Family': 'خانوادگی', 'Music': 'موسیقی', 'Western': 'وسترن',
        'TV Movie': 'فیلم تلویزیونی', 'Romance': 'عاشقانه'
    }
    genres = []
    for genre in data.get('genres', []):
        genre_en = genre['name']
        genres.append(genre_fa_map.get(genre_en, genre_en))
    details['genres_fa'] = genres if genres else ["متفرقه"]
    
    runtime = data.get('runtime')
    details['duration'] = f"{runtime} دقیقه" if runtime else "نامشخص"
    
    poster_path = data.get('poster_path')
    if poster_path:
        details['poster'] = f"https://image.tmdb.org/t/p/w500{poster_path}"
    else:
        details['poster'] = ""
    
    imdb_id = data.get('imdb_id')
    if imdb_id:
        details['imdb_link'] = f"https://www.imdb.com/title/{imdb_id}/"
    else:
        details['imdb_link'] = f"https://www.themoviedb.org/movie/{movie_id}"
    
    return details

# ==================================================
# 📜 مدیریت تاریخچه نامحدود
# ==================================================

def load_history():
    """بارگذاری تاریخچه فیلم‌های ارسال شده"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history):
    """ذخیره تاریخچه - بدون محدودیت"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def is_duplicate(title, history):
    """بررسی تکراری بودن فیلم در تاریخچه"""
    title_clean = title.lower().strip()
    
    for h in history:
        if h['title'].lower().strip() == title_clean:
            return True
        
        # بررسی با TMDB ID برای دقت بیشتر
        if 'tmdb_id' in h and 'tmdb_id' in history[0]:
            pass
    
    return False

# ==================================================
# 🎯 دریافت فیلم‌های امروز (نسخه نهایی)
# ==================================================

def get_todays_movies(count=2):
    """دریافت فیلم‌های امروز - هرگز تکراری نمی‌فرستد"""
    
    # بارگذاری تاریخچه
    history = load_history()
    history_count = len(history)
    
    print(f"   📊 تعداد فیلم‌های ارسال شده تا امروز: {history_count}")
    
    # جمع‌آوری فیلم‌ها از همه منابع با چندین صفحه
    all_movies = []
    all_movies.extend(get_popular_movies(pages=10))      # ۱۰ صفحه = ~۲۰۰ فیلم
    all_movies.extend(get_top_rated_movies(pages=10))    # ۱۰ صفحه = ~۲۰۰ فیلم
    all_movies.extend(get_upcoming_movies(pages=8))      # ۸ صفحه = ~۱۶۰ فیلم
    all_movies.extend(get_now_playing_movies(pages=5))   # ۵ صفحه = ~۱۰۰ فیلم
    
    # حذف تکراری‌ها بر اساس ID
    unique_movies = {}
    for movie in all_movies:
        movie_id = movie.get('id')
        if movie_id and movie_id not in unique_movies:
            unique_movies[movie_id] = movie
    
    all_movies = list(unique_movies.values())
    print(f"   📋 {len(all_movies)} فیلم منحصربه‌فرد پیدا شد")
    
    # فیلتر کردن فیلم‌های تکراری
    new_movies = []
    duplicate_count = 0
    
    for movie in all_movies:
        if not is_duplicate(movie['title'], history):
            new_movies.append(movie)
        else:
            duplicate_count += 1
    
    print(f"   🆕 {len(new_movies)} فیلم جدید | {duplicate_count} فیلم تکراری حذف شد")
    
    # اگر فیلم جدید کافی نیست، از بین همه فیلم‌ها انتخاب کن
    if len(new_movies) < count:
        print(f"   ⚠️ فیلم جدید کافی نیست! انتخاب از بین همه فیلم‌ها...")
        
        if len(all_movies) >= count:
            # انتخاب از بین همه فیلم‌ها (با اخطار)
            print(f"   ⚠️ هشدار: ممکنه فیلم تکراری ارسال بشه")
            selected = random.sample(all_movies, count)
        else:
            print(f"   ❌ هیچ فیلمی برای ارسال وجود ندارد!")
            return []
    else:
        # انتخاب تصادفی از فیلم‌های جدید
        selected = random.sample(new_movies, min(count, len(new_movies)))
    
    # دریافت جزئیات کامل
    full_movies = []
    today_date = datetime.now().isoformat()
    
    for movie in selected:
        print(f"\n   🎬 {movie['title']} ({movie['year']})")
        
        details = get_movie_details(movie['id'])
        full_movie = {**movie, **details}
        full_movies.append(full_movie)
        
        # ثبت در تاریخچه
        history.append({
            'title': full_movie['title'],
            'date': today_date,
            'tmdb_id': movie['id'],
            'year': movie['year'],
            'rating': movie['rating']
        })
    
    # ذخیره تاریخچه
    save_history(history)
    
    print(f"\n   ✅ {len(full_movies)} فیلم نهایی انتخاب شد")
    print(f"   📊 مجموع فیلم‌های ارسال شده: {len(history)}")
    return full_movies

def get_movie_stats():
    """آمار فیلم‌های ارسال شده"""
    history = load_history()
    return {
        'total': len(history),
        'last_10': history[-10:] if len(history) >= 10 else history
    }

# ==================================================
# 🚀 اجرای تست
# ==================================================

if __name__ == "__main__":
    print("🎬 شروع جستجوی فیلم‌های امروز...\n")
    print("=" * 65)
    
    movies = get_todays_movies(2)
    
    stats = get_movie_stats()
    print(f"\n📊 آمار کل: {stats['total']} فیلم ارسال شده")
    
    if movies:
        print("\n" + "=" * 65)
        for i, movie in enumerate(movies, 1):
            print(f"\n{i}. 🎬 {movie['title']} ({movie['year']})")
            print(f"   ⭐ امتیاز: {movie['rating']}")
            print(f"   🎭 ژانر: {', '.join(movie.get('genres_fa', []))}")
            print(f"   🎬 کارگردان: {movie.get('director', 'نامشخص')}")
            print(f"   👥 بازیگران: {', '.join(movie.get('cast', [])[:3])}")
            print(f"   📝 خلاصه: {movie.get('summary_fa', 'ندارد')[:150]}...")
        print("\n" + "=" * 65)
    else:
        print("\n❌ فیلمی برای ارسال پیدا نشد")
