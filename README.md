[![Total clone count](https://img.shields.io/badge/dynamic/json?color=green&label=Total%20clones&query=count&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/clones.json&logo=github)](#)[![Unique clone count](https://img.shields.io/badge/dynamic/json?color=blue&label=Unique&query=uniques&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/clones.json)](#)[![Today's clone count](https://img.shields.io/badge/dynamic/json?color=purple&label=Today%27s%20clones&query=clones[0][%27count%27]&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/clones.json)](#)

[![Total view count](https://img.shields.io/badge/dynamic/json?color=yellow&label=Total%20views&query=count&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/views.json&logo=github)](#)[![Unique view count](https://img.shields.io/badge/dynamic/json?color=indigo&label=Unique&query=uniques&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/views.json)](#)[![Today's clone count](https://img.shields.io/badge/dynamic/json?color=orange&label=Today%27s%20views&query=views[0][%27count%27]&url=https://raw.githubusercontent.com/yjmd2222/fake-attendance/stats/views.json)](#)

[![Last updated](https://img.shields.io/badge/기본_기능_개발_기간-2023--06--02~2023--06--10-blue)](#)

# 자동 출석 프로그램
특정 개발자 교육 기관에서 매일 진행하는 출석 절차를 자동화하는 프로그램.

**주의**: 교육용 목적으로만 사용하고, 학습과정에 참여하지 않고 자리를 비운 상태에서 대리출석은 하지 않길 바랍니다.

| ![프로그램 & Zoom 실행](images/gif-Zoom실행.gif) | 
|:--:| 
| 프로그램 & Zoom 실행 |

| ![QR 체크인: 성공](images/gif-QR.gif) | 
|:--:| 
| QR 체크인: 성공 |

| ![QR 체크인: QR 없음](images/gif-QR없음.gif) | 
|:--:| 
| QR 체크인: QR 없음 |

| ![Zoom 종료](images/gif-Zoom종료.gif) | 
|:--:| 
| Zoom 종료 |

| <img src="images/이메일-Zoom실행.png" alt="이메일-Zoom 실행" width="400"/> | <img src="images/이메일-QR.png" alt="이메일-QR" width="400"/> | <img src="images/이메일-Zoom종료.png" alt="이메일-Zoom 종료" width="400"/> |
|:--:|:--:|:--:| 
| 이메일-Zoom 실행 | 이메일-QR 체크인 | 이메일-Zoom 종료 |

## Archived
[![Last updated](https://img.shields.io/badge/Last_updated-2023--10--05-yellow)](#)

해당 교육기관에서 수료한 관계로 더 이상 이 프로젝트를 maintain하지 않게 되었습니다.

## 작은 메시지
2023-07-03로서 프로젝트는 매우 완성도 높은 상태라고 할 수 있습니다. 물론 맥OS이 제가 주로 사용하는 운영체제가 아니기 때문에 Zoom 자체 업데이트에 대응할 기회가 별로 없었고, 업데이트 관련 화면 인식 관련사항으로 해당 이미지를 교체해야 합니다. 현재로서는 이 이미지들이 모두 자리표시자/placeholder 이미지입니다. 코딩 실력 향상을 위해 추상화나 운영체제 지원 확장을 적용하는 단계로서 실질적인 기능과 관계 없이 효율성 관련 내용으로 프로그램을 업데이트 하고 있는데, 혹시 편리성이나 추가할만한 기능이 있다면 Discussions에 남겨주시면 감사하겠습니다. 혹시 기능적 결함을 발견하거나 맥OS 사용 개선, 또는 화면 인식 관련해서 업데이트 할 부분에 적극적으로 설명이 가능하신 분은 새로운 Issue를 작성해주시기 바랍니다.

## 사용 도구 및 스킬
이 프로젝트를 진행하면서 다음의 도구 사용법과 스킬을 터득했습니다. 코드 내에 최대한 자세히 설명을 기재했지만, 최초 작성시 영어로 작성하여 현재로서 설명이 전부 영어입니다. 최신 개발 트렌드에 맞고 빠른 이해를 위해 ChatGPT를 사용해서 확인하시기 바랍니다.

| 항목 | 적용점|
| - | - |
| Selenium | 웹 상에서 출석 절차 진행 |
| APScheduler | 해당 시간에 Zoom 실행, 종료, QR 출석, 스스로 종료 |
| smtplib | 프로그램 진행 상황 이메일로 보고 |
| argparse | 스케줄 선택 |
| Win32 API/pywinauto | 윈도우 운영체제 Zoom 창 관리 |
| AppleScript/subprocess | 맥OS Zoom 창 관리 |
| PyAutoGUI | Selenium 및 AppleScript 접근 불가 항목 화면 인식으로 관리 |
| pynput | 키보드 입력 자동화 및 사용자 명령어 관리 |
| 객체지향 프로그래밍 | 기능 세분화, 다중상속, 그리고 데코레이터(decorator)로 코드 디자인 개선 |
| 오류 핸들링 | 현재까지 확인한 모든 오류 예외 처리로 대응 |
| 병렬화 | APScheduler와 pynput로 기능 병렬 실행 및 실행 중 키보드 인식기능 연구 |
| Github Actions/YML | 코드 오류와 표준 확인 및 이 프로젝트 방문 횟수 확인 |
| Git 브랜치 | 코드 버전 관리 및 Github Actions 연계로 상단에 배지로 방문 횟수 표기 |

## 사전 요구사항
| 항목 | 기본 조건 |
| - | - |
| 운영체제 | 윈도우 10 이상 또는 맥OS Ventura(13) 이상 |
| 프로그램 언어 | Python 3 |
| 가상 환경 | Anaconda |
| Zoom | 최신 버전 |

있는 그대로 활용한다면 한글로 기본 세팅된 윈도우 11이나 맥OS Ventura를 추천합니다. 다른 운영체제의 경우 화면 인식이나 설정을 별도로 적용해야 할 수도 있습니다. 화면 인식 관련해서 [images](images)를 확인해보세요.

Python 3 환경에서 다음 명령어를 통해 필수 패키지를 설치합니다. 세부 버전으로 Python 3.11.3을 추천합니다.
- Note: M1 맥이나 Miniforge 환경에서는 `pyautogui` 관련 import 오류가 있는 것으로 파악됩니다. Anaconda 전체를 설치한 경우 오류가 없는 것으로 파악되며, 따라서 설치 환경에 주의해주시기 바랍니다.

`pip install -r requirements.txt`

[info_template.py](auto_attendance/info_template.py)에 있는 개인정보 변수에 본인의 카카오 로그인, 이메일 로그인, 그리고 Zoom URL 주소를 입력합니다. 이 때 Zoom 주소는 끝에 `#success`가 명시되어 있는지 확인합니다. 파일 이름을 `info.py`로 변경합니다. Python에서 이메일 발송하는 방법은 다음 블로그를 확인해주세요: 코딩유치원 [블로그](https://coding-kindergarten.tistory.com/204).

참고: 아래 [프로그램 사용 방법](#프로그램-사용-방법)에서 만약 본 모듈이 사용하는 [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln)의 소스파일이 자동적으로 다운로드 되지 않는다면 직접 다운로드 받으셔야 합니다. 다음의 내용에서 수동 다운로드 방법을 확인해주세요.
- .crx 다운로드 방법: https://crx-downloader.com/how-it-works
- 다운로드시 입력할 Screen QR Reader URL 주소: https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln

추가 참고사항: 맥 사용자는 Zoom 창 제어를 위해 모듈을 실행하는 환경(터미널, 개발환경)에 대해 Zoom과 System Events에 대해 권한 부여가 필요할 수도 있습니다. `시스템 설정` - `개인정보 보호 및 보안` - `자동화`에서 권한을 확인해보세요.

## 프로그램 사용 방법
다음 명령으로 모든 기능을 수행합니다: `python -m auto_attendance` 후술할 [기능 안내 및 프로젝트 기획 배경](#기능-안내-및-프로젝트-기획-배경)에서 추가 설명 확인이 가능합니다.

출석 인증 스케줄을 변경하려면 다음 중 하나의 인수(argument)를 추가할 수 있습니다:
- `-p`: optional argument, 아래 중 하나를 사용하세요. (실제 스케줄은 [settings.py](auto_attendance/settings.py)를 확인하세요.) 예시: `python -m auto_attendance -p 'project section'`
    - `'regular'`: 학습기간 학습일
    - `'sprint challenge'`: 학습기간 시험일
    - `'project day 1'`: 학습기간 프로젝트 1일차
    - `'project days 2-5'`: 학습기간 프로젝트 2-5일차
    - `'section review day 1'`: 학습기간 섹션 리뷰 1일차
    - `'section review day 2'`: 학습기간 섹션 리뷰 2일차
    - `'project section'`: 프로젝트 기간
- `-t`: optional argument, [test_times.txt](test_times.txt)와 같이 24시간 형식의 시간 설정이 포함된 텍스트 파일을 사용하세요. 예시: `python -m auto_attendance -t test_times.txt`
- position argument: `10:00 15:00`과 같이 실제 인증 시간을 입력하세요. 예시: `python -m auto_attendance 10:30 14:50`

인수를 비워두면 `'regular'` 인수와 동일한 스케줄로 프로그램이 실행됩니다.

입력 인수에 대한 자세한 설명을 보려면 `python -m auto_attendance -h`를 입력하세요. 인수는 위에 나열된 순서대로 인식되며 올바르게 전달된 경우 다른 인수는 무시됩니다.

프로그램 실행 중 강제 작동 기능을 위해 키보드로 다음을 입력할 수 있습니다. 처음 네 개의 커맨드는 다른 작업 중에도(실행 터미널 밖에서도) 작동하고, 마지막 커맨드는 터미널 안에서만 작동합니다.
- `Ctrl + Alt(command) + Shift + L`: Zoom 실행
- `Ctrl + Alt(command) + Shift + C`: QR 코드 출석
- `Ctrl + Alt(command) + Shift + Q`: 줌 종료
- `Ctrl + Alt(command) + Shift + E`: 프로그램 종료
- `Ctrl + C`: 프로그램 종료

## 기능 안내 및 프로젝트 기획 배경
[![Last updated](https://img.shields.io/badge/Last_updated-2023--08--08-blue)](#)

이 모듈은 출석을 자동화합니다: Zoom 입장 및 퇴장 시간에 맞춰서 Zoom을 실행 및 종료하고, 출석 QR 코드(앱 입실과 퇴실이 아닌 교육기관 중간 출석 확인입니다.)를 스캔하여 출석을 완료합니다. 출석 확인은 출석 시간에 맞추어 실행됩니다. 실제 타이밍은 [settings.py](auto_attendance/settings.py)를 확인하세요.

그래서 제가 왜 이런 것을 만들었을까요? 제 온라인 수업의 운영 정책으로 출석 확인을 위해 오전 9시부터 오후 6시까지(점심 시간인 12시부터 1시는 제외) 항상 카메라를 켜고 책상에 앉아 있어야 했습니다. 또한 출석 QR 코드를 출석 시간에 Zoom 화면에 띄워 수강생으로 출석을 입력하도록 했습니다. 똑같은 일정에 따라 매번 동일한 절차를 밟아야 하는 것은 번거로울 수 있습니다. 이 문제를 개선하고자 이 프로젝트를 시작하게 되었습니다. 도중 운영 정책 변경으로 카메라를 켜지 않는 것을 허용하게 되었는데, 삭제된 카메라 켜는 부분은 [archive/turn_on_video.py](archive/turn_on_video.py)에서 확인 가능하며, 다른 부분에서 교체되어 사용하지 않는 기능과 파일 또한 [archive](archive)에서 확인 가능합니다.

## 제한점 및 회고
교육과정 중 Selenium, 자동화, 그리고 API에 대해 배운 부분이 있습니다. 이 프로그램은 배운 내용을 일상에 적용한 작은 프로젝트입니다. 또한 시작한 이상 적극적으로 프로그램을 개선하면서 효율적인 코드 관리 및 실행을 위해 객체지향 프로그래밍 방법도 적용하고, 강제 작동 기능 추가를 위해 키보드 커맨드 입력도 연구했으며, 윈도우에서만이 아니라 다른 운영체제를 사용하는 수강생에게 프로그램 제공하고 멀티 OS(OS-agnostic) 프로그램/모듈 배포 관련사항을 공부하기 위해 맥OS 확장도 적용했습니다. 다른 시각에서 바라보자면, 데이터 직군 교육생으로서 데이터 관련사항으로는 데이터 자동 접속과 수집/스크레이핑 기능을 제공하는 Selenium을 공부하고, 그 수집을 주기적으로 실행할 수 있는 APScheduler를 적극적으로 배울 수 있었습니다.

물론 제한점도 있습니다. 현재 스마트폰으로 출석을 인증해야 하는 앱 입실과 퇴실은 자동화하지 못하고 있습니다. 한 가지 방법으로는, 스마트폰의 카메라의 촬영화면을 QR이 포함된 가상화면으로 인식시키는 것인데, 제가 사용중인 iPhone은 정상적인 방법으로 카메라 촬영화면을 교체할 수 있는 공개된 모듈이 없습니다. 또한 현재로서는 하나의 인증된 스마트폰으로만 앱 입/퇴실이 가능하기 때문에 가상스마트폰을 이용하는 것도 인증의 문제에 있어서 제한됩니다. 추후 합법적인 방법의 공개 모듈을 발견한다면 적용해볼 수 있겠습니다.

이러한 제한점을 제외하더라도 개인적인 작은 아이디어에서 시작해서 모두가 편리하게 사용할 수 있는 프로그램을 작성했습니다. 물론 교육기관과 교육기관의 소속 단체에서 제한을 걸 수 있기 때문에 적극적으로 이 프로그램을 밝히진 않았고, 따라서 많은 피드백은 없습니다. 하지만 코드 작성 실력을 쌓고 일상에서 스스로에게 필요한 부분을 인지하고 작성했다는 부분을 돌아보며, 많은 것을 스스로, 그리고 적극적으로 배웠다고 생각합니다. 앞으로도 자신감을 갖고 새로운 아이디어로 무엇이든 도전할 수 있다고 생각합니다.

## Credits
- 해당 교육기관: 출석 인증 절차 도입으로 본 프로젝트 아이디어 제공
- tkobayashi0111: [Screen QR Reader](https://chrome.google.com/webstore/detail/screen-qr-reader/ekoaehpknadfoaolagjfdefeopkhfhln) 제공
- yjmd2222: 프로젝트의 유일 구성원으로서 기획, 개발, 그리고 끝내 완성 :)

## License
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Apache 2.0 라이선스 적용
