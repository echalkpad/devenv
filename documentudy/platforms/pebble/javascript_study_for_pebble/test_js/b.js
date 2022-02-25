
function fetchWeather() {
  var req = new XMLHttpRequest();
  req.open('GET', 'http://google.com', true);
  req.onload = function () {
    if (req.readyState === 4) {
        debug("pass 4");
      if (req.status === 200) {
        debug("pass 200");
//      console.log(req.responseText);
        debug(req.responseText);
/*
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
*/
      } else {
       // console.log('Error');
        debug('Error');
      }
    }
  };
  req.send(null);
}

fetchWeather();
