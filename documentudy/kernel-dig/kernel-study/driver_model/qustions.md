
## Device Tree  

- 어떤 dts 파일을 쓰는지?  
struct device_node *np = pdev->dev.of_node;  
ret = of_property_read_string(np, "marvell,phy-name", &dsi->name);  
> dev는 이미 이전에 초기화가 되었음 어디서?   
로 dts 파일에서 문자열을 찾아서 dsi->name값에 저장하는데  
어떤 dts 파일을 쓰는지 언제 어떻게 아나?  


## platform device driver  

- pdev->dev 의 dev 는 언제 초기화되었고 어떻게 쓰이는지?  
struct device 구조체 인스턴스임.  



## module_init() 으로 디바이스 드라이버를 등록했을때 모듈빌드를 안해도 호출이 되나?  
  
>  
moudle_init 매크로는 디바이스 드라이버를 모듈로 컴파일 하지 않으면  
device_initcall에 의해서  .initcall7.init 섹션에 등록되어 커널 초기화 과정에서  
등록하게 된다.  
  
>  
빌드인 하기위해서는 device_initcall() 매크로를 사용해도 된다.   
#define device_initcall(fn)             __define_initcall("6",fn,6)   
  
> 즉 device_initcall은 initcall 6번 module_init은 7번이므로 더 늦게 호출된다.  
  
  
참고 http://egloos.zum.com/flameco82/v/2778032  
