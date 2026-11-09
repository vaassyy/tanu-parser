import requests
from bs4 import BeautifulSoup
import datetime
import time
import re

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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}

offers_xml = ""
offer_id_counter = 1

print("🚀 Старт парсинга (установлен таймаут 45 секунд для медленного сервера)...")

for cat_url in URLS:
    print(f"\n📂 Категория: {cat_url}")
    
    # Для первого теста парсим по 2 страницы с каждой категории
    for page in range(1, 3):
        page_url = f"{cat_url}?page={page}" if page > 1 else cat_url
        
        try:
            print(f"   ⏳ Загрузка страницы {page}...")
            # УВЕЛИЧЕН ТАЙМАУТ до 45 секунд
            res = requests.get(page_url, headers=HEADERS, timeout=45)
            
            if res.status_code != 200:
                print(f"   ❌ Ошибка доступа: код {res.status_code}")
                break
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # НОВЫЕ КЛАССЫ: ищем по их родному классу catalogCard
            items = soup.select('.catalogCard, div[class^="catalogCard"]')
            
            # Если не нашло, пробуем найти по картинке и подняться к родителю
            if not items:
                imgs = soup.select('.catalogCard-img')
                if imgs:
                    # Ищем родительский контейнер, который держит всю карточку
                    items = [img.find_parent('div') for img in imgs if img.find_parent('div')]

            if not items:
                print("   ⚠️ Товары на странице не найдены или категория закончилась.")
                break
                
            print(f"   ✅ Найдено товаров: {len(items)}")
            
            for item in items:
                # Название
                name_elem = item.select_one('[class*="title"], [class*="name"], a')
                name = name_elem.text.strip() if name_elem else "Без названия"
                
                # Ссылка
                link_elem = item.select_one('a')
                link = link_elem['href'] if link_elem and link_elem.has_attr('href') else cat_url
                if link.startswith('/'): link = "https://od.tanu.ua" + link
                
                # Цена (ищем любые цифры с точкой, например 95.10)
                price_elem = item.select_one('[class*="price"], b, strong')
                price_text = price_elem.text if price_elem else "0"
                price_text = price_text.replace(',', '.')
                price_match = re.search(r'[\d\.]+', price_text)
                price = price_match.group(0) if price_match else "0"
                
                # Фото
                img_elem = item.select_one('img')
                img_src = ""
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src') or ""
                    if img_src.startswith('/'): img_src = "https://od.tanu.ua" + img_src
                
                # Записываем в XML только если есть нормальная цена и название
                if price != "0" and name != "Без названия":
                    offers_xml += f"""
        <offer id="{offer_id_counter}" available="true">
            <url>{link}</url>
            <price>{price}</price>
            <picture>{img_src}</picture>
            <name>{name}</name>
        </offer>"""
                    offer_id_counter += 1
            
            time.sleep(2) # Пауза 2 секунды между страницами, чтобы не нагружать их сервер
            
        except Exception as e:
            print(f"   ❌ Ошибка парсинга: {e}")
            break

# Сборка финального файла
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

print(f"\n🎉 Парсинг завершен! Всего успешно собрано товаров: {offer_id_counter - 1}")
