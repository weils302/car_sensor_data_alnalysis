import time
import requests
import re
from bs4 import BeautifulSoup
import csv
import os
import datetime

YOUR_URL = 'https://www.carsensor.net/usedcar/search.php?CARC=BM_S011'
#YOUR_URL = 'https://www.carsensor.net/usedcar/index.html?STID=CS210610&AR=&BRDC=&CARC=BM_S011&NINTEI=&CSHOSHO='


def get_html(url):
    response = requests.get(url)
    return response.content.decode('utf-8')


def parse_html(html):
    return BeautifulSoup(html, 'html.parser')


def get_last_page_num(soup):
    CSS_LAST_PAGE_NUM = soup.select('#js-resultBar > div.resultBar__link > div > div.pager__text > a:nth-child(12)')[0]
    return extract_number_from_href(CSS_LAST_PAGE_NUM['href'])


def extract_number_from_href(href):
    match = re.search(r'index(\d+)', href)
    if match:
        return int(match.group(1))
    else:
        return None


def get_next_page_url(soup, current_page_num):
    CSS_NEXT_PAGE = '#js-resultBar > div.resultBar__link > div > div.pager__text > a'
    next_page_elements = soup.select(CSS_NEXT_PAGE)
    for element in next_page_elements:
        if element.text == str(current_page_num + 1):
            return 'https://www.carsensor.net' + element['href']
    return None


def get_detail_page_urls(soup):
    CSS_DETAIL_PAGE_LINKS = 'div.cassetteMain > div > div.cassetteMain__carInfoContainer > h3 > a'
    detail_page_elements = soup.select(CSS_DETAIL_PAGE_LINKS)
    urls = []
    for element in detail_page_elements:
        href = element['href']
        if 'lease' not in href:
            urls.append('https://www.carsensor.net' + href)
    return urls


def extract_data(soup, url):
    data = {}
    # List of selectors that need special handling
    special_handling_keys = ['body_type', 'drive_type', 'color', 'right_handle', 'transmission', 'displacement',
                             'member', 'engine_type_gasoline', 'door_number']

    for key, selector in CSS_SELECTORS.items():
        if selector is None:
            continue

        element = soup.select_one(selector)

        # If the main selector didn't match and the key requires special handling, try the alternate selector
        if element is None and key in special_handling_keys and 'section:nth-child(6)' in selector:
            alternate_selector = selector.replace('section:nth-child(6)', 'section:nth-child(5)')
            element = soup.select_one(alternate_selector)

        if element:
            if key == 'base_price':
                data[key] = element.get('content').replace(",", "")  # remove comma from the number
            elif key == 'total_price':
                price_text = element.text.strip()  # remove leading/trailing whitespaces
                if price_text == "---万円":
                    data[key] = "0"
                else:
                    # remove '万円' and convert to the required format
                    price_text = price_text.replace('万円', '')
                    price_float = float(price_text) * 10000  # convert '万' to actual number
                    data[key] = str(int(price_float))  # convert it to string without comma
            elif key == 'distance':
                distance_float = float(element.text) * 10000
                data[key] = str(int(distance_float))
            elif key == 'inspection_remaining_month':
                inspection_elements = element.select('p')
                if len(inspection_elements) >= 2:
                    inspection_text = inspection_elements[1].text
                    if inspection_text == "車検整備付":
                        data[key] = "24"
                    elif inspection_text == "車検整備無":
                        data[key] = "0"
                    elif len(inspection_elements) >= 3:
                        year_month_text = inspection_elements[1].text + inspection_elements[2].text
                        # Use a regular expression to extract the year and month
                        match = re.match(r'(\d{4})\(R\d{2}\)年(\d{1,2})月', year_month_text)
                        if match:
                            year = int(match.group(1))
                            month = int(match.group(2))
                            # Calculate the difference in months
                            now = datetime.datetime.now()
                            diff = (year - now.year) * 12 + month - now.month
                            data[key] = str(diff)
                        else:
                            data[key] = year_month_text
                else:
                    data[key] = None
            elif key == 'repair':
                if element.text == 'なし':
                    data[key] = 0
                elif element.text == 'あり':
                    data[key] = 1
                else:
                    data[key] = element.text
            elif key in ['one_owner', 'record_book', 'new_car', 'no_smoke', 'registered', 'legally_imported',
                         'demo_car', 'rental_car', 'eco_car', 'camping', 'welfare']:
                # If the text is '◯', store 1, otherwise store 0.
                data[key] = '1' if element.text.strip() == '◯' else '0'
            elif key == 'region':
                # Split the text by the <br/> tag and save each part to the corresponding column.
                region_parts = element.decode_contents().split('<br/>')
                data['Prefecture'] = region_parts[0].strip() if len(region_parts) > 0 else None
                data['City'] = region_parts[1].strip() if len(region_parts) > 1 else None
            elif key == 'legal_maintenance':
                # Check if the text is "法定整備付", "法定整備無", or "法定整備別" and store 1, 0, or 2 accordingly.
                text = element.text.strip()
                if '法定整備付' in text:
                    data[key] = '1'
                elif '法定整備無' in text:
                    data[key] = '0'
                elif '法定整備別' in text:
                    data[key] = '2'
                else:
                    data[key] = None
            elif key == 'guarantee':
                # Check if the text contains "保証付" or "保証無", and "ディーラー保証" or "販売店保証".
                text = element.text.strip()
                if '保証付' in text:
                    data['guarantee_exists'] = '1'
                    if 'ディーラー保証' in text:
                        data['guarantee_type'] = '1'
                    elif '販売店保証' in text:
                        data['guarantee_type'] = '0'
                elif '保証無' in text:
                    data['guarantee_exists'] = '0'
                    data['guarantee_type'] = None
            elif key == 'point':
                # Extract the number from the text and store it.
                point_text = element.text.strip()
                point_number = re.search(r'\d+(\.\d+)?', point_text)
                data[key] = point_number.group() if point_number else '0'
            elif key == 'right_handle':
                if element.text == '右':
                    data[key] = '1'
                elif element.text == '左':
                    data[key] = '0'
                else:
                    data[key] = None
            elif key == 'displacement':
                data[key] = element.text.replace('cc', '')
            elif key == 'member':
                data[key] = element.text.replace('名', '')
            elif key == 'engine_type_gasoline':
                if element.text == 'ディーゼル':
                    data[key] = '0'
                elif element.text == 'ガソリン':
                    data[key] = '1'
                elif element.text == 'ハイブリッド':
                    data[key] = '2'
                else:
                    data[key] = element.text
            elif key in ['power_steering', 'abs', 'safety_support', 'auto_brake', 'adaptive_cruise', 'lane_keep',
                         'park_assist', 'accelerator_safe', 'obstacle_sensor', 'neck_rest', '360_camera',
                         'esp', 'hill_descent', 'idle_stop', 'anti_theft', 'auto_high_beam', 'turbo', 'ac_cool',
                         'double_ac', 'navi', 'tv', 'music_player_plugin', 'etc', 'air_sus', '1500w', 'drive_rec',
                         'disp_audio', 'cold_region', 'keyless', 'smart_key', 'power_window', 'backseat_monitor',
                         'bench_seat', '3rd_row', 'walk_through', 'power_seat', 'seat_ac', 'seat_heater',
                         'fullflat_seat', 'ottoman', 'leather_seat', 'front_fog', 'sunroof', 'roof_rail', 'full_aero',
                         'alumi_wheel', 'low_down', 'lift_up', 'slide_door', 'all_paint']:
                if element.has_attr('class') and 'equipmentList__item--active' in element['class']:
                    data[key] = '1'
                else:
                    data[key] = '0'
            elif key in ['air_bag', 'camera', 'monitor', 'audio_player', 'vid_player']:
                if element.has_attr('class') and 'equipmentList__item--active' in element['class']:
                    item_types = element.text.split('：')[1].split('/')
                    for item_type in item_types:
                        if item_type != '－':
                            data[key + '_' + item_type] = '1'
                    # Set the rest fields to '0'
                    for field in SUBFIELDS[key]:
                        full_key = key + '_' + field
                        if full_key not in data:
                            data[full_key] = '0'
                else:
                    for field in SUBFIELDS[key]:
                        data[key + '_' + field] = '0'
            elif key == 'halogen_headlight':
                if element.has_attr('class') and 'equipmentList__item--active' in element['class']:
                    data[key] = '1'
                    data['headlight_type'] = element.text.split('：')[1]
                else:
                    data[key] = '0'
                    data['headlight_type'] = 'Halogen'
            else:
                data[key] = element.text
        else:
            if key == 'point':
                data[key] = '0'
            else:
                data[key] = None
    data['url'] = url  # Add the detail page URL
    return data


CSS_SELECTORS = {
    # 基本情報
    'car_name': 'body > div.page > div:nth-child(5) > main > section > h2 > span',
    'base_price': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.priceWrap > div.basePrice > p.basePrice__price',
    'total_price': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.priceWrap > div.totalPrice > p.totalPrice__price',
    'model_year': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(1) > p.specWrap__box__num',
    'distance': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(2) > p.specWrap__box__num',
    'inspection_remaining_month': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(3)',
    'repair': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(4) > p:nth-child(2)',
    # 状態
    'recycle': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(6) > td:nth-child(2)',
    'one_owner': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)',
    'record_book': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)',
    'new_car': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(4) > td:nth-child(4)',
    'no_smoke': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(5) > td:nth-child(2)',
    'region': 'body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(5) > p:nth-child(2)',
    'registered': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(6) > td:nth-child(4)',
    'legally_imported': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(5) > td:nth-child(4)',
    'demo_car': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(7) > td:nth-child(2)',
    'rental_car': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(7) > td:nth-child(4)',
    'eco_car': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(8) > td',
    'legal_maintenance': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(10) > td > p',
    'guarantee': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(11) > td > p',
    'camping': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(2) > td:nth-child(4)',
    'welfare': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(3) > td:nth-child(4)',
    # 品質評価
    'point': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(4) > div > div.evaluationWrap--large > div > div:nth-child(2) > p',
    # 基本スペック
    'body_type': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)',
    'drive_type': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)',
    'color': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(2) > td:nth-child(2)',
    'right_handle': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(2) > td:nth-child(4)',
    'transmission': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(3) > td:nth-child(4)',
    'displacement': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)',
    'member': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(4) > td:nth-child(4)',
    'engine_type_gasoline': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(5) > td:nth-child(2)',
    'door_number': 'body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(5) > td:nth-child(4)',
    # 装備仕様
    # 安全装備
    'power_steering': '#equipmentList > div:nth-child(1) > ul > li:nth-child(1)',
    'abs': '#equipmentList > div:nth-child(1) > ul > li:nth-child(2)',
    'safety_support': '#equipmentList > div:nth-child(1) > ul > li:nth-child(3)',
    'auto_brake': '#equipmentList > div:nth-child(1) > ul > li:nth-child(4)',
    'adaptive_cruise': '#equipmentList > div:nth-child(1) > ul > li:nth-child(5)',
    'lane_keep': '#equipmentList > div:nth-child(1) > ul > li:nth-child(6)',
    'park_assist': '#equipmentList > div:nth-child(1) > ul > li:nth-child(7)',
    'accelerator_safe': '#equipmentList > div:nth-child(1) > ul > li:nth-child(8)',
    'obstacle_sensor': '#equipmentList > div:nth-child(1) > ul > li:nth-child(9)',
    'air_bag': '#equipmentList > div:nth-child(1) > ul > li:nth-child(10)',
    'air_bag_運転席': None,  # these keys will be handled in the 'air_bag' key
    'air_bag_助手席': None,
    'air_bag_サイド': None,
    'air_bag_カーテン': None,
    'neck_rest': '#equipmentList > div:nth-child(1) > ul > li:nth-child(11)',
    '360_camera': '#equipmentList > div:nth-child(1) > ul > li:nth-child(12)',
    'camera': '#equipmentList > div:nth-child(1) > ul > li:nth-child(13)',
    'camera_フロント': None,
    'camera_サイド': None,
    'camera_バック': None,
    'monitor': '#equipmentList > div:nth-child(1) > ul > li:nth-child(14)',
    'monitor_ブラインドスポット': None,
    'monitor_リアトラフィック': None,
    'esp': '#equipmentList > div:nth-child(1) > ul > li:nth-child(15)',
    'hill_descent': '#equipmentList > div:nth-child(1) > ul > li:nth-child(16)',
    'idle_stop': '#equipmentList > div:nth-child(1) > ul > li:nth-child(17)',
    'anti_theft': '#equipmentList > div:nth-child(1) > ul > li:nth-child(18)',
    'auto_high_beam': '#equipmentList > div:nth-child(1) > ul > li:nth-child(19)',
    # 快適装備
    'turbo': '#equipmentList > div:nth-child(2) > ul > li:nth-child(1)',
    'ac_cool': '#equipmentList > div:nth-child(2) > ul > li:nth-child(2)',
    'double_ac': '#equipmentList > div:nth-child(2) > ul > li:nth-child(3)',
    'navi': '#equipmentList > div:nth-child(2) > ul > li:nth-child(4)',
    'tv': '#equipmentList > div:nth-child(2) > ul > li:nth-child(5)',
    'vid_player': '#equipmentList > div:nth-child(2) > ul > li:nth-child(6)',
    'vid_player_DVD': None,
    'vid_player_ブルーレイ': None,
    'audio_player': '#equipmentList > div:nth-child(2) > ul > li:nth-child(7)',
    'audio_player_CD': None,
    'audio_player_MD': None,
    'audio_player_ミュージックサーバー': None,
    'music_player_plugin': '#equipmentList > div:nth-child(2) > ul > li:nth-child(8)',
    'etc': '#equipmentList > div:nth-child(2) > ul > li:nth-child(9)',
    'air_sus': '#equipmentList > div:nth-child(2) > ul > li:nth-child(10)',
    '1500w': '#equipmentList > div:nth-child(2) > ul > li:nth-child(11)',
    'drive_rec': '#equipmentList > div:nth-child(2) > ul > li:nth-child(12)',
    'disp_audio': '#equipmentList > div:nth-child(2) > ul > li:nth-child(13)',
    'cold_region': '#equipmentList > div:nth-child(2) > ul > li:nth-child(14)',
    # インテリア
    'keyless': '#equipmentList > div:nth-child(3) > ul > li:nth-child(1)',
    'smart_key': '#equipmentList > div:nth-child(3) > ul > li:nth-child(2)',
    'power_window': '#equipmentList > div:nth-child(3) > ul > li:nth-child(3)',
    'backseat_monitor': '#equipmentList > div:nth-child(3) > ul > li:nth-child(4)',
    'bench_seat': '#equipmentList > div:nth-child(3) > ul > li:nth-child(5)',
    '3rd_row': '#equipmentList > div:nth-child(3) > ul > li:nth-child(6)',
    'walk_through': '#equipmentList > div:nth-child(3) > ul > li:nth-child(7)',
    'power_seat': '#equipmentList > div:nth-child(3) > ul > li:nth-child(8)',
    'seat_ac': '#equipmentList > div:nth-child(3) > ul > li:nth-child(9)',
    'seat_heater': '#equipmentList > div:nth-child(3) > ul > li:nth-child(10)',
    'fullflat_seat': '#equipmentList > div:nth-child(3) > ul > li:nth-child(11)',
    'ottoman': '#equipmentList > div:nth-child(3) > ul > li:nth-child(12)',
    'leather_seat': '#equipmentList > div:nth-child(3) > ul > li:nth-child(13)',
    # エクステリア
    'halogen_headlight': '#equipmentList > div:nth-child(4) > ul > li:nth-child(1)',
    'headlight_type': None,
    'front_fog': '#equipmentList > div:nth-child(4) > ul > li:nth-child(2)',
    'sunroof': '#equipmentList > div:nth-child(4) > ul > li:nth-child(3)',
    'roof_rail': '#equipmentList > div:nth-child(4) > ul > li:nth-child(4)',
    'full_aero': '#equipmentList > div:nth-child(4) > ul > li:nth-child(5)',
    'alumi_wheel': '#equipmentList > div:nth-child(4) > ul > li:nth-child(6)',
    'low_down': '#equipmentList > div:nth-child(4) > ul > li:nth-child(7)',
    'lift_up': '#equipmentList > div:nth-child(4) > ul > li:nth-child(8)',
    'slide_door': '#equipmentList > div:nth-child(4) > ul > li:nth-child(9)',
    'all_paint': '#equipmentList > div:nth-child(4) > ul > li:nth-child(10)',
}

SUBFIELDS = {
    'air_bag': ['運転席', '助手席', 'サイド', 'カーテン'],
    'camera': ['フロント', 'サイド', 'バック'],
    'monitor': ['ブラインドスポット', 'リアトラフィック'],
    'audio_player': ['CD', 'MD', 'ミュージックサーバー'],
    'vid_player': ['DVD', 'ブルーレイ']
}


def save_data(data, filename):
    fieldnames = [key for key in CSS_SELECTORS.keys() if key not in ['region', 'guarantee']]
    fieldnames += ['Prefecture', 'City', 'guarantee_exists', 'guarantee_type', 'url']
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # write header only once
        writer.writerow(data)


def main():
    url = YOUR_URL
    html = get_html(url)
    soup = parse_html(html)
    last_page_num = get_last_page_num(soup)
    detail_page_counter = 0  # Initialize the counter

    for page_num in range(1, last_page_num + 1):
        detail_page_urls = get_detail_page_urls(soup)
        while detail_page_urls:  # 如果还有更多的详情页
            detail_page_url = detail_page_urls.pop(0)  # 取出第一个详情页的 URL
            html = get_html(detail_page_url)
            detail_soup = parse_html(html)  # 创建一个新的 BeautifulSoup 对象来处理详情页
            data = extract_data(detail_soup, detail_page_url)
            save_data(data, 'data.csv')
            detail_page_counter += 1
            print(f'Scraped {detail_page_counter} detail pages: {detail_page_url}')  # Print the counter and the URL

        url = get_next_page_url(soup, page_num)
        print(url)
        if url is not None:
            html = get_html(url)
            soup = parse_html(html)  # 更新 soup 对象以指向新的搜索结果页

        # time.sleep(0.25)


if __name__ == '__main__':
    main()
