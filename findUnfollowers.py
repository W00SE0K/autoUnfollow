import instaloader
import pandas as pd

L = instaloader.Instaloader()

# 여기에 본인의 아이디/비번 입력하세요
username = 'your_instagram_username'
password = 'your_instagram_password'

def login_with_2fa():
    print("2단계 인증이 필요합니다. 인증 코드를 입력하세요.")
    two_factor_code = input("2FA 코드: ")
    L.login(username, password, verification_code=two_factor_code)
    L.save_session_to_file()

try:
    print("기존 세션 로드 시도 중...")
    L.load_session_from_file(username)
    print("세션 로드 완료")
except FileNotFoundError:
    print("새로 로그인 중...")
    try:
        L.login(username, password)
        L.save_session_to_file()
        print("로그인 완료 및 세션 저장")
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        login_with_2fa()
        print("2단계 인증 완료 및 세션 저장")

print("프로필 로딩 중...")
profile = instaloader.Profile.from_username(L.context, username)
print(f"프로필 '{username}' 로딩 완료")

print("팔로잉 목록 수집 중...")
following_list = [followee.username for followee in profile.get_followees()]
print(f"팔로잉 목록 수집 완료: {len(following_list)}명")

print("팔로워 목록 수집 중...")
follower_list = [follower.username for follower in profile.get_followers()]
print(f"팔로워 목록 수집 완료: {len(follower_list)}명")


print("팔로우하지만 팔로우하지 않는 사용자 찾기 중...")
not_following_back = set(following_list) - set(follower_list)

#공식 계정 배제 위한 설정 
print("팔로워 수가 1만 명 이상인 사용자 제외 중...")
filtered_not_following_back = []
for username in not_following_back:
    user_profile = instaloader.Profile.from_username(L.context, username)
    if user_profile.followers < 10000:
        filtered_not_following_back.append(username)


df = pd.DataFrame(filtered_not_following_back, columns=['Username'])
df.to_excel('filtered_not_following_back.xlsx', index=False)
print("엑셀 파일로 저장 완료: filtered_not_following_back.xlsx")

unfollow_choice = input("이 사용자들을 언팔로우 하시겠습니까? (y/n): ").strip().lower()
if unfollow_choice == 'y':
 
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import time

    def unfollow_user(driver, user):
        driver.get(f'https://www.instagram.com/{user}/')
        time.sleep(3)
        
        try:
            unfollow_button = driver.find_element(By.XPATH, '//button[text()="Following"]')
            unfollow_button.click()
            time.sleep(1)
            
            confirm_button = driver.find_element(By.XPATH, '//button[text()="Unfollow"]')
            confirm_button.click()
            print(f'언팔로우 완료: {user}')
        except Exception as e:
            print(f'언팔로우 실패 ({user}): {e}')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    username_input = driver.find_element(By.NAME, 'username')
    password_input = driver.find_element(By.NAME, 'password')
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    time.sleep(10)

    for user in filtered_not_following_back:
        unfollow_user(driver, user)
        time.sleep(2)  

    driver.quit()
