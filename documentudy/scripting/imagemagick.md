
### 이미지에 텍스트 삽입하기
http://blog.naver.com/skeehun/150005118551


- 참고 
http://www.imagemagick.org/discourse-server/viewtopic.php?t=8380

```sh
convert -size 500x500 out.jpg -thumbnail 250x250 -gravity South -bordercolor black -border 1x1 -background Black -splice 0x25 -font KoPubDotumBold.ttf -fill white -draw 'text 0,0 "삽입 텍스트"' result.jpg
```

```sh
convert -size 500x500 out.jpg  -gravity South -bordercolor white -border 1x1 -background Navy -splice 0x25 -font KoPubDotumBold.ttf -fill white -draw 'text 0,0 "삽입 텍스트"' result.jpg
```

- "-splice" 옵션

```text
-splice geometry
Splice the current background color into the image.

This will add rows and columns of the current -background color into the given
image according to the given -gravity geometry setting. See Image Geometry for
complete details about the geometry argument. Essentially -splice will divide
the image into four quadrants, separating them by the inserted rows and
columns.

If a dimension of geometry is zero no rows or columns will be added for that
dimension. Similarly using a zero offset with the appropriate -gravity setting
will add rows and columns to the edges of the image, padding the image only
along that one edge. Edge padding is what -splice is most commonly used for.

If the exact same geometry and -gravity is later used with -chop the added
added all splices removed.  ```

- 다른 방법 
http://www.imagemagick.org/Usage/annotating/

```sh
convert dragon.gif   -background Khaki  label:'Faerie Dragon' \
          -gravity Center -append    anno_label.jpg
```
> annotate.c 관련 오류는 brew install ghostscript 로 해결했음.  


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
