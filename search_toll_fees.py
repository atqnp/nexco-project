import pandas as pd
import time
import csv
import itertools
from functools import reduce
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

url = "http://search.w-nexco.co.jp/route.php"
options = Options()
options.add_argument('--headless')

df = pd.read_csv('ryokin_test.csv')
df_edit = df.dropna(subset=['入口','出口'])

#new session
class FeeList(object):
    def __init__(self):
        self.buttonlist = []

class AllToll(FeeList):
    def __init__(self, cartype_val):
        FeeList.__init__(self)
        self.cartype_val = cartype_val
        
    def get_toll(self, cartype_val):
        for index, row in df_edit.iterrows():
            #navigate to the page
            driver = webdriver.Chrome(chrome_options=options)
            driver.get(url)

            #get the fill in form
            in_field = driver.find_element_by_name("fnm")
            in_field.send_keys(row['入口'])
            time.sleep(1)
            out_field = driver.find_element_by_name("tnm")
            out_field.send_keys(row['出口'])
            time.sleep(1)

            select_car_type = Select(driver.find_element_by_name("cartyp")).select_by_value(cartype_val)
            time.sleep(1)
            select_hour = Select(driver.find_element_by_id("sl_hour_id")).select_by_value("10")
            time.sleep(1)
            select_min = Select(driver.find_element_by_id("sl_min_id")).select_by_value("0")
            time.sleep(1)
            select_detour1 = Select(driver.find_element_by_id("detour1_id")).select_by_value("G1110")
            time.sleep(1)
            select_detour2 = Select(driver.find_element_by_id("detour2_id")).select_by_value("G6000")

            driver.find_element_by_css_selector(".submit-btn").send_keys("\n")
            time.sleep(3)
            driver.find_element_by_css_selector(".submit-btn").send_keys("\n")
            time.sleep(2)
    
            #wait for page to load
            time.sleep(3)
            driver.find_element_by_id("pritab9").click()
            #get the toll fee
            time.sleep(3)
            
            def ic_name():
                start = driver.find_element_by_css_selector("span.start").get_attribute("innerText")
                goal = driver.find_element_by_css_selector("span.goal").get_attribute("innerText")
                return start, goal
                
            def norm_toll():
                normal_toll = driver.find_element_by_css_selector("span.toll-normal").get_attribute("innerText")
                etc_toll = driver.find_element_by_css_selector("span.toll-etc").get_attribute("innerText")
                etc2_toll = driver.find_element_by_css_selector("span.toll-etc2").get_attribute("innerText")
                return normal_toll, etc_toll, etc2_toll
            
            def box_toll():
                box1_toll = driver.find_element_by_xpath('//*[@class="etc-info pc-stay pos-etc_box"]/div[2]/div')
                span_box1 = box1_toll.find_elements_by_tag_name("span")
                box1 = []
                for span1 in span_box1:
                    test1 = span1.get_attribute("innerText")
                    box1.append(test1)
                box2_toll = driver.find_element_by_xpath('//*[@class="etc-info pc-stay pos-etc2_box"]/div[2]/div')
                span_box2 = box2_toll.find_elements_by_tag_name("span")
                box2 = []
                for span2 in span_box2:
                    test2 = span2.get_attribute("innerText")
                    box2.append(test2)
                    
                def normal_case():
                    if len(span_box1) == 1:
                        box1.insert(0,0)
                        box1.extend([0,0])
                    if len(span_box2) == 1:
                        box2.insert(0,0)
                        box2.extend([0,0])
                    
                def big_case():
                    box1.insert(0,0)
                    box2.insert(0,0)
                    if len(span_box1) == 1:
                        box1.extend([0,0])
                    if len(span_box2) == 1:
                        box2.extend([0,0])
                
                if cartype_val == "1" or cartype_val == "2":
                    run_case = normal_case()
                else:
                    run_case = big_case()
                return  box1, box2
            
            name_of_ic = ic_name()
            get_norm_toll = norm_toll()
            get_box_toll = list(itertools.chain.from_iterable(box_toll()))

            #close session
            driver.quit()
    
            toll = [name_of_ic, get_norm_toll, get_box_toll]
            merged_toll = list(itertools.chain.from_iterable(toll))
            self.buttonlist.append(merged_toll)
            time.sleep(10)
        return self.buttonlist
    
kei = AllToll("1").get_toll("1")
normal = AllToll("2").get_toll("2")
chugata = AllToll("3").get_toll("3")
ogata = AllToll("4").get_toll("4")
toku = AllToll("5").get_toll("5")

title =  ['入口', '出口', '通常（現金）', 'ETC', 'ETC2.0', 
            '休日(ETC)', '深夜(ETC)', '還元率30%(ETC)', '還元率50%(ETC)', 
            '休日(ETC2.0)', '深夜(ETC2.0)','還元率30%(ETC2.0)', '還元率50%(ETC2.0)']
pd_kei = pd.DataFrame(kei, columns = title)
pd_normal = pd.DataFrame(normal, columns = title)
pd_chugata = pd.DataFrame(chugata, columns = title)
pd_ogata = pd.DataFrame(ogata, columns = title)
pd_toku = pd.DataFrame(toku, columns = title)

all_kei = pd_kei[pd_kei.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)
all_normal = pd_normal[pd_normal.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)
all_chugata = pd_chugata[pd_chugata.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)
all_ogata = pd_ogata[pd_ogata.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)
all_toku = pd_toku[pd_toku.columns[2:]].replace('[\$,円,分]', '', regex=True).astype(int)

fin_gen = pd.concat([pd_kei['入口'], pd_kei['出口'],
                     all_kei['通常（現金）'],all_normal['通常（現金）'],
                     all_chugata['通常（現金）'],all_ogata['通常（現金）'],all_toku['通常（現金）']], axis=1, 
                     keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_etc = pd.concat([pd_kei['入口'], pd_kei['出口'],
                     all_kei['ETC'],all_normal['ETC'],
                     all_chugata['ETC'],all_ogata['ETC'],all_toku['ETC']], axis=1,
                     keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_etc2 = pd.concat([pd_kei['入口'], pd_kei['出口'], 
                      all_kei['ETC2.0'],all_normal['ETC2.0'],
                      all_chugata['ETC2.0'],all_ogata['ETC2.0'],all_toku['ETC2.0']], axis=1,
                      keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_kyu = pd.concat([pd_kei['入口'], pd_kei['出口'], 
                     all_kei['休日(ETC)'],all_normal['休日(ETC)'],
                     all_chugata['休日(ETC)'],all_ogata['休日(ETC)'],all_toku['休日(ETC)']], axis=1,
                     keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_shya = pd.concat([pd_kei['入口'], pd_kei['出口'],
                      all_kei['深夜(ETC)'],all_normal['深夜(ETC)'],
                      all_chugata['深夜(ETC)'],all_ogata['深夜(ETC)'],all_toku['深夜(ETC)']], axis=1,
                      keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_etc30p = pd.concat([pd_kei['入口'], pd_kei['出口'], 
                        all_kei['還元率30%(ETC)'],all_normal['還元率30%(ETC)'],
                        all_chugata['還元率30%(ETC)'],all_ogata['還元率30%(ETC)'],all_toku['還元率30%(ETC)']], axis=1,
                        keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_etc50p = pd.concat([pd_kei['入口'], pd_kei['出口'], 
                        all_kei['還元率50%(ETC)'],all_normal['還元率50%(ETC)'],
                        all_chugata['還元率50%(ETC)'],all_ogata['還元率50%(ETC)'],all_toku['還元率50%(ETC)']], axis=1,
                        keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_2etc30p = pd.concat([pd_kei['入口'], pd_kei['出口'],
                         all_kei['還元率30%(ETC2.0)'],all_normal['還元率30%(ETC2.0)'],
                         all_chugata['還元率30%(ETC2.0)'],all_ogata['還元率30%(ETC2.0)'],all_toku['還元率30%(ETC2.0)']], axis=1,
                         keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_2etc50p = pd.concat([pd_kei['入口'], pd_kei['出口'],
                         all_kei['還元率50%(ETC2.0)'],all_normal['還元率50%(ETC2.0)'],
                         all_chugata['還元率50%(ETC2.0)'],all_ogata['還元率50%(ETC2.0)'],all_toku['還元率50%(ETC2.0)']], axis=1,
                         keys=['入口', '出口', '軽自動車', '普通車', '中型車', '大型車', '特大車'])

fin_data = [fin_gen, fin_etc, fin_etc2, fin_kyu, fin_shya, fin_etc30p, fin_etc50p, fin_2etc30p, fin_2etc50p]
df_merged = reduce(lambda left,right: pd.merge(left, right, on = ['入口', '出口'], how='outer'), fin_data)

with pd.ExcelWriter('toll all.xlsx') as writer:
    df_merged.to_excel(writer, sheet)
