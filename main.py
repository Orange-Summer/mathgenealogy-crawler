import random

import pandas
import requests
import urllib3
from bs4 import BeautifulSoup
from retrying import retry

global advisorId
advisorId = 295778

requests.adapters.DEFAULT_RETRIES = 15
s = requests.session()
s.keep_alive = False
s.verify = False
urllib3.disable_warnings()

header_list = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0;) Gecko/20100101 Firefox/61.0"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"},
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36"},
    {"User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15"},
]




@retry(stop_max_attempt_number=10, wait_random_min=1000, wait_random_max=10000)
def _get_request(url, session, headers):
    return session.get(url, headers=headers, timeout=1)


def get_request(url, session, headers):
    try:
        html_str = _get_request(url, session, headers)
    except TimeoutError:  # 1
        html_str = 'TimeoutError'
    except:  # 2
        html_str = 'OtherError'
    return html_str


def crawl(pid, func):
    global advisorId
    print("Visiting: " + str(pid))
    # 加载页面
    url = "https://mathgenealogy.org/id.php?id=" + str(pid)
    headers = random.choice(header_list)
    page = get_request(url, func, headers)
    # time.sleep(random.randint(2, 3))
    soup = BeautifulSoup(page.text, 'lxml')
    if soup.find("h2") is None:
        return 0
    # 获取姓名
    name = soup.find("h2").text.strip().replace("  ", " ")
    print("  Name: " + name)
    # 获取学位、年份、国籍
    div1 = soup.select("#paddingWrapper > div:nth-child(7)")[0]
    if div1 is not None:
        institution = div1.find_all("span")[1].text.strip()
        if len(institution) == 0:
            institution = ""
        title_and_year = div1.find_all("span")[0].text.replace(institution, "").strip().replace("  ", " ")
        title_and_year_split = title_and_year.split()
        if len(title_and_year_split) > 1:
            title = " ".join(title_and_year_split[:-1])
            year = title_and_year_split[-1]
        else:
            title = ""
            year = ""
        image = div1.find("img")
        if image is not None:
            country = image["alt"]
        else:
            country = ""
    else:
        institution = ""
        title = ""
        year = ""
        country = ""

    # 获取论文
    div2 = soup.select("#paddingWrapper > div:nth-child(8)")[0]
    if div2 is not None:
        dissertation = div2.find_all("span")[1].text
        dissertation = dissertation \
            .strip().strip('"').strip('\'') \
            .replace('\r', ' ').replace('\n', ' ').replace('"', ' ').replace('\'', ' ').replace('  ', ' ')
        dissertation = "'" + dissertation + "'"
        if len(dissertation) == 0:
            dissertation = ''
    else:
        dissertation = ''

    # 获取分类
    div3 = soup.select("#paddingWrapper > div:nth-child(9)")
    if len(div3) > 0:
        div3 = div3[0]
        if div3 is not None:
            temp = div3.text.split(':')[1].split('—')[0].strip()
            if temp.isdigit():
                classification = int(temp)
            else:
                classification = -1
        else:
            classification = -1
    else:
        classification = -1

    mathematician = {
        "id": pid,
        "name": name,
        "title": title,
        "institution": institution,
        "year": year,
        "country": country,
        "dissertation": dissertation,
        "classification": classification
    }
    # 存入 mathematician.csv
    df = pandas.DataFrame(mathematician, index=[pid])
    df.to_csv("data/mathematician.csv", mode='a', index=False, header=False)
    # 找到当前导师
    p_tag = soup.find_all("p")[2]
    for link in p_tag.find_all("a"):
        href = link.get("href")
        if href is not None and href.startswith("id.php?id=") and "&fChrono" not in href:
            advisor = {
                "id": advisorId,
                "pid": pid,
                "aid": int(href[10:])
            }
            df = pandas.DataFrame(advisor, index=[advisorId])
            advisorId += 1
            df.to_csv("data/advisor.csv", mode='a', index=False, header=False)
    print("  nextadvisorId: " + str(advisorId))


if __name__ == "__main__":
    for pid in range(276143, 291062):
        crawl(pid, s)
    # crawl(178330, s)
    # crawl(293245, s)
