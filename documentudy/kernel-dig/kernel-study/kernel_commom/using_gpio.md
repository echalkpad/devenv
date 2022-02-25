shell 에서 gpio 컨트롤 하는 방법  
출처 : http://luketopia.net/2013/07/28/raspberry-pi-gpio-via-the-shell/  

```sh
echo 4 > /sys/class/gpio/expot
echo out > /sys/class/gpio/gpio4/direction
echo 0 > /sys/class/gpio/gpio4/value
echo 1 > /sys/class/gpio/gpio4/value
```

