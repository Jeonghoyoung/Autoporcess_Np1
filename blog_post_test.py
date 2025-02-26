from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_post_to_blog(username, password, title, content):
    """
    블로그 글 작성 테스트
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    # driver = webdriver.Chrome(options=options)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)    
    try:
        # 네이버 로그인
        driver.get('https://nid.naver.com/nidlogin.login')
        script_id = f'document.querySelector("#id").value="{username}"'
        script_pw = f'document.querySelector("#pw").value="{password}"'
        driver.execute_script(script_id)
        driver.execute_script(script_pw)
        
        wait = WebDriverWait(driver, 10)
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_login')))
        login_button.click()
        time.sleep(3)
        
        # 블로그 글쓰기 페이지로 이동
        driver.get(f'https://blog.naver.com/{username}/postwrite')
        time.sleep(3)
        
        # iframe 전환
        driver.switch_to.frame('mainFrame')
        
        # 제목 입력
        title_input = driver.find_element(By.CSS_SELECTOR, '.se-text-input')
        title_input.send_keys(title)
        
        # 본문 입력
        content_iframe = driver.find_element(By.CSS_SELECTOR, '.se-iframe')
        driver.switch_to.frame(content_iframe)
        body = driver.find_element(By.CSS_SELECTOR, 'body')
        body.send_keys(content)
        
        # 프레임 복귀
        driver.switch_to.default_content()
        driver.switch_to.frame('mainFrame')
        
        # 발행 버튼 클릭
        publish_button = driver.find_element(By.CSS_SELECTOR, '.publish_button')
        publish_button.click()
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"블로그 글 작성 실패: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    USERNAME = "your_username"
    PASSWORD = "your_password"
    TEST_TITLE = "테스트 제목입니다"
    TEST_CONTENT = "테스트 본문입니다"
    
    result = test_post_to_blog(USERNAME, PASSWORD, TEST_TITLE, TEST_CONTENT)
    print(f"테스트 결과: {'성공' if result else '실패'}") 