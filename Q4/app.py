from os.path import basename
import os

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests

def create_google_search_url(keyword: str):
    return f"https://www.google.com/search?q={keyword}"

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(10)

print("=" * 100)
print("연습문제 7-4. 구글 사이트에서 pdf 파일을 검색하여 수집하는 크롤러")
print("=" * 100)

keyword = input("1.크롤링할 키워드는 무엇입니까?: ")
count = int(input("2.크롤링 할 건 수는 몇건입니까?: "))
filepath = input("3.파일을 저장할 경로만 쓰세요(예:c:\\temp\\): ")

# 해당 경로에 폴더가 없다면 폴더 만들기
if not os.path.isdir(filepath):
    os.mkdir(filepath)

driver.get(create_google_search_url(keyword))

downloaded_files = 0

while downloaded_files < count:

    # 현재 페이지에 있는 PDF 링크를 모두 가져옴
    pdf_links = driver.find_elements(By.CSS_SELECTOR, '.yuRUbf > a')

    # 링크를 통해 파일 다운로드
    for link in pdf_links:
        pdf_url = link.get_attribute('href')
        
        if "pdf" in pdf_url:
            file_name = basename(pdf_url)
            file_path = os.path.join(filepath, file_name)
            
            if not os.path.isfile(file_path):
                response = requests.get(pdf_url, verify=False)

                with open(file_path, "wb") as fp:
                    fp.write(response.content)
                    downloaded_files += 1

                    print(f"{downloaded_files}. 파일 다운로드 완료: {file_name}")

                    if downloaded_files >= count:
                        print("지정된 수의 파일이 다운로드 되어 프로그램을 종료합니다.")
                        driver.quit()
                        exit()

    # 다음 페이지로 이동
    try:
        next_button = driver.find_element(By.ID, 'pnnext')
        next_button.click()
    except Exception as e:
        print("더 이상 페이지가 존재하지 않아, 자동으로 종료합니다.")
        driver.quit()
        exit()

driver.quit()
