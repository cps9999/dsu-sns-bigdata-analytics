from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from os.path import basename
import requests
import time
import os

def create_pixabay_search_url(keyword, page_no):
    return f"https://pixabay.com/ko/images/search/{keyword}/?pagi={page_no}"

print('=' * 100)
print("pixabay 사이트에서 이미지를 검색하여 수집하는 크롤러 입니다")
print('=' * 100)

keyword = input("1.크롤링할 이미지의 키워드는 무엇입니까?: ")
cnt = int(input("2.크롤링 할 건수는 몇건입니까?: "))
filepath = input("3.파일이 저장될 경로만 쓰세요(예: c:\\temp\\): ")

if not os.path.isdir(filepath):
    os.mkdir(filepath)

chrome_driver = ChromeDriverManager().install()
driver = Chrome(chrome_driver)

page_no = 1

while True:
    driver.get(create_pixabay_search_url(keyword, page_no))
    driver.implicitly_wait(30)
    time.sleep(1)

    imgs = driver.execute_script("""
        return window.__BOOTSTRAP__;
    """)

    imgs = list(map(lambda r: r["sources"]["1x"], imgs["page"]["results"]))

    for i, img_url in enumerate(imgs):
        with open(os.path.join(filepath, basename(img_url)), "wb") as fp:
            response_img = requests.get(img_url).content
            fp.write(response_img)
        print(f"{cnt} 개 중 {len(os.listdir(filepath))} 개 다운로드 완료.")

        if len(os.listdir(filepath)) >= cnt:
            break

    if len(os.listdir(filepath)) >= cnt or len(imgs) < 100:
        break

    page_no = page_no + 1
