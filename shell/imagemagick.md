
이미지에 텍스트 삽입하기
http://blog.naver.com/skeehun/150005118551


### 이미지 사이즈 변경하기

convert samsi.png -resize 50%x50% -quality 100 samsi_50.png


### 이미지 합성하기


- 단순 합성

convert 배경 삽입 -conposite 결과
convert bg.jpg insert.png -composite out.jpg

- 우측 아래에 10pixel 띄우고 이미지 삽입하기
convert bg.jpg insert.png -gravity southeast -geometry +10+10 -composite out.jpg

참고 : 이미지 위치를 상대적으로 지정하기.
http://stackoverflow.com/questions/12273479/combining-multiple-images-in-imagemagick-with-relative-not-absolute-offsets

참고 : 이미지에 워터마크 박기
http://www.xoogu.com/2013/how-to-automatically-watermark-or-batch-watermark-photos-using-imagemagick/

참고 : 기초 기능
http://openwiki.kr/tech/imagemagick
