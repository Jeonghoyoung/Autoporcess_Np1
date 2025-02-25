from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_login(username, password, is_frequent=False):
    """
    네이버 로그인 테스트
    :param username: 네이버 아이디
    :param password: 네이버 비밀번호
    :param is_frequent: 자주 사용하는 아이디 여부
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # 네이버 로그인 페이지로 이동
        driver.get('https://nid.naver.com/nidlogin.login')
        
        # JavaScript를 이용한 id/pw 입력
        script_id = f'document.querySelector("#id").value="{username}"'
        script_pw = f'document.querySelector("#pw").value="{password}"'
        
        driver.execute_script(script_id)
        driver.execute_script(script_pw)
        
        # 로그인 버튼 클릭
        wait = WebDriverWait(driver, 10)
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_login'))
        )
        login_button.click()
        
        # 로그인 성공 확인
        time.sleep(3)
        
        if "otp" in driver.current_url or "2step" in driver.current_url:
            print("2단계 인증이 필요합니다.")
            return False
            
        # 로그인 후 쿠키 삭제 (1회용 아이디의 경우)
        if not is_frequent:
            driver.delete_all_cookies()
            
        return True
        
    except Exception as e:
        print(f"로그인 테스트 실패: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # 테스트 실행
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    print("1회용 아이디 로그인 테스트")
    result = test_login(USERNAME, PASSWORD, False)
    print(f"테스트 결과: {'성공' if result else '실패'}\n")
    
    print("자주 사용하는 아이디 로그인 테스트")
    result = test_login(USERNAME, PASSWORD, True)
    print(f"테스트 결과: {'성공' if result else '실패'}") 