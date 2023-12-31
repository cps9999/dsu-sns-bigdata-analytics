from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# 사용자 입력 받기
print("=" * 100)
key_word = input("1.공고명으로 검색할 키워드는 무엇입니까?: ")
begin_date = input("2.조회 시작일자 입력(예:2019/01/01): ")
finish_date = input("3.조회 종료일자 입력(예:2019/12/31): ")
save_directory = input("4.파일로 저장할 폴더 이름을 쓰세요(예:c:\\temp\\): ")

# 파일 경로 설정
xlsx_file = f"{save_directory}.xlsx"
txt_file = f"{save_directory}.txt"
cnt_limit = 30

# 웹 드라이버 설치
chrome = ChromeDriverManager().install()
browser = webdriver.Chrome(chrome)

# 웹사이트 열기
browser.get("https://www.g2b.go.kr/index.jsp")
browser.implicitly_wait(30)

# 검색 필드에 키워드, 시작일, 종료일 입력
browser.find_element(By.CSS_SELECTOR, "#bidNm").send_keys(key_word)
browser.find_element(By.CSS_SELECTOR, "#fromBidDt").send_keys(begin_date)
browser.find_element(By.CSS_SELECTOR, "#toBidDt").send_keys(finish_date)

# 검색 버튼 클릭 (자바스크립트 실행)
browser.execute_script("javascript:search1();")
time.sleep(1)

# 검색 결과 로딩이 완료될 때까지 대기
WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#sub")))

total_data = []

while len(total_data) < cnt_limit:
    # 검색 결과 가져오기
    data_list = browser.execute_script("""
        return [
            ...document
                .querySelector("#sub")
                .contentDocument.querySelector("html > frameset > frame:nth-child(2)")
                .contentDocument.querySelectorAll(
                "#resultForm > div.results > table > tbody > tr"
                ),
            ].map((trElement) => {
            const tdItems = trElement.querySelectorAll("td");
            const itemTexts = [...tdItems].map((element) => element.innerText);

            return [
                ...itemTexts.slice(0, 3),
                tdItems[3].querySelector("a")?.getAttribute("href") || "",
                ...itemTexts.slice(3),
            ];
        });
    """)

    total_data.extend(data_list)  # total_data를 업데이트 합니다.


    try:
        # 다음 페이지로 이동
        browser.execute_script("""
            document
                .querySelector("#sub")
                .contentDocument.querySelector("html > frameset > frame:nth-child(2)")
                .contentDocument.querySelector("#pagination > a.default").click();
        """)
            
        time.sleep(1)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sub"))
        )
    except:
        break

# 검색 결과를 텍스트 파일에 저장
with open(txt_file, "w", encoding="utf8") as fp:
    for i, sample in enumerate(total_data):
        fp.write(f"{i + 1}번쨰 공고내용을 추출합니다~~~~\n")
        fp.write(f"1.업무: {sample[0]}\n")
        fp.write(f"2.공고번호-치수: {sample[1]}\n")
        fp.write(f"3.분류: {sample[2]}\n")
        fp.write(f"4.공고명: {sample[3]}\n")
        fp.write(f"5.URL 주소: {sample[4]}\n")
        fp.write(f"6.공고기관: {sample[5]}\n")
        fp.write(f"7.수요기관: {sample[6]}\n")
        fp.write(f"8.계약방법: {sample[7]}\n")
        fp.write(f"9.입력일시(입찰마감일시): {sample[8]}\n")
        fp.write(f"10.공동수급: {sample[9]}\n")
        fp.write(f"11.투찰여부: {sample[10]}\n")
        fp.write("\n")

# 검색 결과를 엑셀 파일에 저장
result_df = pd.DataFrame(total_data, columns=["업무", "공고번호-치수", "분류", "공고명", "URL 주소", "공고기관", "수요기관", "계약방법", "입력일시(입찰마감일시)", "공동수급", "투찰여부"])
result_df.to_excel(xlsx_file, index=False)
