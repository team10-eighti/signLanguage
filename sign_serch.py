from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from loguru import logger

URL = 'https://sldict.korean.go.kr/front/sign/signList.do?top_category=CTE'

chrome_options = Options()
chrome_options.add_argument("--headless")
END_INDEX = 3
# driver = webdriver.Chrome()
# driver.implicitly_wait(0.1)

for index in range(2, END_INDEX):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(URL)

    driver.find_element(by=By.XPATH, value=f'/html/body/div[2]/div[3]/div/div/div[1]/nav/div/div/ul/li[1]/ul/li[{index}]/a/span').click()

    # 카테고리
    category = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[3]/div/div/div[4]/form/div[1]/ul/li[5]/a/span').text
    # 결과 찾기 총 ()건
    count = int(driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[1]/p/span').text)
    total_page = (count // 10) + 1
    logger.add(f'{str(index)+ "_" + category}.log')

    csv_file = open(f'{str(index)+ "_" + category}.csv', 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
    csv_writer.writerow(['단어명', '카테고리', '설명', '동영상', '이미지'])

    for page in range(1, total_page+1):
        for i in range(1, 11):
            driver.find_element(by=By.XPATH, value=f'/html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[2]/ul/li[{i}]/div[2]/div/ul/li/div/p/span[1]/a').click()
            video_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "html5Video")))
            sign_page = driver.page_source
            soup = BeautifulSoup(sign_page, 'html.parser')

            words =""
            description = ""
            video_value = ""
            img_value = ""

            try:
                # 단어명
                words = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[3]/div/div/div[4]/form/dl/dd').text

                # 설명
                description = driver.find_element(by=By.XPATH, value='/html/body/div[2]/div[3]/div/div/div[4]/form/div[3]/div[2]/div/div/div[1]/div/dl/dd[2]').text

                # 이미지
                fr_d = soup.select_one('div.fr_d')
                images = fr_d.select('img.mCS_img_loaded')
                img_value = ' '.join([img['src'] for img in images])

                # 동영상
                source_tags = video_element.find_elements(by=By.TAG_NAME, value="source")

                for source in source_tags:
                    if source.get_attribute("type") == "video/mp4":
                        video_value = source.get_attribute("src")

                word_list = words.split(',')
                for word in word_list:
                    row = [word, category, description, video_value, img_value]
                    logger.info(f"[{10*(page-1)+i}/{count}] {row}")
                    csv_writer.writerow(row)

            except Exception as e:
                logger.error(f"[{10*(page-1)+i}/{count}] | Exception: {e}")
                csv_writer.writerow([words, category, description, video_value, img_value])

            driver.back()

        # /html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[3]/span[4]/a  # 2번째 버튼
        # /html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[3]/span[12]/a # 10번째 버튼
        # /html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[3]/span[13]/a # 다음 페이징 버튼
        if page % 10 == 0:
            driver.find_element(by=By.XPATH, value=f'/html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[3]/span[13]/a').click()
        else:
            page_nav = (page % 10) + 3  # range(3, 13)
            driver.find_element(by=By.XPATH, value=f'/html/body/div[2]/div[3]/div/div/div[4]/form/div[2]/div[3]/span[{page_nav}]/a').click()

        sleep(0.01)
    csv_file.close()

    driver.quit()
