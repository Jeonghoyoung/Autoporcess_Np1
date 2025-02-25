from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def test_get_cafe_list(username, password):
    """
    가입된 카페 목록 가져오기 테스트
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    cafe_list = []
    
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
        
        # 카페 메인으로 이동
        driver.get('https://cafe.naver.com/')
        time.sleep(2)
        
        # 내 카페 버튼 클릭
        my_cafe_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_my_setting')))
        my_cafe_btn.click()
        time.sleep(2)
        
        # 프레임 전환
        driver.switch_to.frame('cafe_main')
        
        while True:
            cafe_elements = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.mycafe_list .cafe_info a')
            ))
            
            for cafe in cafe_elements:
                try:
                    cafe_name = cafe.text
                    cafe_url = cafe.get_attribute('href')
                    cafe_list.append((cafe_name, cafe_url))
                    print(f"카페 발견: {cafe_name}")
                except:
                    continue
            
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '.SectionPagination .page_item:not(.isActive)')
                    )
                )
                if next_button.is_displayed() and next_button.is_enabled():
                    next_button.click()
                    time.sleep(random.uniform(1.5, 2.5))
                else:
                    break
            except:
                break
                
        return cafe_list
        
    except Exception as e:
        print(f"카페 목록 가져오기 실패: {str(e)}")
        return []
        
    finally:
        driver.quit()

if __name__ == "__main__":
    USERNAME = "your_username"
    PASSWORD = "your_password"
    
    cafe_list = test_get_cafe_list(USERNAME, PASSWORD)
    print(f"\n총 {len(cafe_list)}개의 카페를 찾았습니다.")
    for i, (name, url) in enumerate(cafe_list, 1):
        print(f"{i}. {name}: {url}") 