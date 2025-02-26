from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
    # ChromeDriver 자동 설치 및 관리
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
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
        
        # 현재 페이지의 모든 iframe 출력
        # iframes = driver.find_elements(By.TAG_NAME, "iframe")
        # for iframe in iframes:
        #     print(f"Found iframe: {iframe.get_attribute('id')} - {iframe.get_attribute('name')}")
        
        # # 올바른 iframe ID를 찾아서 전환
        # wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))
        # driver.switch_to.frame(0)  # 첫 번째 iframe으로 전환
        
        while True:
            cafe_elements = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, '.mycafe_list .cafe_info a')
            ))
            
            for cafe in cafe_elements:
                try:
                    cafe_name = cafe.text
                    # '내가 쓴 글 보기:' 텍스트를 가진 요소는 건너뛰기
                    if cafe_name == '내가 쓴 글 보기':
                        continue
                    
                    cafe_url = cafe.get_attribute('href')
                    cafe_list.append((cafe_name, cafe_url))
                    print(f"카페 발견: {cafe_name}")
                except:
                    continue
            
            try:
                # 페이지네이션 영역에서 모든 페이지 버튼 수집
                pagination = driver.find_element(By.CLASS_NAME, 'SectionPagination')
                page_buttons = pagination.find_elements(By.CSS_SELECTOR, '.page_item')
                
                # prev, next 버튼 제외하고 숫자 버튼만 필터링
                number_buttons = []
                for button in page_buttons:
                    class_name = button.get_attribute('class')
                    if not ('prev' in class_name.lower() or 'next' in class_name.lower()):
                        number_buttons.append(button)
                
                # 현재 페이지 번호 찾기
                current_page = int(pagination.find_element(By.CSS_SELECTOR, '.page_item.isActive').text)
                
                # 다음 페이지 버튼 찾아서 클릭
                for button in number_buttons:
                    if int(button.text) == current_page + 1:
                        # JavaScript로 클릭 실행
                        driver.execute_script("arguments[0].click();", button)
                        time.sleep(random.uniform(1.5, 2.5))
                        break
                else:  # 다음 페이지를 찾지 못했을 경우
                    break
                    
            except Exception as e:
                print(f"페이지네이션 종료: {str(e)}")
                break
                
        return cafe_list
        
    except Exception as e:
        print(f"카페 목록 가져오기 실패: {str(e)}")
        return []
        
    finally:
        driver.quit()

if __name__ == "__main__":
    USERNAME = "puwnt1114"
    PASSWORD = "tnwjdxhd12"
    
    cafe_list = test_get_cafe_list(USERNAME, PASSWORD)
    print(f"\n총 {len(cafe_list)}개의 카페를 찾았습니다.")
    for i, (name, url) in enumerate(cafe_list, 1):
        print(f"{i}. {name}: {url}") 