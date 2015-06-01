:::ROS 세미나 정리

## 1 세션 :: ROS 개론
-모든 로봇 플랫폼으로 거의다 사용하고 있다고 보면됨. 
-로봇을 하는데 ROS를 사용하지 않는것은 영상처리를 하는데 OPEN CV를 안하는것과 같다고 보면됨.
- H/W -OS -App 독립적인 분리가 가능.

- 로봇 플랫폼 종류
	Open RT : 일본에서 많이 사용.
	Oppros
	evolution robitics
	오포로스 (유럽)
	URBi
	NAO qi : 소뱅 페퍼에 적용된 플랫폼. (Open 아님)
- ROS 진정한 목적
	로봇 S/W개발을 전세계 레벨에서 공동작업 가능하도록 환경을 구축하는 것.
- BSD 라이센스 사용
- ROS는 메타 운영체제
	-> 로봇 응용 프로그램을 위한 S/W프레임 워크 개념.
- 모든 운영체제에 포팅 가능, 아두이노도 가능( 통신 가능하도록 프로토콜만 맞춘 정도) 이 기종간의 통신 지원.
- 생태계 
	- 위키 페이지 14697페이지 - 가장 강력한 특징.
	- 릴리즈 1년에 한번, (현재 Indifo추천 - 우분투 14.04 추천)
	- 설치 - 스크립트 두줄로 가능.
- 용어
	Node - 실행가능한 프로세스
	Package - 노드의 묶음
	Message - 노드간의 통신        +-----[Master]--+
	Topic, Publisher, Subscriber  [P] -----(T)----> [S]
				      엔코더 위치정보  SLAM
	
- ROS Tool 
	3차원 모델링, 시뮬레이션 가능
	(asus action - 키넥트 비슷)
	RViz 3차원 시각화 시스템 플러그인
	로봇 모션 플래닝 가능 

## 2 세션 :: Python 으로 하는 ROS (ROSPy)
유진로봇 이지훈 

- 파이썬 디자인 철학 - 이 철학 기반으로 설계됨.
- 빠른 프로토타이핑 할때도 유용.
- ROS 프로그래밍 하기.
	ROSPy 패키지 만들기
		-package.xml, CmakeList.txt, setup.py
	uvc_camera : 디바이스드라이버?
	기본적으로 node가 독립적이기 때문에 터미널을 많이 띄우게 됨.
- 예제 twist github에서 코드 볼수 있음.( @jihoonl)
- 파이선 코딩 스타일 가이드. 
	wiki.ros.orh/PyStyleGuide
Pocket sphinx



## 3 세션 :: SLAM, Navigation

SLAM: 지도 만들기까지만
Navigation: 지도를 이용해서 로봇이 이동하는 부분
	실내지도는 없음. 공간을 지도로 제공- 앞으로는 실내위치 추적이 되야하기 떄문.

1. SLAM
	(4가지 중요 키워드)
	1) 위치
		-실내위치 -landmark, Indoor GPS, WIFI SLAM(성능떨어짐), Beacon(a라는 방에있다 정도)
		-추측항법 (Dead Reckaning)
			runge-kutta 방법 이용.
	2) 센싱
		비전센서, Depth camera, 거리센서(레이져 스캐너, LRF)
	3) 지도
	4) 경로
		포텐션 장, 파티클 필터

	Gmapping ; ros 에서 사용하는 방식?
		OpenSLAM.org 전세계 모든 open SLAM 정보 다있음. 매우 좋은 사이트
		예제: gmapping + kobuki
		master 실행 명령어 : roscore
	OGM (2차원 점유 격자 지도)
	- 위치추정
		칼만 필터 - 예측하는것 
			예측-보정 반복하는 재귀 필터 , 베이시안확률 이용.
		파티클 필터 - 샘플링(try$error) 기반, 확률
			초기화->예측->보정->위치측정->재출
		추천 자료,서적 
			확률 로보틱스 - 세바스찬 교수 - 바이블임.
2. Navigation
	DWA (Dynamic Window Approach) local plan
	x y theta 가 하닌 속도 공간으로 바뀜.
	- 장애물과 부딛히지 않으면서 목적까지 최적의 속도로 이동할 수 있는 방법.


## 4 세션 :: 자작로봇 tamsarobot
LIVA 소형 x86 PC (SW)
Odomatry 방법 3가지
	euler Runge-kutta Exat
AMLL


## 5세션 :: Rocon Appable Robot (터틀봇 앱시스템 관련)
: 안드로이드나 윈도우의 앱 - 로봇의 앱 시스템 개념.
유진로봇이 ROS에 컨트리뷰션하고 있는 기능.
한로봇에 두가지 이상의 앱을 설치하여 실행 가능.

Rapp (Robot app)

talker / listener
ROS xomunitcation 방법 5가지
pub, sub, action..


## 6세션 :: Robot 암 모델링과 MoveIt 사용법
http://moveit.ros.org
로봇팔 제어 MoveIt을 사용하여 매우 편리하게 개발가능.

로봇팔 + 말단장치(end effector) 로 구성됨
unimate(1961) 세계 최초의 산업용 로봇 팔

로봇의 기초 동작.
Sensing -> Planning -> Action

- 기초 
 구성요소 : 기저, 링크, 관절, 말단장치
 작업공간과 관절공간으로 나뉨.
  작업공간: 말단장치의 위치와 자세(x y z roll pitch yaq)
  관절공간: 각 관절의 각도로 표현. 로봇팔은 관절값(Theta)만 매개변수임.

- 자유도 (DOF)
 어떤 물체를 표현할 수 있는 최소한의 변수(x y z roll pitch yaq)
 6자유도면 모든 동작 됨 
 	+1 자유도일수록 좀더 수월하게 동작됨. (인간의팔 7자유도)

- 순기구학, 역기구학
 기하학적 운동계획 (기구학)
 동역학적 효과 계산 (동역학)
 -> 을 이용하여 각 관절에 적당한 명령을 전달.

순기구학: 각 관절의 각도이용 -> 말단위치
역기구학: 말단 위치 -> 관절 각도 값 계산 //해를 구하기 매우 어렵다.
	-> 이 해를 MoveIt이 계산해줌. 
	
MoveIt 은 모션플래닝 패키지이다.
산업용에서도 엄청많이 쓰임.
	ROSi -> 산업용 로봇으로 사용하는 ROS

- MoveIt 사용법	
 moveIt에 넘겨줘야할 정보.
 	-링크정보
	-관절정보 
		-> 이 두가지를 URDF 포맷으로 기술해줌. (로봇 모델링에 많이사용)
		(SRDF, SDF도 있음)

		-> 이것을 SRDF로 변환하면 ROS에서 사용가능.

		-> MoveIt Setup Assistant 사용하면 엄청 편하게 바로 변환해줌.
