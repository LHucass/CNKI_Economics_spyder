from collections import Iterable
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from time import sleep
import selenium.webdriver.support.expected_conditions as EC
import pandas as pd
import numpy as np
browser = webdriver.Safari()
browser.get(r"http://data.cnki.net/ValueSearch/Index?datatype=year&ky=GDP")#设置好浏览器驱动配置

#初始设定，当选择完爬虫后不得修改，否则会导致问题！！
indicators = ["R&D人员 全时当量","R&D人员","R&D 内部支出","R&D内部经费支出"]
#regions = ["北京市","天津市","廊坊市","石家庄市","邯郸市","东营市","濮阳市","运城市"]
regions = ["北京","天津","石家庄","唐山","秦皇岛","邯郸","邢台","保定","张家口","承德","沧州","廊坊","衡水","太原","大同","阳泉","长治","晋城","朔州","晋中","运城","忻州","临汾","吕梁","呼和浩特","包头","乌海","赤峰","通辽","鄂尔多斯","呼伦贝尔","巴彦淖尔","乌兰察布","沈阳","大连","鞍山","抚顺","本溪","丹东","锦州","营口","阜新","辽阳","盘锦","铁岭","朝阳","葫芦岛","长春","吉林","四平","辽源","通化","白山","松原","白城","哈尔滨","齐齐哈尔","鸡西","鹤岗","双鸭山","大庆","伊春","佳木斯","七台河","牡丹江","黑河","绥化","上海","南京","无锡","徐州","常州","苏州","南通","连云港","淮安","盐城","扬州","镇江","泰州","宿迁","杭州","宁波","温州","嘉兴","湖州","绍兴","金华","衢州","舟山","台州","丽水","合肥","芜湖","蚌埠","淮南","马鞍山","淮北","铜陵","安庆","黄山","滁州","阜阳","宿州","巢湖","六安","亳州","池州","宣城","福州","厦门","莆田","三明","泉州","漳州","南平","龙岩","宁德","南昌","景德镇","萍乡","九江","新余","鹰潭","赣州","吉安","宜春","抚州","上饶","济南","青岛","淄博","枣庄","东营","烟台","潍坊","济宁","泰安","威海","日照","莱芜","临沂","德州","聊城","滨州","菏泽","郑州","开封","洛阳","平顶山","安阳","鹤壁","新乡","焦作","濮阳","许昌","漯河","三门峡","南阳","商丘","信阳","周口","驻马店","武汉","黄石","十堰","宜昌","襄阳","鄂州","荆门","孝感","荆州","黄冈","咸宁","随州","长沙","株洲","湘潭","衡阳","邵阳","岳阳","常德","张家界","益阳","郴州","永州","怀化","娄底","广州","韶关","深圳","珠海","汕头","佛山","江门","湛江","茂名","肇庆","惠州","梅州","汕尾","河源","阳江","清远","东莞","中山","潮州","揭阳","云浮","南宁","柳州","桂林","梧州","北海","防城港","钦州","贵港","玉林","百色","贺州","河池","来宾","崇左","海口","三亚","三沙","儋州","重庆","成都","自贡","攀枝花","泸州","德阳","绵阳","广元","遂宁","内江","乐山","南充","眉山","宜宾","广安","达州","雅安","巴中","资阳","贵阳","六盘水","遵义","安顺","毕节","铜仁","昆明","曲靖","玉溪","保山","昭通","丽江","普洱","临沧","拉萨","日喀则","昌都","林芝","山南","那曲","西安","铜川","宝鸡","咸阳","渭南","延安","汉中","榆林","安康","商洛","兰州","嘉峪关","金昌","白银","天水","武威","张掖","平凉","酒泉","庆阳","定西","陇南","西宁","海东","海南","银川","石嘴山","吴忠","固原","中卫","乌鲁木齐","克拉玛依","吐鲁番","哈密"]
years = ["2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021"]
try:
    curl_finish = np.load("curl_finish.npy")
except:
    curl_finish = np.zeros((len(indicators),len(regions),len(years)),bool)

for indicator in indicators:
    for region in regions:
        for year in years:
            if curl_finish[indicators.index(indicator), regions.index(region), years.index(year)] == 1:
                continue
            try:
                df_data = pd.read_excel(indicator+".xlsx")
            except:
                df_data = pd.DataFrame()
            print(indicator,region,year)
            #初始化并模拟搜索
            browser.find_element_by_name("IndicateName").clear()
            browser.find_element_by_name("IndicateName").send_keys(indicator)#此行代码运行极不稳定，一旦卡死请重新运行！
            print("passed")
            browser.find_element_by_name("IndicateRegion").clear()
            browser.find_element_by_name("IndicateRegion").send_keys(region)
            browser.find_element_by_name("StartYear").send_keys(year)
            browser.find_element_by_name("EndYear").send_keys(year)
            element = browser.find_element_by_id("AdvancedSearch")  # 页面搜索按钮
            browser.execute_script("arguments[0].click();",element)  # arguments[0], element means passing element into arguments[0] to execute in Javascript
            xpath = "/html/body/div[1]/div[3]/div[1]/div/div[2]/table/tbody/tr"
            sleep(20)
            print("start sleeping")
            ls = []
            try:#此处根据是否刷新，进行进一步爬取操作，将table的每一个元素都加入ls
                table = browser.find_elements_by_xpath(xpath)
                for tr in table:
                    tds = tr.find_elements_by_tag_name("td")
                    ls.append([td.text for td in tds])
            except EC.StaleElementReferenceException:
                table = browser.find_elements_by_xpath(xpath)
                for tr in table:
                    tds = tr.find_elements_by_tag_name("td")
                    ls.append([td.text for td in tds])
            table_df = pd.DataFrame(ls)#将获取到的所有ls转为dataframe入table_df
            df_data = df_data.append(table_df)
            df_data.to_excel(indicator+".xlsx")
            curl_finish[indicators.index(indicator), regions.index(region), years.index(year)] = 1  # 测试成功，当一个对应数值爬过了就修改标志位为1
            np.save("curl_finish.npy",curl_finish)#保存爬虫状态文件
print(curl_finish)

#indicator = "R&D人员全时当量"
#region = "北京市"
#year = "2005"
'''
browser.find_element_by_name("IndicateName").clear()
browser.find_element_by_name("IndicateName").send_keys(indicator)
browser.find_element_by_name("IndicateRegion").clear()
browser.find_element_by_name("IndicateRegion").send_keys(region)
browser.find_element_by_name("StartYear").send_keys(year)
browser.find_element_by_name("EndYear").send_keys(year)
element = browser.find_element_by_id("AdvancedSearch")#页面搜索按钮
browser.execute_script("arguments[0].click();", element)  # arguments[0], element means passing element into arguments[0] to execute in Javascript
xpath = "/html/body/div[1]/div[3]/div[1]/div/div[2]/table/tbody/tr"
sleep(20)
ls = []
try:
    table = browser.find_elements_by_xpath(xpath)
    for tr in table:
        tds = tr.find_elements_by_tag_name("td")
        print("获取%s年%s地区表格数据成功",year,region)
        ls.append([td.text for td in tds])
        print("数据增加成功")
        print(ls)
except EC.StaleElementReferenceException:
    print("表格已被刷新，重新获取中")
    table = browser.find_elements_by_xpath(xpath)
    for tr in table:
        tds = tr.find_elements_by_tag_name("td")
        ls.append([td.text for td in tds])
        print(ls)
table_df = pd.DataFrame(ls)
print(table_df)
'''
