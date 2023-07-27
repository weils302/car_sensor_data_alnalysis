import lxml.html
import requests
import re
from pymongo import MongoClient
import time
import argparse

# MongoDBの参照するデータベース名
DB_NAME = 'CARSENSOR'

# 車両基本情報のCSS selector
CSS_BODY_PRICE = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.priceWrap > div.basePrice > p.basePrice__price'
CSS_TOTAL_PRICE = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.priceWrap > div.totalPrice > p.totalPrice__price'
CSS_MODEL_YEAR = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.specWrap > div:nth-child(1) > p.specWrap__box__num'
CSS_DISTANCE = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.specWrap > div:nth-child(2)'
CSS_INSPECTION = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.specWrap > div:nth-child(3)'
CSS_REPARE = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.specWrap > div:nth-child(4) > p:nth-child(2)'
CSS_CAR_INFO = 'body > div.page > div:nth-child(6) > main > section > h2 > span'
CSS_DRIVE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(5) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)'
CSS_RECYCLE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(6) > td:nth-child(2)'
CSS_LEGAL_MAINTENANCE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(9) > td > p'
CSS_WARRANTY = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(10) > td > p'
CSS_ONE_OWNER = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child(4)'
CSS_RECORD_BOOK = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(4) > td:nth-child(2)'
CSS_NO_SMOKE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(2) > div > table > tbody > tr:nth-child(5) > td:nth-child(2)'
CSS_REGION = 'body > div.page > div:nth-child(6) > main > section > div > div.column__sub > div.specWrap > div:nth-child(5) > p:nth-child(2)'

# 一覧ページのページ数を取得するCSS selector
CSS_LAST_PAGE_NUM = '#js-resultBar > div.resultBar__link > div > div.pager__text > a:nth-child(12)'
# 詳細ページのURL　CSS selector
CSS_DETAIL_PAGE_URL = '#carList h3[class="casetMedia__body__title"] > a'

# オプション CSS selector
CSS_KEYLESS = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(5)'
CSS_SMARTKEY = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(6)'
CSS_NAVI = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(7)'
CSS_TV = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(8)'
CSS_VIDEO = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(9)'
CSS_AUDIO = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(10)'
CSS_PLAYER = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(11)'
CSS_MONITOR = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(12)'
CSS_ETC = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(13)'
CSS_SHEAT_AIR = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(18)'
CSS_SHEAT_HEATER = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(19)'
CSS_LEATHER_SHEAT = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(22)'
CSS_IDLINGSTOP = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(23)'
CSS_AS_SENSOR = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(24)'
CSS_CRUISE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(25)'
CSS_ABS = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(26)'
CSS_ESC = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(27)'
CSS_ANTI_THEFT = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(28)'
CSS_AUTO_BRAKE = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(29)'
CSS_PARKING_ASSIST = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(30)'
CSS_AIRBAG = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(31)'
CSS_HEADLIGHT = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(32)'
CSS_CAMERA = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(33)'
CSS_AROUND_CAMERA = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(34)'
CSS_AERO = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(37)'
CSS_ALUMI_WHEEL = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(38)'
CSS_LOWDOWN = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(39)'
CSS_LIFTUP = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(40)'
CSS_COLD_AREA = 'body > div.page > div:nth-child(8) > div > div.column__main > section:nth-child(6) > div > ul > li:nth-child(41)'


# EMスペース、ノーブレークスペースの符号
EM_SPACE = '\u3000'
NBSP = '\xa0'

URL_DICT = {
    "VEZEL": 'https://www.carsensor.net/usedcar/bHO/s101/index.html',
    'FIT': 'https://www.carsensor.net/usedcar/bHO/s028/index.html',
    'PRIUS': 'https://www.carsensor.net/usedcar/bTO/s122/index.html'
}


def main(args):
    URL = URL_DICT[args.car_type]
    total_list_num = get_lastpage_num(URL)

    client = MongoClient()
    db = client[DB_NAME]
    collection = db[args.car_type]
    if args.reset_db:
        print("reset DB collection:", args.car_type)
        collection.delete_many({})

    for i in range(1, total_list_num + 1):
        listpage_url = URL.replace('index', 'index' + str(i))
        urls = scrape_list_page(listpage_url)
        collect_insert(urls, collection)
        print(listpage_url, ' done')


def collect_insert(urls, collection):
    """
    指定したリストページ内の詳細ページをスクレイピングし、DBに格納
    input:
        - urls: generator object, 詳細ページのurlを生成するgenerator
        - collection: mongodb collection object
    output: None
    """
    for url in urls:
        key = extract_key(url)
        key_check = collection.find_one({'key': key})
        if not key_check:
            print('add ', key)
            usedcar = scrape_detail_page(url, key)
            collection.insert_one(usedcar)
            time.sleep(1)


def get_lastpage_num(url):
    """
    リストページのhtmlからリストページの総数を取得して返す
    intput:
        - url: str
    output:
        - last_num: int, リストページ数
    """
    response = requests.get(url)
    root = lxml.html.fromstring(response.content)
    # 最後のlistページのurlを取得する
    last_page = root.cssselect(CSS_LAST_PAGE_NUM)[0]
    # urlから最後のindex番号を取得する
    last_index = last_page.get('href').split("/")[-1]
    m = re.search('index([0-9]+)', last_index)
    # re.search()でマッチしなかった場合のエラー処理
    if m is None:
        raise ValueError('index.html of last page is not found')
    last_num = int(m.group(1))
    return last_num


def scrape_list_page(url):
    """
    リストページから詳細ページのurlを取得し、生成する(generator object)
    input:
        - url: str, リストページのurl
    output:
        generator object, 詳細ページのurlを生成する
    """
    # webページ読み込み、response.contentから文字列を取得してパース
    response = requests.get(url)
    root = lxml.html.fromstring(response.content)
    # 全てのurlを絶対urlに変換
    root.make_links_absolute(response.url)
    htmlElems = root.cssselect(CSS_DETAIL_PAGE_URL)
    for elem in htmlElems:
        url = elem.get('href')
        yield url


def scrape_detail_page(url, key):
    """
    詳細ページから各種情報を取得し、dictで返す
    input:
        - url: str, 詳細ページのurl
        - key: str, 詳細ページのurlに対するキー
    output:
        - usedcar: dict, dbに格納するドキュメント
    """
    true_mark = "◯"

    response = requests.get(url)
    root = lxml.html.fromstring(response.content)

    # 本体価格---------------------------------------------------------------
    base_price = root.cssselect(CSS_BODY_PRICE)
    base_price = base_price[0].get('content').replace(',', '')
    base_price = int(base_price)
    # 本体価格応相談の場合はNullにする
    if base_price > 90000000:
        base_price = None
    # 支払総額---------------------------------------------------------------
    total_price = root.cssselect(CSS_TOTAL_PRICE)
    total_price = total_price[0].text_content()
    total_price = re.sub(r'\n(\t)+', '', total_price).replace('万円', '')
    try:
        total_price = int(float(total_price) * 10000)
    except ValueError:
        total_price = None
    # 年式---------------------------------------------------------------
    model_year = root.cssselect(CSS_MODEL_YEAR)
    model_year = model_year[0].text
    model_year = int(model_year)
    # 走行距離---------------------------------------------------------------
    distance = root.cssselect(CSS_DISTANCE)
    distance = distance[0].text_content()
    distance = re.sub(r'\n(\t)+', '', distance).strip().replace('走行距離', '')
    if '万' in distance:
        distance = distance.replace('万km', '')
        try:
            distance = float(distance)
        except ValueError:
            distance = None
    else:
        distance = distance.replace('km', '')
        try:
            distance = float(distance) / 10000
        except ValueError:
            distance = None
    # 車検---------------------------------------------------------------
    inspection = root.cssselect(CSS_INSPECTION)
    inspection = inspection[0].text_content()
    inspection = re.sub(r'\n(\t)+', '', inspection).replace('車検有無', '')
    # 修復歴---------------------------------------------------------------
    repare = root.cssselect(CSS_REPARE)
    repare = repare[0].text
    # 本体情報等---------------------------------------------------------------
    info = root.cssselect(CSS_CAR_INFO)
    info = info[0].text
    info = info.replace(EM_SPACE, ' ').replace(NBSP, ' ')
    # 駆動方式----------------------------------------------------------------
    try:
        drive = root.cssselect(CSS_DRIVE)
        drive = drive[0].text
    except IndexError:
        css_drive_tmp = CSS_DRIVE.replace(
            'section:nth-child(5)', 'section:nth-child(4)'
        )
        drive = root.cssselect(css_drive_tmp)
        drive = drive[0].text
    # リサイクル料-------------------------------------------------------------
    recycle = root.cssselect(CSS_RECYCLE)
    recycle = recycle[0].text
    # 法定整備---------------------------------------------------------------
    legal_maintenance = root.cssselect(CSS_LEGAL_MAINTENANCE)
    legal_maintenance = legal_maintenance[0].text
    # 保証---------------------------------------------------------------
    warranty = root.cssselect(CSS_WARRANTY)
    warranty = warranty[0].text
    warranty = warranty.replace(EM_SPACE, ' ')
    # ワンオーナー------------------------------------------------------------
    one_owner = root.cssselect(CSS_ONE_OWNER)
    one_owner = one_owner[0].text
    if one_owner == true_mark:
        one_owner = 1
    else:
        one_owner = 0
    # 定期点検記録簿-----------------------------------------------------------
    record_book = root.cssselect(CSS_RECORD_BOOK)
    record_book = record_book[0].text
    if record_book == true_mark:
        record_book = 1
    else:
        record_book = 0
    # 禁煙車---------------------------------------------------------------
    no_smoke = root.cssselect(CSS_NO_SMOKE)
    no_smoke = no_smoke[0].text
    if no_smoke == true_mark:
        no_smoke = 1
    else:
        no_smoke = 0
    # 地域-----------------------------------------------------------------
    region = root.cssselect(CSS_REGION)
    region = region[0].text

    usedcar = {
        'url': response.url,
        'base_price': base_price,
        'total_price': total_price,
        'model_year': model_year,
        'distance': distance,
        'repare': repare,
        'inspection': inspection,
        'info': normalize_spaces(info),
        'drive': drive,
        'recycle': recycle,
        'legal_maintenance': legal_maintenance,
        'warranty': warranty,
        'one_owner': one_owner,
        'record_book': record_book,
        'no_smoke': no_smoke,
        'key': key,
        'region': region
    }

    # オプション情報を取得してusedcarに追加
    options = get_options_state(root)
    usedcar.update(options)
    return usedcar


def get_options_state(root):
    """
    車両のオプション情報を取得する
    input:
        - root: lxml.html.
    """
    # オプション一覧を辞書にまとめる
    options = {
        'keyless': CSS_KEYLESS,
        'smartkey': CSS_SMARTKEY,
        'navi': CSS_NAVI,
        'TV': CSS_TV,
        'video': CSS_VIDEO,
        'audio': CSS_AUDIO,
        'player': CSS_PLAYER,
        'monitor': CSS_MONITOR,
        'ETC': CSS_ETC,
        'sheat_air': CSS_SHEAT_AIR,
        'sheat_heater': CSS_SHEAT_HEATER,
        'idling_stop': CSS_IDLINGSTOP,
        'AS_sensor': CSS_AS_SENSOR,
        'cruise': CSS_CRUISE,
        'ABS': CSS_ABS,
        'ESC': CSS_ESC,
        'anti_theft': CSS_ANTI_THEFT,
        'auto_brake': CSS_AUTO_BRAKE,
        'parking_assist': CSS_PARKING_ASSIST,
        'airbag': CSS_AIRBAG,
        'headlight': CSS_HEADLIGHT,
        'camera': CSS_CAMERA,
        'around_camera': CSS_AROUND_CAMERA,
        'aero': CSS_AERO,
        'alumi_wheel': CSS_ALUMI_WHEEL,
        'lowdown': CSS_LOWDOWN,
        'liftup': CSS_LIFTUP,
        'cold_area': CSS_COLD_AREA
    }
    result = {}
    for key, option in options.items():
        htmlElems = root.cssselect(option)
        if len(htmlElems) == 0:
            option = option.replace(
                'section:nth-child(6)', 'section:nth-child(7)'
            )
            htmlElems = root.cssselect(option)
        if len(htmlElems) == 0:
            option = option.replace(
                'section:nth-child(7)', 'section:nth-child(5)'
            )
            htmlElems = root.cssselect(option)
        result[key] = get_option_value(key, htmlElems)
    return result


def get_option_value(key, elem):
    """
    option辞書に入れるvalue値を取得する
    input:
        - key: str, オプション名
        - elem: 詳細ページのlxml.html.HTMLElemオブジェクト
    output:
        - value: int or str, option辞書のkeyに対するvalue
    """
    class_id = elem[0].attrib['class']
    if 'active' in class_id:
        text = elem[0].text
        if key in ['navi', 'video', 'audio', 'airbag', 'camera']:
            value = text.split('：')[-1]
        elif key == 'TV':
            if 'フルセグ' in text:
                value = 'フルセグ'
            else:
                value = 'ワンセグ'
        elif key == "headlight":
            if 'ディスチャージ' in text:
                value = 'ディスチャージドランプ'
            else:
                value = 'LED'
        else:
            value = 1
    else:
        value = 0
    return value


def normalize_spaces(s):
    """
    文字列内の連続する空白を一つにし、前後の空白を削除する
    input:
        - s: str
    output: str
    """
    return re.sub(r'\s+', ' ', s).strip()


def extract_key(url):
    """
    詳細ページのurlからキーを取得し、返す
    input:
        - url: str, 詳細ページのurl
    output: str
    """
    key = url.split('/')[-2]
    if not key.startswith('CU'):
        raise ValueError('key extract error, detail url is wrong')
    return key


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('car_type', type=str)
    parser.add_argument('--reset_db', action='store_true')
    args = parser.parse_args()
    main(args)
