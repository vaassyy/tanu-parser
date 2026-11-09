import requests
from bs4 import BeautifulSoup
import datetime
import time
import re

# Твои 14 категорий
URLS = [
    "https://od.tanu.ua/fishing/",
    "https://od.tanu.ua/kids/",
    "https://od.tanu.ua/telefony-tv-i-ehlektronika/",
    "https://od.tanu.ua/computers-notebooks/",
    "https://od.tanu.ua/bytovaya-tekhnika-interyer/",
    "https://od.tanu.ua/tovary-dlya-doma/",
    "https://od.tanu.ua/dacha-sad-ogorod/",
    "https://od.tanu.ua/santekhnika/",
    "https://od.tanu.ua/instrumenty-i-avtotovary/",
    "https://od.tanu.ua/sport-i-uvlecheniya/",
    "https://od.tanu.ua/krasota-i-zdorovje/",
    "https://od.tanu.ua/podarki-i-tovary-dlya-prazdnikov/",
    "https://od.tanu.ua/office-school-books/",
    "https://od.tanu.ua/tovary-dlya-biznesa/"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

offers_xml = ""
offer_id_counter = 1

print("🚀 Старт парсинга...")

for cat_url in URLS:
    print(f"\n📂 Категория: {cat_url}")
    
    # ДЛЯ ТЕСТА: парсим только первые 2 страницы каждой категории
    for page in range(1, 3):
        # Формируем ссылку (обычно страницы идут как ?page=2)
        page_url = f"{cat_url}?page={page}" if page > 1 else cat_url
        
        try:
            print(f"   ⏳ Загрузка страницы {page}...")
            res = requests.get(page_url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                print(f"   ❌ Ошибка доступа: код {res.status_code}")
                break
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Ищем карточки товаров по самым популярным классам
            items = soup.select('.product-layout, .product-thumb, .product-item, .catalog-item, .item, .product-card, .products-list-item')
            
            if not items:
                print("   ⚠️ Товары не найдены. (Нужно уточнить верстку сайта)")
                break
                
            print(f"   ✅ Найдено товаров: {len(items)}")
            
            for item in items:
                # Название
                name_elem = item.select_one('.name, .product-name, h4 a, .title, .catalog-item__name, .product-title')
                name = name_elem.text.strip() if name_elem else "Без названия"
                
                # Ссылка
                link = name_elem['href'] if name_elem and name_elem.has_attr('href') else cat_url
                if link.startswith('/'): link = "https://od.tanu.ua" + link
                
                # Цена
                price_elem = item.select_one('.price, .product-price, .price-new, .catalog-item__price, .current-price')
                price_text = price_elem.text if price_elem else "0"
                price = re.sub(r'[^\d]', '', price_text) # Оставляем только цифры
                if not price: price = "0"
                
                # Фото
                img_elem = item.select_one('img')
                img_src = ""
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src') or ""
                    if img_src.startswith('/'): img_src = "https://od.tanu.ua" + img_src
                
                offers_xml += f"""
        <offer id="{offer_id_counter}" available="true">
            <url>{link}</url>
            <price>{price}</price>
            <picture>{img_src}</picture>
            <name>{name}</name>
        </offer>"""
                offer_id_counter += 1
            
            time.sleep(1) # Пауза, чтобы не заблокировали
            
        except Exception as e:
            print(f"   ❌ Ошибка парсинга: {e}")
            break

# Сборка финального YML
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
final_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="{current_time}">
    <shop>
        <name>OD Tanu</name>
        <company>OD Tanu Dropshipping</company>
        <url>https://od.tanu.ua/</url>
        <currencies>
            <currency id="UAH" rate="1"/>
        </currencies>
        <offers>
            {offers_xml}
        </offers>
    </shop>
</yml_catalog>
"""

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(final_xml)

print(f"\n🎉 Парсинг завершен! Всего собрано товаров: {offer_id_counter - 1}")
