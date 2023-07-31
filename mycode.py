from bs4 import BeautifulSoup
import requests
import re
import datetime
import csv


url = 'https://www.carsensor.net/usedcar/detail/AU3403073652/index.html?TRCD=200002&RESTID=CS210610&LOAN=ZNK'
response = requests.get(url)
html_content = response.content.decode('utf-8')

soup = BeautifulSoup(html_content, 'html.parser')

CSS_CHECK = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(3)')
print(CSS_CHECK)


# 一覧ページのページ数を取得するCSS selector
'''
CSS_LAST_PAGE_NUM = soup.select('#js-resultBar > div.resultBar__link > div > div.pager__text > a:nth-child(12)')[0]

def extract_number_from_href(href):
    match = re.search(r'index(\d+)', href)
    if match:
        return match.group(1)
    else:
        return None

# 调用函数并传入 href
href = CSS_LAST_PAGE_NUM['href']
last_page_num = extract_number_from_href(href)

# 打印提取到的数字
print(last_page_num)

'''
#AU2832583163_cas > div.cassetteMain > div > div.cassetteMain__carInfoContainer > h3 > a
#AU3193278737_cas > div.cassetteMain > div > div.cassetteMain__carInfoContainer > h3 > a


#基本情報
CSS_BASE_PRICE = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.priceWrap > div.basePrice > p.basePrice__price')
CSS_TOTAL_PRICE = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.priceWrap > div.totalPrice > p.totalPrice__price')
CSS_MODEL_YEAR = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(1) > p.specWrap__box__num')
CSS_DISTANCE = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(2) > p.specWrap__box__num')
CSS_INSPECTION = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(3)')
CSS_REPAIR = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(4) > p:nth-child(2)')

#状態
#CSS_CAR_INFO = 'body > div.page > div:nth-child(6) > main > section > h2 > span'
#CSS_DRIVE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(5) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)'
CSS_RECYCLE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(6) > td:nth-child(2)')
CSS_ONE_OWNER = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)')
CSS_RECORD_BOOK = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)')
CSS_NEW_CAR = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(4) > td:nth-child(4)')
CSS_NO_SMOKE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(5) > td:nth-child(2)')
CSS_REGION = soup.select('body > div.page > div:nth-child(5) > main > section > div > div.column__sub > div.specWrap > div:nth-child(5) > p:nth-child(2)')
CSS_REGISTERED = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(6) > td:nth-child(4)')
CSS_LEGAL_IMPORTED = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(5) > td:nth-child(4)')
CSS_DEMO_CAR = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(7) > td:nth-child(2)')
CSS_RENTAL_CAR = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(7) > td:nth-child(4)')
CSS_ECO_CAR = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(8) > td')
CSS_LEGAL_MAINTENANCE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(10) > td > p')
CSS_WARRANTY = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(11) > td > p')
CSS_CAMPING = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(2) > td:nth-child(4)')
CSS_WELFARE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(3) > td:nth-child(4)')

#品質評価
CSS_POINT = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(4) > div > div.evaluationWrap--large > div > div:nth-child(2) > p')

#基本スペック
CSS_BODY_TYPE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(1) > td:nth-child(2)')
CSS_DRIVE_TYPE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)')
CSS_COLOR = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(2) > td:nth-child(2)')
CSS_HANDLE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(2) > td:nth-child(4)')
CSS_TRANSMISSION = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(3) > td:nth-child(4)')
CSS_DISPLACEMENT = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)')
CSS_MEMBER = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(4) > td:nth-child(4)')
CSS_ENGINE_TYPE = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(5) > td:nth-child(2)')
CSS_DOOR_NUMBER = soup.select('body > div.page > div:nth-child(7) > div > div.column__main > section:nth-child(6) > div > table > tbody > tr:nth-child(5) > td:nth-child(4)')

#装備仕様
#安全装備
CSS_POWER_STEERING = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(1)')
CSS_ABS = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(2)')
CSS_SAFETY_SUPPORT = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(3)')
CSS_AUTO_BRAKE = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(4)')
CSS_ADAPTIVE_CRUISE = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(5)')
CSS_LANE_KEEP = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(6)')
CSS_PARK_ASSIST = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(7)')
CSS_ACCELERATOR_SAFE = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(8)')
CSS_OBSTACLE_SENSOR = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(9)')
CSS_AIR_BAG = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(10)')
CSS_NECK_REST = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(11)')
CSS_360_CAMERA = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(12)')
CSS_CAMERA = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(13)')
CSS_MONITOR = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(14)')
CSS_ESP = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(15)')
CSS_HILL_DESCENT = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(16)')
CSS_IDLE_STOP = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(17)')
CSS_ANTI_THEFT = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(18)')
CSS_AUTO_HIGHBEAM = soup.select('#equipmentList > div:nth-child(1) > ul > li:nth-child(19)')

#快適装備
CSS_TURBO = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(1)')
CSS_AC_COOL = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(2)')
CSS_DOUBLE_AC = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(3)')
CSS_NAVI = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(4)')
CSS_TV = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(5)')
CSS_VID_PLAYER = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(6)')
CSS_AUDIO_PLAYER = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(7)')
CSS_MUSIC_PLAYER = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(8)')
CSS_ETC = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(9)')
CSS_AIR_SUS = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(10)')
CSS_1500W = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(11)')
CSS_DRIVE_REC = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(12)')
CSS_DISP_AUDIO = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(13)')
CSS_COLD_REGION = soup.select('#equipmentList > div:nth-child(2) > ul > li:nth-child(14)')

#インテリア
CSS_KEYLESS = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(1)')
CSS_SMART_KEY = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(2)')
CSS_POWER_WINDOW = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(3)')
CSS_BACKSEAT_MONITOR = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(4)')
CSS_BENCH_SEAT = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(5)')
CSS_3RD_ROW = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(6)')
CSS_WALK_THROUGH = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(7)')
CSS_POWER_SEAT = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(8)')
CSS_SEAT_AC = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(9)')
CSS_SEAT_HEATER = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(10)')
CSS_FULLFLAT_SEAT = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(11)')
CSS_OTTOMAN = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(12)')
CSS_LEATHER_SEAT = soup.select('#equipmentList > div:nth-child(3) > ul > li:nth-child(13)')

#エクステリア
CSS_HEADLIGHT = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(1)')
CSS_FRONT_FOG = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(2)')
CSS_SUNROOF = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(3)')
CSS_ROOF_RAIL = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(4)')
CSS_FULL_AERO = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(5)')
CSS_ALUMI_WHEEL = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(6)')
CSS_LOW_DOWN = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(7)')
CSS_LIFT_UP = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(8)')
CSS_SLIDE_DOOR = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(9)')
CSS_ALL_PAINT = soup.select('#equipmentList > div:nth-child(4) > ul > li:nth-child(10)')

# 可以通过selectors_result字典中的键来访问对应的选择器结果


# 詳細ページのURL　CSS selector
#CSS_DETAIL_PAGE_URL = '#carList h3[class="casetMedia__body__title"] > a'

# オプション CSS selector
#CSS_KEYLESS = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(5)'
#CSS_SMARTKEY = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(6)'
#CSS_NAVI = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(7)'
#CSS_TV = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(8)'
#CSS_VIDEO = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(9)'
#CSS_AUDIO = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(10)'
#CSS_PLAYER = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(11)'
#CSS_MONITOR = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(12)'
#CSS_ETC = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(13)'
#CSS_SHEAT_AIR = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(18)'
#CSS_SHEAT_HEATER = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(19)'
#CSS_LEATHER_SHEAT = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(22)'
#CSS_IDLINGSTOP = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(23)'
#CSS_AS_SENSOR = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(24)'
#CSS_CRUISE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(25)'
#CSS_ABS = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(26)'
#CSS_ESC = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(27)'
#CSS_ANTI_THEFT = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(28)'
#CSS_AUTO_BRAKE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(29)'
#CSS_PARKING_ASSIST = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(30)'
#CSS_AIRBAG = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(31)'
#CSS_HEADLIGHT = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(32)'
#CSS_CAMERA = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(33)'
#CSS_AROUND_CAMERA = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(34)'
#CSS_AERO = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(37)'
#CSS_ALUMI_WHEEL = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(38)'
#CSS_LOWDOWN = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(39)'
#CSS_LIFTUP = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(40)'
#CSS_COLD_AREA = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(41)'

print(CSS_LAST_PAGE_NUM)

print(CSS_MODEL_YEAR[0])
for element in CSS_INSPECTION:
    text = element.text
    print(text)
