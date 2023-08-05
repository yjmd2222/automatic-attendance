# Fake attendance script for you-know-what

# 실행 방법
## 윈도우
`info_template.py` 파일 이름 `info.py`로 변경 후 카카오 로그인 정보 및 줌 링크 입력. 줌 링크는 `#success` 제외하고 입력합니다.

리포 로컬로 클론(`git clone https://github.com/yjmd2222/fake-attendance`)한 후 터미널에 `pip install -r requirements.txt` 입력해서 필요 모듈 설치

터미널에 `python -m fake_attendance` 입력해서 실행. 현재 프로젝트 기간이므로 `python -m fake_attendance -p 'project section'` 입력으로 프로젝트 기간에 맞는 스케줄러 실행
## 맥
`info_template.py` 파일 이름 `info.py`로 변경 후 카카오 로그인 정보 및 줌 링크 입력. 줌 링크는 `#success` 제외하고 입력합니다.

리포 로컬로 클론(`git clone https://github.com/yjmd2222/fake-attendance`)한 후 `macos` 브랜치로 이동(`git checkout macos`). `pip install -r requirements.txt` 입력해서 필요 모듈 설치

터미널에 `python -m fake_attendance` 입력해서 실행. 현재 프로젝트 기간이므로 `python -m fake_attendance -p 'project section'` 입력으로 프로젝트 기간에 맞는 스케줄러 실행

# 커맨드
스크립트 실행 중 아래 커맨드 입력해서 강제 스케줄 실행 가능
- 줌 실행: `Ctrl + Alt + L`
- QR 체크인: `Ctrl + Alt + C`
- 줌 종료: `Ctrl + Alt + Q`
- 스케줄러 종료: `Ctrl + Alt + E`
