from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def test_post_to_cafe(username, password, cafe_url, title, content):
    """
    카페 글 작성 테스트
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    
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
        
        # 카페로 이동
        driver.get(cafe_url)
        time.sleep(2)
        
        # 프레임 전환
        driver.switch_to.frame('cafe_main')
        
        # 게시판 메뉴 클릭
        menu_button = driver.find_element(By.CSS_SELECTOR, '.cafe-menu-button')
        menu_button.click()
        time.sleep(1)
        
        # 작성 가능한 게시판 찾기
        writable_boards = []
        board_elements = driver.find_elements(By.CSS_SELECTOR, '.cafe-menu-list a')
        
        for board in board_elements:
            try:
                board_url = board.get_attribute('href')
                if not board_url or 'ArticleList' not in board_url:
                    continue
                    
                board.click()
                time.sleep(1)
                
                write_button = driver.find_elements(By.CSS_SELECTOR, '.cafe-write-btn')
                if write_button:
                    writable_boards.append((board.text, board_url))
            except:
                continue
        
        if not writable_boards:
            raise Exception("작성 가능한 게시판이 없습니다.")
        
        # 랜덤 게시판 선택
        selected_board = random.choice(writable_boards)
        print(f"선택된 게시판: {selected_board[0]}")
        
        # 글쓰기 페이지로 이동
        driver.get(selected_board[1])
        time.sleep(1)
        driver.switch_to.frame('cafe_main')
        
        write_button = driver.find_element(By.CSS_SELECTOR, '.cafe-write-btn')
        write_button.click()
        time.sleep(2)
        
        # 제목 입력
        title_input = driver.find_element(By.CSS_SELECTOR, '.textarea_input')
        title_input.send_keys(title)
        
        # 본문 입력
        driver.switch_to.frame('se2_iframe')
        body = driver.find_element(By.CSS_SELECTOR, 'body#editorBody')
        body.send_keys(content)
        
        # 프레임 복귀 및 등록
        driver.switch_to.default_content()
        driver.switch_to.frame('cafe_main')
        submit_button = driver.find_element(By.CSS_SELECTOR, '.BaseButton')
        submit_button.click()
        
        return True
        
    except Exception as e:
        print(f"카페 글 작성 실패: {str(e)}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    USERNAME = "your_username"
    PASSWORD = "your_password"
    CAFE_URL = "your_cafe_url"
    TEST_TITLE = "테스트 제목입니다"
    TEST_CONTENT = "테스트 본문입니다"
    
    result = test_post_to_cafe(USERNAME, PASSWORD, CAFE_URL, TEST_TITLE, TEST_CONTENT)
    print(f"테스트 결과: {'성공' if result else '실패'}") 