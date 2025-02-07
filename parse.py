import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import re
import time


"""
爬時政要聞分類的文章連結
num_pages:從第一頁爬到第n頁
"""
def crawl_url(channel_code, num_pages, data_dict):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    url = 'https://www.cac.gov.cn/cms/JsonList'
    
    data_dict = {}
    for i in range(1,num_pages+1):
        params = {
            'channelCode': channel_code,
            'perPage': '20',
            'pageno': i  # 這裡設置頁數
            }
        response = requests.post(url, data=params, headers=headers)
        response_json = response.json()
        
        for data in response_json['list']:
            data_id = data['infourl'].split('/')[-1].split('.')[0]
            if data_id not in data_dict:
                data_dict[data_id] = data
    return data_dict

"""
檢查URL有沒有包含https
"""
def check_https(string):
    if 'https:' not in string:
        return f'https:{string}'
    else:
        return string

def parse_all_link(content_data):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for doc_id in content_data:
        content_data[doc_id]['infourl'] = check_https(content_data[doc_id]['infourl'])
        doc_url = content_data[doc_id]['infourl']
        
        print(f'Now working at {doc_url}')

        response = requests.get(doc_url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
        
            # 嘗試提取發布時間
            date_tag = soup.find("span", id="pubtime")  # 檢查網頁實際的 class
            publish_date = date_tag.text.strip() if date_tag else "未找到發布時間"
        
            # 嘗試提取來源
            source_tag = soup.find("span", id="source")  # 檢查網頁的 class
            source = source_tag.text.strip().split('：')[1].strip() if source_tag else "未找到來源"
        
            # 嘗試提取內文
            content_tag = soup.find("div", class_="main-content")  # 檢查網頁的內文標籤
            content = content_tag.text.strip() if content_tag else "未找到內文"
            
            content_data[doc_id]['publish_date'] = publish_date
            content_data[doc_id]['source'] = source
            content_data[doc_id]['content'] = content
        else:
            print(f"請求失敗，狀態碼: {response.status_code}")
    return content_data




#%%
if __name__ == "__main__":
    channel_code = {
        "時政要聞":"A093601",
        "辦領導動態":"A09370102",
        "網信發布":"A093702",
        "政策法規":"A093703",
        "互聯網內容管理":"A093704",
        "清朗系列專項行動":"A093711",
        "網絡安全":"A093705",
        "數據治理":"A093708",
        "信息化":"A093706",
        "國際交流":"A093707",
        "更多工作":"A093709",
        }
    
    num_pages = 2
    data_dict = {}
    for channel in channel_code:
        code = channel_code[channel]
        data_dict = crawl_url(code, num_pages, data_dict)
        
    after_parse = parse_all_link(data_dict)

    timestamp = time.localtime()
    date_time_str = time.strftime("%Y-%m-%d %H:%M:%S", timestamp)
    json_path = './{date_time_str}.json'
    
    with open(json_path,'w',enoding='utf-8')as file:
        json.dump(after_parse, file)

#%%


























