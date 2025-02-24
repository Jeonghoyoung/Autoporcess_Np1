from PyQt5 import QtWidgets
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import random

# MAC : pyinstaller --onefile --windowed --name "네이버자동화" --target-architecture arm64 main.py
# WINDOW : pyinstaller --onefile --windowed --name "네이버자동화" --target-architecture x64 main.py

class NaverAutomationApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cafe_list = []  # 가입된 카페 목록 저장
        self.selected_cafes = []  # 선택된 카페 목록
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Naver Automation')

        # 레이아웃 설정
        layout = QtWidgets.QVBoxLayout()

        # 아이디 입력 위젯
        self.idInput = QtWidgets.QLineEdit(self)
        self.idInput.setPlaceholderText("아이디를 입력하세요")
        layout.addWidget(self.idInput)

        # 비밀번호 입력 위젯
        self.pwInput = QtWidgets.QLineEdit(self)
        self.pwInput.setPlaceholderText("비밀번호를 입력하세요")
        self.pwInput.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.pwInput)

        # 로그인 옵션 토글 버튼
        self.loginToggle = QtWidgets.QCheckBox('자주 사용하는 아이디로 로그인', self)
        layout.addWidget(self.loginToggle)

        # 제목 입력 위젯 추가
        self.titleEdit = QtWidgets.QLineEdit(self)
        self.titleEdit.setPlaceholderText("제목을 입력하세요...")
        layout.addWidget(self.titleEdit)

        # 본문 입력 위젯
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setPlaceholderText("여기에 글을 작성하세요...")
        layout.addWidget(self.textEdit)

        # 작업 유형 선택
        self.workTypeGroup = QtWidgets.QGroupBox("작업 유형")
        workTypeLayout = QtWidgets.QVBoxLayout()
        
        self.oneTimeRadio = QtWidgets.QRadioButton("1회용 아이디 작업")
        self.frequentRadio = QtWidgets.QRadioButton("자주 사용하는 아이디 작업")
        workTypeLayout.addWidget(self.oneTimeRadio)
        workTypeLayout.addWidget(self.frequentRadio)
        self.workTypeGroup.setLayout(workTypeLayout)
        layout.addWidget(self.workTypeGroup)

        # 작업 설정
        settingsGroup = QtWidgets.QGroupBox("작업 설정")
        settingsLayout = QtWidgets.QGridLayout()

        self.cafeCountSpinBox = QtWidgets.QSpinBox()
        self.cafeCountSpinBox.setRange(1, 100)
        self.postCountSpinBox = QtWidgets.QSpinBox()
        self.postCountSpinBox.setRange(1, 10)
        
        settingsLayout.addWidget(QtWidgets.QLabel("카페 방문 횟수:"), 0, 0)
        settingsLayout.addWidget(self.cafeCountSpinBox, 0, 1)
        settingsLayout.addWidget(QtWidgets.QLabel("글 작성 횟수:"), 1, 0)
        settingsLayout.addWidget(self.postCountSpinBox, 1, 1)
        
        settingsGroup.setLayout(settingsLayout)
        layout.addWidget(settingsGroup)

        # 카페 목록 표시 위젯
        self.cafeListWidget = QtWidgets.QListWidget()
        self.cafeListWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )
        layout.addWidget(self.cafeListWidget)

        # 블로그 작성 옵션
        self.blogCheckBox = QtWidgets.QCheckBox("블로그에도 동일하게 작성")
        layout.addWidget(self.blogCheckBox)

        # 버튼들
        buttonLayout = QtWidgets.QHBoxLayout()
        self.getCafesButton = QtWidgets.QPushButton('가입 카페 가져오기')
        self.getCafesButton.clicked.connect(self.get_joined_cafes)
        self.loginAndPostButton = QtWidgets.QPushButton('작업 시작')
        self.loginAndPostButton.clicked.connect(self.start_automation)
        
        buttonLayout.addWidget(self.getCafesButton)
        buttonLayout.addWidget(self.loginAndPostButton)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.show()

    def login_naver(self, driver, username, password):
        try:
            # 네이버 로그인 페이지로 이동
            driver.get('https://nid.naver.com/nidlogin.login')
            
            # JavaScript를 이용한 id/pw 입력 (자동입력 방지 우회)
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
            try:
                wait.until(
                    lambda driver: driver.current_url != 'https://nid.naver.com/nidlogin.login'
                )
            except:
                raise Exception("로그인 실패: 타임아웃")
            
            # 2단계 인증이나 보안 확인이 있는 경우 처리
            if "otp" in driver.current_url or "2step" in driver.current_url:
                raise Exception("2단계 인증이 필요합니다. 먼저 브라우저에서 직접 로그인해주세요.")
            
            # 로그인 후 쿠키 설정 대기
            time.sleep(3)
            
        except Exception as e:
            print(f"로그인 중 오류 발생: {str(e)}")
            raise

    def get_joined_cafes(self):
        """가입된 카페 목록을 크롤링하여 가져옵니다."""
        username = self.idInput.text()
        password = self.pwInput.text()
        
        if not self._validate_credentials(username, password):
            return

        driver = self._create_driver()
        try:
            self._fetch_cafe_list(driver, username, password)
            self._update_cafe_list_widget()
        except Exception as e:
            self._show_error_message(str(e))
        finally:
            driver.quit()

    def _validate_credentials(self, username, password):
        """로그인 정보 유효성을 검사합니다."""
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, '경고', '아이디와 비밀번호를 입력하세요.')
            return False
        return True

    def _create_driver(self):
        """웹드라이버를 생성합니다."""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(options=options)

    def _fetch_cafe_list(self, driver, username, password):
        """카페 목록을 가져옵니다."""
        self.login_naver(driver, username, password)
        
        # 내 카페 페이지로 이동
        driver.get('https://cafe.naver.com/')
        time.sleep(2)
        
        # 내 카페 버튼 클릭
        wait = WebDriverWait(driver, 10)
        my_cafe_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn_my_setting')))
        my_cafe_btn.click()
        time.sleep(2)
        self.cafe_list = []
        
        # 프레임 전환
        driver.switch_to.frame('cafe_main')
        
        while True:
            # 카페 목록 요소들 찾기
            cafe_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.mycafe_list .cafe_info a')))
            
            for cafe in cafe_elements:
                try:
                    cafe_name = cafe.text
                    cafe_url = cafe.get_attribute('href')
                    self.cafe_list.append((cafe_name, cafe_url))
                except:
                    continue
            
            # 다음 페이지 확인
            try:
                # 다음 페이지 버튼 찾기 및 클릭
                next_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.SectionPagination .page_item:not(.isActive)'))
                )
                if next_button.is_displayed() and next_button.is_enabled():
                    next_button.click()
                    time.sleep(random.uniform(1.5, 2.5))  # 랜덤 대기 시간 추가
                else:
                    break
            except Exception as e:
                print(f"다음 페이지 이동 중 오류 발생: {str(e)}")
                break
        # 기본 프레임으로 복귀
        driver.switch_to.default_content()

    def _process_cafe_elements(self, cafe_elements):
        """카페 요소들을 처리합니다."""
        for cafe in cafe_elements:
            cafe_name = cafe.text
            cafe_url = cafe.get_attribute('href')
            self.cafe_list.append((cafe_name, cafe_url))

    def _go_to_next_page(self, driver):
        """다음 페이지로 이동을 시도합니다."""
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, '.SectionPagination a.next')
            next_page.click()
            time.sleep(2)
            return True
        except:
            return False

    def _update_cafe_list_widget(self):
        """UI의 카페 목록을 업데이트합니다."""
        self.cafeListWidget.clear()
        for cafe_name, _ in self.cafe_list:
            self.cafeListWidget.addItem(cafe_name)

    def _show_error_message(self, error_message):
        """에러 메시지를 표시합니다."""
        QtWidgets.QMessageBox.warning(self, '오류', f'카페 목록 가져오기 실패: {error_message}')

    def post_to_blog(self, driver, content, username):
        """블로그에 글을 작성합니다."""
        try:
            driver.get(f'https://blog.naver.com/{username}/postwrite')
            time.sleep(3)

            # iframe 전환
            driver.switch_to.frame('mainFrame')
            
            # 제목 입력
            title_input = driver.find_element(By.CSS_SELECTOR, '.se-text-input')
            title_input.send_keys(self.titleEdit.text())

            # 본문 입력
            content_iframe = driver.find_element(By.CSS_SELECTOR, '.se-iframe')
            driver.switch_to.frame(content_iframe)
            body = driver.find_element(By.CSS_SELECTOR, 'body')
            body.send_keys(content)
            
            # 기본 프레임으로 복귀
            driver.switch_to.default_content()
            driver.switch_to.frame('mainFrame')

            # 발행 버튼 클릭
            publish_button = driver.find_element(By.CSS_SELECTOR, '.publish_button')
            publish_button.click()
            time.sleep(2)

        except Exception as e:
            print(f"블로그 작성 중 오류 발생: {str(e)}")
            raise

    def start_automation(self):
        """선택된 옵션에 따라 자동화를 시작합니다."""
        title = self.titleEdit.text()
        content = self.textEdit.toPlainText()
        username = self.idInput.text()
        password = self.pwInput.text()
        
        if not title or not content or not username or not password:
            QtWidgets.QMessageBox.warning(self, '경고', '모든 필드를 입력하세요.')
            return

        selected_items = self.cafeListWidget.selectedItems()
        if not selected_items:
            QtWidgets.QMessageBox.warning(self, '경고', '카페를 선택하세요.')
            return

        driver = webdriver.Chrome()
        try:
            self.login_naver(driver, username, password)
            
            # 선택된 카페들에 대해 작업 수행
            for _ in range(self.postCountSpinBox.value()):
                for item in selected_items:
                    cafe_url = next(url for name, url in self.cafe_list if name == item.text())
                    self.post_to_cafe(driver, cafe_url, content)
                    
                    if self.blogCheckBox.isChecked():
                        self.post_to_blog(driver, content)
                    
                    time.sleep(2)

            if not self.frequentRadio.isChecked():
                driver.delete_all_cookies()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, '오류', f'작업 중 오류 발생: {str(e)}')
        finally:
            driver.quit()

    def post_to_cafe(self, driver, cafe_url, content):
        """카페에 글을 작성합니다. 작성 가능한 게시판 중 랜덤으로 선택합니다."""
        try:
            driver.get(cafe_url)
            time.sleep(2)

            # 카페 메인 프레임으로 전환
            driver.switch_to.frame('cafe_main')

            # 게시판 메뉴 버튼 클릭
            menu_button = driver.find_element(By.CSS_SELECTOR, '.cafe-menu-button')
            menu_button.click()
            time.sleep(1)

            # 작성 가능한 게시판 목록 수집
            writable_boards = []
            board_elements = driver.find_elements(By.CSS_SELECTOR, '.cafe-menu-list a')
            
            for board in board_elements:
                try:
                    # 게시판 링크 확인
                    board_url = board.get_attribute('href')
                    if not board_url or 'ArticleList' not in board_url:
                        continue

                    # 게시판 클릭
                    board.click()
                    time.sleep(1)

                    # 글쓰기 버튼 존재 여부 확인
                    write_button = driver.find_elements(By.CSS_SELECTOR, '.cafe-write-btn')
                    if write_button:
                        writable_boards.append((board.text, board_url))
                except:
                    continue

            if not writable_boards:
                raise Exception("작성 가능한 게시판이 없습니다.")

            # 랜덤하게 게시판 선택
            selected_board = random.choice(writable_boards)
            print(f"선택된 게시판: {selected_board[0]}")

            # 선택된 게시판으로 이동
            driver.get(selected_board[1])
            time.sleep(1)
            driver.switch_to.frame('cafe_main')

            # 글쓰기 버튼 클릭
            write_button = driver.find_element(By.CSS_SELECTOR, '.cafe-write-btn')
            write_button.click()
            time.sleep(2)

            # 제목 입력
            title_input = driver.find_element(By.CSS_SELECTOR, '.textarea_input')
            title_input.send_keys(self.titleEdit.text())

            # 본문 프레임으로 전환
            driver.switch_to.frame('se2_iframe')
            
            # 본문 입력
            body = driver.find_element(By.CSS_SELECTOR, 'body#editorBody')
            body.send_keys(content)

            # 기본 프레임으로 복귀
            driver.switch_to.default_content()
            driver.switch_to.frame('cafe_main')

            # 등록 버튼 클릭
            submit_button = driver.find_element(By.CSS_SELECTOR, '.BaseButton')
            submit_button.click()
            time.sleep(2)

        except Exception as e:
            print(f"카페 글 작성 중 오류 발생: {str(e)}")
            raise

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = NaverAutomationApp()
    sys.exit(app.exec_()) 