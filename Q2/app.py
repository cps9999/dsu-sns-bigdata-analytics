from datetime import datetime
import requests
import math
import pandas as pd
import json

def get_posts(keyword, count, startDt, endDt):
    page_count = math.ceil(int(count) / 20)
    result_posts = []

    for page_no in range(1, page_count + 1):
        response = requests.get(
            "https://section.blog.naver.com/ajax/SearchList.naver",
            headers={
                "Referer": "https://section.blog.naver.com/Search/Post.naver?pageNo=1&rangeType=ALL&orderBy=sim&keyword=%EC%88%98%EB%AC%B8%EB%8B%AC%EA%B8%B0%EC%B2%B4%ED%97%98"
            },
            params={
                "countPerPage": 20,
                "currentPage": page_no,
                "keyword": keyword,
                "startDate": startDt,
                "endDate": endDt,
            }
        )

        if not response.ok:
            print("요청을 성공적으로 실행하지 못 했습니다.")
            continue

        text = response.text[5:]
        data = json.loads(text)

        if "code" in data["result"] and data["result"]["code"] == "error":
            print("입력 값에 문제가 있어 응답이 성공적으로 이루어지지 않았습니다.")
            continue

        result_posts.extend(data["result"]["searchList"])

    return result_posts

def count_contains(data, keywords):
    return sum(1 for keyword in keywords if keyword in data)

print('=' * 100)
print("연습문제 6-5: 블로그 크롤러 : 여러건의 네이버 블로그 정보 추출하여 저장하기".center(65))
print('=' * 100)

keyword = input("1.크롤링할 키워드는 무엇입니까?(예:여행): ")
must_contains = input(
    "2.결과에서 반드시 포함하는 단어를 입력하세요(예:국내,바닷가)\n(여러개일 경우 ,로 구분해서 입력하고 없으면 엔터를 입력하세요): ").split(',')
must_excludes = input(
    "3.결과에서 제외할 단어를 입력하세요(예:분양권,해외)\n(여러개일 경우 ,로 구분해서 입력하고 없으면 엔터 입력하세요): ").split(',')
startDt = input("4.조회 시작일자 입력(예:2017-01-01):")
endDt = input("5.조회 종료일자 입력(예:2017-12-31):")
crawlCnt = input("6.크롤링 할 건수는 몇건입니까?(최대 1000건): ") or "5"
filepath = input("7.파일을 저장할 폴더명만 쓰세요(예:c:\\temp\\):")

xlsx_path = f"{filepath}.xlsx"
txt_path = f"{filepath}.txt"

results = get_posts(keyword, crawlCnt, startDt, endDt)

filtered_posts = []
for post in results:
    must_contain_count = count_contains(post["contents"], must_contains)
    must_exclude_count = count_contains(post["contents"], must_excludes)
    
    if must_contain_count == len(must_contains) and must_exclude_count == 0:
        filtered_posts.append(post)

df = pd.DataFrame({
    "블로그주소": [post["postUrl"] for post in filtered_posts],
    "작성자이름": [post["nickName"] for post in filtered_posts],
    "작성일자": [datetime.fromtimestamp(post["addDate"] / 1000).strftime("%Y.%m.%d %H:%M:%S") for post in filtered_posts],
    "블로그내용": [post["contents"] for post in filtered_posts]
})

with open(txt_path, "w", encoding="utf8") as fp:
    for rownum in range(df.shape[0]):
        fp.write(f"총 {df.shape[0]} 건 중 {rownum + 1} 번째 블로그 데이터를 수집합니다".ljust(100, '=') + '\n')
        fp.write(f"1.블로그 주소:{df['블로그주소'][rownum]}\n")
        fp.write(f"2.작성자:{df['작성자이름'][rownum]}\n")
        fp.write(f"3.작성 일자:{df['작성일자'][rownum]}\n")
        fp.write(f"4.블로그 내용:{df['블로그내용'][rownum]}\n")
        fp.write("\n")

df.to_excel(xlsx_path)
