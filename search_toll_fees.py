#入口,出口
#妙高高原,茂原長南
#佐賀大和,豊前
#岩槻,加須
#所沢,岩槻
#岩槻,相模原

# Import library
# ライブラリーをインポートする
import pandas as pd
import datetime
import time, csv, itertools
from functools import reduce
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# This is the URL used to search for the toll fees.
# このURLで高速料金を探す
options = Options()
options.add_argument('--headless')
url = "http://search.w-nexco.co.jp/route.php"

# This will read the csv file of the list and delete the empty rows with no IC name available.
# CSVファイルを読み込み、空セルを削除。CSVファイル名を入力してください。そのファイルはこのノートと一緒に同じファイルに入れてください。
#read CSV
print("""
CSVファイル名を入力します。このファイルはこのプログラムと一緒に同じファイルに入れていると確認してください。
""")
input_file = input("検索入力のCSVファイルを入力してください（例:ryokin.csv)： ")
df = pd.read_csv(input_file)
df_edit = df.dropna(subset=['入口','出口'])

print("""
検索日時を入力してください。
検索日付...
""")
in_yr, in_mth, in_day = input("日付（例：2018/9/3）： ").split("/")
in_week = datetime.datetime(int(in_yr),int(in_mth),int(in_day)).weekday()
if in_week == 6:
    date_val = ("day_{}_{}_{}_{}_0".format(in_yr, in_mth, in_day,in_week-6))
else:
    date_val = ("day_{}_{}_{}_{}_0".format(in_yr, in_mth, in_day,in_week+1))
print("""
検索時間...
    """)
input_hr = input("時（0から23までだけ入力してください）：")
input_min = input("分（10分毎で00の場合は0だけ入力してください）： ")
# Run the whole program and iterate through each row. A time.sleep is put to add time for response. Prevent from being recognized as bot
# プログラムを実行。全車種を検索する。

#new session
#create list
class FeeList(object):
    def __init__(self):
        self.buttonlist = []

#class for finding all fees
class AllToll(FeeList):
    def __init__(self, cartype_val):
        FeeList.__init__(self)
        self.cartype_val = cartype_val

    def fin_toll(self, cartype_val):
        return print("車種区分 : {}　検索終了".format(cartype_val))

    def get_toll(self, cartype_val):
        for index, row in df_edit.iterrows():
            try:
                #open the browser and navigate to the page
                #ブラウザ開いてURLに接続
                driver = webdriver.Chrome(chrome_options=options)
                driver.get(url)
            
                in_keys = row['入口']
                out_keys = row['出口']

                #fill in the form
                #検索フォーム入力
                driver.find_element_by_id("calImgDiv").click()
                driver.find_element_by_id(date_val).click() #日付設定　#set date (2018/8/6)
                select_hour = Select(driver.find_element_by_id("sl_hour_id")).select_by_value(input_hr) #時間設定　#set time
                select_min = Select(driver.find_element_by_id("sl_min_id")).select_by_value(input_min)
                in_field = driver.find_element_by_name("fnm") #出発IC
                in_field.send_keys(in_keys)
                time.sleep(1)
                in_path = ('//*[@class="sg_list_element_ic" and (text() = "{}")]'.format(in_keys))
                ActionChains(driver).move_to_element(in_field).click(driver.find_element_by_xpath(in_path)).perform()
                out_field = driver.find_element_by_name("tnm") #到着IC
                out_field.send_keys(out_keys)
                time.sleep(1)
                out_path = ('//*[@class="sg_list_element_ic" and (text() ="{}")]'.format(out_keys))
                ActionChains(driver).move_to_element(out_field).click(driver.find_element_by_xpath(out_path)).perform()
                select_car_type = Select(driver.find_element_by_name("cartyp")).select_by_value(cartype_val) #車種区分
                #通らない道路　（二つしかセットできない）
                #set detour (only 2 can be set)
                #"G1110"- C3 外環道, "G6000"-首都高速
                select_detour1 = Select(driver.find_element_by_id("detour1_id")).select_by_value("G1110")
                select_detour2 = Select(driver.find_element_by_id("detour2_id")).select_by_value("G6000")
                #検索する
                driver.find_element_by_css_selector(".submit-btn").send_keys("\n")

                #wait for page to load and click ETC料金順
                #ページを待つとETC料金順をクリック
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "pritab9")))
                driver.find_element_by_id("pritab9").click()
                #wait for page to load and get the toll fee
                #ページを待つとデータを取る
                time.sleep(2)
                #出発IC名と到着IC名
                start = driver.find_element_by_css_selector("span.start").get_attribute("innerText")
                goal = driver.find_element_by_css_selector("span.goal").get_attribute("innerText")
                #通常(現金), ETC, ETC2.0
                normal_toll = driver.find_element_by_css_selector("span.toll-normal").get_attribute("innerText")
                etc_toll = driver.find_element_by_css_selector("span.toll-etc").get_attribute("innerText")
                etc2_toll = driver.find_element_by_css_selector("span.toll-etc2").get_attribute("innerText")
                #他の料金検索
                def box_toll(box_no):
                    if box_no == 1:
                        box_path = '//*[@class="etc-info pc-stay pos-etc_box"]/div[2]/div'
                    else:
                        box_path = '//*[@class="etc-info pc-stay pos-etc2_box"]/div[2]/div'
                    box_toll = driver.find_element_by_xpath(box_path)
                    dt_box = box_toll.find_elements_by_tag_name("dt")
                    dd_box = box_toll.find_elements_by_tag_name("dd")
                    box_desc = []
                    box_val = []
                    for dt in dt_box:
                        test_d = dt.get_attribute("innerText")
                        box_desc.append(test_d)
                    for dd in dd_box:
                        test_v = dd.get_attribute("innerText")
                        box_val.append(test_v)
                    for i in box_desc:
                        if "平日" in i:
                            box_desc.remove(i)
                    for j in box_val:
                        if "還元率" in j:
                            box_val.remove(j)
                    box_val = list(filter(None, box_val))
                    full_box = dict(zip(box_desc, box_val))

                    return  full_box

                get_box1_toll = box_toll(1)
                get_box2_toll = box_toll(2)

                #close browser and session
                #ブラウザを閉じる
                driver.quit()
                
                dict_kyu = "休日（終日）"
                dict_shya = "深夜（0-4時）"
                dict_etc30p = "還元率30%\xa0/\xa05～9回"
                dict_etc50p = "還元率50%\xa0/\xa010回以上"

                #collected toll fess is put inside the list and made into list of list
                #取ったデータをリストに入れる
                toll = {'入口' : start, '出口' : goal, 
                        '通常(現金)' : normal_toll, 'ETC' : etc_toll, 'ETC2.0' : etc2_toll,
                        '休日' : get_box1_toll.get(dict_kyu, "0"), '深夜' : get_box1_toll.get(dict_shya, "0"), 
                        '還元率30%(ETC)' : get_box1_toll.get(dict_etc30p, "0"), '還元率50%(ETC)' : get_box1_toll.get(dict_etc50p, "0"),
                        '還元率30%(ETC2.0)' :get_box2_toll.get(dict_etc30p, "0") , '還元率50%(ETC2.0)' : get_box2_toll.get(dict_etc50p, "0")}
                self.buttonlist.append(toll.copy())
                #wait time before next session
                #次のセッションをスタートする待つ時間
                time.sleep(3)
            except NoSuchElementException as exception:
                driver.quit()
                pass
        return self.buttonlist
    
print("""
    検索中... [車種区分　: (1-軽・自動二輪, 2-普通車, 3-中型車, 4-大型車, 5-特大車)]
""")
#車種区分
#Type of car: ("1"-軽・自動二輪, "2"-普通車, "3"-中型車, "4"-大型車, "5"- 特大車)
#車種ごとにPython機能で実行
kei = AllToll("1").get_toll("1")
kei_fin = AllToll("1").fin_toll("1")
normal = AllToll("2").get_toll("2")
norm_fin = AllToll("2").fin_toll("2")
chugata = AllToll("3").get_toll("3")
chu_fin = AllToll("3").fin_toll("3")
ogata = AllToll("4").get_toll("4")
ogata_fin = AllToll("4").fin_toll("4")
toku = AllToll("5").get_toll("5")
toku_fin = AllToll("5").fin_toll("5")


# Change list into Pandas DataFrame. Make another dataframe to exclude all unrelated symbols (円,分, etc.)
# リストをPandasデータフレームに変更。もう一つのデータフレームを作り要らない記号を削除。
# すべての上記プログラムを作動しましたら、下記プログラムを作動することができます。
print("""
    データを編集中...
""")

#header for dataframe
#データのヘッダー
def edit_to_pandas(cartype):
    frame = pd.DataFrame(cartype)
    frame = frame[['入口', '出口', '通常(現金)', 'ETC', 'ETC2.0','休日', '深夜', 
                   '還元率30%(ETC)', '還元率50%(ETC)','還元率30%(ETC2.0)', '還元率50%(ETC2.0)']]
    return frame

def edit_to_int(cartype):
    return cartype[cartype.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)

def compile_toll(tolltype):
    return pd.concat([pd_kei['入口'], pd_kei['出口'],
                     all_kei[tolltype],all_normal[tolltype],
                     all_chugata[tolltype],all_ogata[tolltype],all_toku[tolltype]], axis=1,
                     keys=['入口', '出口', tolltype + '_軽自動車', tolltype + '_普通車',
                           tolltype + '_中型車', tolltype + '_大型車', tolltype + '_特大車'])

def compare_toll():
    edit_pd_kei = pd_kei[['入口','出口']]
    compare_both = edit_pd_kei.merge(df_edit, indicator=True, how='outer')
    diff_ic = compare_both[compare_both['_merge'] == 'right_only']
    return diff_ic[['入口','出口']]

#Pandas
pd_kei = edit_to_pandas(kei)
pd_normal = edit_to_pandas(normal)
pd_chugata = edit_to_pandas(chugata)
pd_ogata = edit_to_pandas(ogata)
pd_toku = edit_to_pandas(toku)

#change data to int
all_kei = edit_to_int(pd_kei)
all_normal = edit_to_int(pd_normal)
all_chugata = edit_to_int(pd_chugata)
all_ogata = edit_to_int(pd_ogata)
all_toku = edit_to_int(pd_toku)

# Compile all the fees based on the fee type (cash, ETC, ETC2.0 and others)
# 料金は種類ごとに編集
fin_gen = compile_toll('通常(現金)')
fin_etc = compile_toll('ETC')
fin_etc2 = compile_toll('ETC2.0')
fin_kyu = compile_toll('休日')
fin_shya = compile_toll('深夜')
fin_etc30p = compile_toll('還元率30%(ETC)')
fin_etc50p = compile_toll('還元率50%(ETC)')
fin_2etc30p = compile_toll('還元率30%(ETC2.0)')
fin_2etc50p = compile_toll('還元率50%(ETC2.0)')

# Compile all data into one sheet
# 全てのデータを一つのシートにまとめる。フォーマット：
#（通常（現金）、ETC、ETC2.0、深夜、休日、平日朝夕 還元率30%(ETC)、平日朝夕 還元率50%(ETC)、平日朝夕 還元率30%(ETC2.0)、平日朝夕 還元率50%(ETC2.0）
print("全てのデータを一つのシートにまとめる...")
fin_data = [fin_gen, fin_etc, fin_etc2, fin_kyu, fin_shya, fin_etc30p, fin_etc50p, fin_2etc30p, fin_2etc50p]
fin_data_comp = [fin_gen, fin_etc, fin_etc2, fin_kyu, fin_shya]
df_merged = reduce(lambda left,right: pd.merge(left, right, on = ['入口', '出口'], how='outer'), fin_data)
df_merged.columns = pd.MultiIndex.from_tuples([tuple(c.split('_')) for c in df_merged.columns])
df_merg_comp = reduce(lambda left,right: pd.merge(left, right, on = ['入口', '出口'], how='outer'), fin_data_comp)
df_merg_comp.columns = pd.MultiIndex.from_tuples([tuple(c.split('_')) for c in df_merg_comp.columns])

#compare datas to output error list
#データ比較しエラーリストを作成
diff_ic = compare_toll()

# Export into file.
# エクセルにエクスポートする。希望しているファイル名を入力できます。
print("""
エクセルにエクスポートする。希望しているファイル名を入力できます。
6種類のファイルが出力できます。
    1. まとめデータのエクセルファイル
    2. まとめデータのCSVファイル
    3. コンパクトまとめデータのCSVファイル（還元率以外）
    4. 入力エラーのCSVファイル
    5. 生データのエクセルファイル
    6. 種類ごとに分けるデータのエクセルファイル
""")
output_file = input("出力結果ファイル名を入力してください（例:ryokin_fees.xlsx）:")
output_file_csv = input("出力結果のCSVファイル名を入力してください（例:ryokin_fees.csv）:")
output_error_csv = input("入力エラーのCSVファイル名を入力してください（例:ryokin_error.csv）:")
raw_file = input("出力結果の生データファイル名を入力してください（例:ryokin_fees.xlsx）:")
omake_file = input("出力結果の種類ごとに分けるデータファイル名を入力してください（例:ryokin_fees.xlsx）:")

df_merged.to_csv(output_file_csv)
df_merg_comp.to_csv("compact" + output_file_csv)
diff_ic.to_csv(output_error_csv)

with pd.ExcelWriter(output_file) as writer:
    df_merged.to_excel(writer, sheet_name = 'まとめ')

with pd.ExcelWriter(raw_file) as writer:
    pd_kei.to_excel(writer, sheet_name = '料金（軽自動車）')
    pd_normal.to_excel(writer, sheet_name = '料金（普通車）')
    pd_chugata.to_excel(writer, sheet_name = '料金（中型車）')
    pd_ogata.to_excel(writer, sheet_name = '料金（大型車）')
    pd_toku.to_excel(writer, sheet_name = '料金（特大車）')

with pd.ExcelWriter(omake_file) as writer:
    fin_gen.to_excel(writer, sheet_name = '料金（通常（現金））')
    fin_etc.to_excel(writer, sheet_name = '料金（ETC）')
    fin_etc2.to_excel(writer, sheet_name = '料金（ETC2.0）')
    fin_kyu.to_excel(writer, sheet_name = '料金（休日）')
    fin_shya.to_excel(writer, sheet_name = '料金（深夜）')
    fin_etc30p.to_excel(writer, sheet_name = '料金（還元率30%(ETC)）')
    fin_etc50p.to_excel(writer, sheet_name = '料金（還元率50%(ETC)）')
    fin_2etc30p.to_excel(writer, sheet_name = '料金（還元率30%(ETC2.0)）')
    fin_2etc50p.to_excel(writer, sheet_name = '料金（還元率50%(ETC2.0)）')

print("出力ファイルが出来ましたのでプログラムの同じファイルからダウンロードできます。")
