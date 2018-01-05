### 목적 : 아래 코드 이해하기!

```js

function fetchWeather(latitude, longitude) {
  var req = new XMLHttpRequest();
  req.open('GET', 'http://api.openweathermap.org/data/2.5/weather?' +
      'lat=' + latitude + '&lon=' + longitude + '&cnt=1&appid=' + myAPIKey, true);
  req.onload = function () {
    if (req.readyState === 4) {
      if (req.status === 200) {
        console.log(req.responseText);
        var response = JSON.parse(req.responseText);
        var temperature = Math.round(response.main.temp - 273.15);
        var icon = iconFromWeatherId(response.weather[0].id);
        var city = response.name;
        console.log(temperature);
        console.log(icon);
        console.log(city);
        Pebble.sendAppMessage({
            'WEATHER_ICON_KEY': icon,
            'WEATHER_TEMPERATURE_KEY': temperature + '\xB0C',
            'WEATHER_CITY_KEY': city
            }); 
      } else {
        console.log('Error');
      }   
    }   
  };  
  req.send(null);
}

```


### 기본 실행 방법
$ jsc
http://www.freshblurbs.com/blog/2011/09/25/command-line-javascript-cli-mac-os-x.html



### javascript 웹 크롤링 하기


- XMLHttpRequest() responseText 관련내용 튜토리얼 아래 참고
https://developer.mozilla.org/ko/docs/AJAX/Getting_Started
https://opentutorials.org/course/1375/6843

- XMLHttpRequest() API 참고 문서
https://developer.mozilla.org/ko/docs/XMLHttpRequest

- JSON.parse
https://opentutorials.org/course/1375/6844
https://msdn.microsoft.com/ko-kr/library/cc836466(v=vs.94).aspx




