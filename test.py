from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome 드라이버 경로 설정
# webdriver_service = Service()
# webdriver_service.start()

# Chrome 옵션 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": r"C:\Users\jinmo\downloads",
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Chrome 드라이버 생성
driver = webdriver.Chrome(options=chrome_options)

# 웹 페이지로 이동
driver.get('https://file-examples.com/wp-content/storage/2017/02/file-sample_100kB.doc')

# # 파일 다운로드 링크 요소를 찾습니다. 예를 들어 <a> 태그에 다운로드 링크가 있다면:
# download_link = driver.find_element(By.XPATH, '//*[@id="download-link"]')

# # 파일 다운로드를 클릭합니다.
# download_link.click()

# 파일 다운로드가 완료될 때까지 대기합니다.
wait = WebDriverWait(driver, 10)
downloaded_file_path = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "downloaded_file_css_selector"))).get_attribute("href")

# 다운로드한 파일 경로 출력
print("다운로드한 파일 경로:", downloaded_file_path)

# Chrome 드라이버 종료
driver.quit()