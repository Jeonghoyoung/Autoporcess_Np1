from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

def test_post_to_cafe(username, password, cafe_url, title, content):
    """
    카페 글 작성 테스트
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--log-level=3')  # 로그 레벨 설정
    
    # 자동 로그인 방지 우회를 위한 설정 추가
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 쿠키와 캐시 유지 (선택사항)
    # options.add_argument('--user-data-dir=C:\\Path\\To\\Chrome\\Profile')
    
    # ChromeDriver 자동 설치 및 관리
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # 자동화 감지 플래그 제거
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        '''
    })
    
    try:
        # 네이버 로그인
        driver.get('https://nid.naver.com/nidlogin.login')
        
        # 로그인 페이지 로딩 대기
        time.sleep(2)
        
        # 자바스크립트 실행 전 짧은 대기 시간 추가
        time.sleep(random.uniform(1, 2))
        
        # 무작위 지연 시간을 두고 ID와 비밀번호 입력
        script_id = f'document.querySelector("#id").value="{username}"'
        script_pw = f'document.querySelector("#pw").value="{password}"'
        driver.execute_script(script_id)
        time.sleep(random.uniform(0.5, 1.5))  # 무작위 지연
        driver.execute_script(script_pw)
        time.sleep(random.uniform(0.5, 1.5))  # 무작위 지연
        
        wait = WebDriverWait(driver, 10)
        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_login')))
        login_button.click()
        time.sleep(3)
        
        # 카페로 이동
        driver.get(cafe_url)
        time.sleep(2)
        
        # 프레임 전환
        # driver.switch_to.frame('cafe_main')
        
        # 게시판 메뉴 클릭
        # menu_button = driver.find_element(By.CSS_SELECTOR, '.cafe-menu-button')
        # menu_button.click()
        # time.sleep(1)
        
        # 작성 가능한 게시판 찾기
        writable_boards = []
        board_elements = driver.find_elements(By.CSS_SELECTOR, '.cafe-menu-list a')

        for board in board_elements:
            try:
                board_url = board.get_attribute('href')
                onclick_attr = board.get_attribute('onclick')
                
                # URL이 없거나 ArticleList가 없는 경우, 또는 onclick 속성에 '-'나 '0'이 포함된 경우 제외
                if (not board_url or 'ArticleList' not in board_url or 
                    (onclick_attr and ('-' in onclick_attr or '0' in onclick_attr))):
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
        # print(writable_boards)

        # 랜덤 게시판 선택
        # selected_board = random.choice(writable_boards)
        selected_board = writable_boards[0]
        print(f"선택된 게시판: {selected_board[0]}")
        
        # 글쓰기 페이지로 이동
        driver.get(selected_board[1])
        time.sleep(2)
        
        # 프레임 전환
        driver.switch_to.frame('cafe_main')
        
        # 글쓰기 버튼 찾기 및 클릭
        try:
            write_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.post_btns a#writeFormBtn, .post_btns .btn_write, .cafe-write-btn'))
            )
            write_button.click()
            time.sleep(3)  # 페이지 전환 대기 시간 증가
            
            # 현재 URL 확인
            current_url = driver.current_url
            print(f"글쓰기 버튼 클릭 후 URL: {current_url}")
            
            # URL이 글쓰기 페이지가 아니라면 직접 URL로 이동
            if 'write' not in current_url:
                # 게시판 ID 추출
                board_id = selected_board[1].split('/')[-1]
                print(board_id)
                write_url = f"https://cafe.naver.com/ca-fe/cafes/31404847/menus/{board_id}/articles/write?boardType=L"
                print(f"글쓰기 페이지로 직접 이동: {write_url}")
                driver.get(write_url)
                time.sleep(3)
            
            # 프레임 재설정
            driver.switch_to.default_content()
            try:
                driver.switch_to.frame('cafe_main')
            except:
                pass  # 새 URL에서는 프레임이 다를 수 있음
                
        except Exception as e:
            print(f"글쓰기 버튼 클릭 중 오류: {str(e)}")
            # 직접 글쓰기 URL로 이동 시도
            write_url = f"https://cafe.naver.com/ca-fe/cafes/31404847/menus/2/articles/write?boardType=L"
            print(f"글쓰기 페이지로 직접 이동: {write_url}")
            driver.get(write_url)
            time.sleep(3)
        
        try:
            # WebDriverWait을 사용하여 제목 입력 필드가 나타날 때까지 기다립니다
            wait = WebDriverWait(driver, 10)
            
            # 여러 가능한 선택자를 시도합니다
            try:
                # 첫 번째 방법: 일반적인 제목 입력 필드 찾기
                title_area = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "textarea.textarea_input")
                ))
            except:
                try:
                    # 두 번째 방법: iframe 내부의 제목 필드 찾기
                    iframe = driver.find_element(By.CSS_SELECTOR, "iframe#cafe_main")
                    driver.switch_to.frame(iframe)
                    title_area = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "input[name='subject']")
                    ))
                except:
                    # 세 번째 방법: 다른 CSS 선택자 시도
                    title_area = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".title_inbox input, .title_area input, input.title")
                    ))
            
            # 제목 입력
            title_area.clear()
            title_area.send_keys(title)
            time.sleep(1)
            
            print("제목 입력 성공")
            
        except Exception as e:
            print(f"제목 입력 중 에러 발생: {str(e)}")
            
            # 디버깅을 위한 정보 출력
            print("현재 URL:", driver.current_url)
            print("페이지 소스 일부:", driver.page_source[:500])
            
            # 스크린샷 저장 (선택사항)
            driver.save_screenshot("error_screenshot.png")
            print("스크린샷이 저장되었습니다: error_screenshot.png")
            
            raise e
        
        # 본문 입력
        content_wait = WebDriverWait(driver, 10)
        content_div = content_wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.se-component.se-text.se-l-default'))
        )
        
        # JavaScript를 사용하여 본문 내용 입력
        driver.execute_script(
            "arguments[0].querySelector('div[contenteditable=true]').innerHTML = arguments[1];",
            content_div,
            content
        )
        
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
    USERNAME = "puwnt1114"
    PASSWORD = "tnwjdxhd12"
    CAFE_URL = "https://cafe.naver.com/pythonhy"
    TEST_TITLE = "테스트 제목입니다"
    TEST_CONTENT = "테스트 본문입니다"
    
    result = test_post_to_cafe(USERNAME, PASSWORD, CAFE_URL, TEST_TITLE, TEST_CONTENT)
    print(f"테스트 결과: {'성공' if result else '실패'}") 