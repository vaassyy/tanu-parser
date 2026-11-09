import datetime

# Генерируем тестовый XML
xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}">
    <shop>
        <name>Test OD Tanu</name>
        <offers>
            <offer id="123" available="true">
                <price>1500</price>
                <name>Тестовый товар</name>
            </offer>
        </offers>
    </shop>
</yml_catalog>
"""

# Сохраняем его в файл
with open("feed.xml", "w", encoding="utf-8") as file:
    file.write(xml_content)

print("XML успешно создан!")
