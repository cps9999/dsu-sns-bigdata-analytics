from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os

def create_youtube_search_url(keyword: str):
    return f"https://www.youtube.com/results?search_query={keyword}&sp=EgIQAQ%253D%253D"

keyword = input("1.유튜브에서 검색할 주제 키워드를 입력하세요(예:롯데마트): ")
count = int(input("2.위 주제로 댓글을 크롤링할 유튜브 영상은 몇건입니까?: "))
comment_cnt = int(input("3.각 동영상에서 추출할 댓글은 몇건입니까?: "))
filepath = input("4.크롤링 결과를 저장할 폴더명만 쓰세요(예: c:\\temp\\): ")

if not os.path.isdir(filepath):
    os.mkdir(filepath)

addrs = []
chrome_driver = ChromeDriverManager().install()
driver = webdriver.Chrome(chrome_driver)

driver.get(create_youtube_search_url(keyword))
driver.implicitly_wait(30)
driver.maximize_window()

while True:
    addrs = driver.execute_script("""
        return [...document.querySelectorAll("#contents > ytd-video-renderer a#thumbnail")].map(element => element.getAttribute("href"));
    """)
    if len(addrs) >= count:
        break
    driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)    
    driver.implicitly_wait(30)

full_urls = list(map(lambda url: f"https://youtube.com{url}", addrs))[0:count]
names = []
contents = []
dates = []

for url in full_urls:
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
    )
    time.sleep(1)
    
    driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)
        
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#body"))
    )
    
    _names = []
    _contents = []
    _dates = []
    
    while True:
        (_names, _contents, _dates) = driver.execute_script("""
            return [
                [...document.querySelectorAll("#header-author > h3")].map(element => element.innerText),
                [...document.querySelectorAll("#content-text")].map(element => element.innerText),
                [...document.querySelectorAll("#header-author > yt-formatted-string > a")].map(element => element.innerText) 
            ]
        """)        

        if min([len(_names), len(_contents), len(_dates)]) >= comment_cnt:
            break

        driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.PAGE_DOWN)
        driver.implicitly_wait(30)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#body"))
        )

        time.sleep(3)
        

    names = [*names, _names[0:comment_cnt]]
    contents = [*contents, _contents[0:comment_cnt]]
    dates = [*dates, _dates[0:comment_cnt]]

df_base_data = {
    "URL 주소": [],
    "댓글작성자명": [],
    "댓글작성일자": [],
    "댓글 내용": []
}

with open(filepath + ".txt", "w", encoding="utf8") as fp:
    for i, url in enumerate(full_urls):
        for name, content, date in zip(names[i], contents[i], dates[i]):
            df_base_data["URL 주소"] = [*df_base_data["URL 주소"], url]
            df_base_data["댓글작성자명"] = [*df_base_data["댓글작성자명"], name]
            df_base_data["댓글작성일자"] = [*df_base_data["댓글작성일자"], date]
            df_base_data["댓글 내용"] = [*df_base_data["댓글 내용"], content]

            fp.write(f"{'-'*100}\n") 
            fp.write(f"1.유튜브 URL주소: {url}\n")
            fp.write(f"2.댓글 작성자명: {name}\n")
            fp.write(f"3.댓글 작성일자: {date}\n")
            fp.write(f"4.댓글 내용: {content}\n")
            fp.write("\n")

df = pd.DataFrame(df_base_data)
df.to_excel(filepath + ".xlsx")
df.to_csv(filepath + ".csv", encoding="utf8")
