
## 사전조사  

### 웹페이지에서 미세먼지 데이터 읽어오기


PM10
http://www.airkorea.or.kr/sidoCompare?itemCode=10007

PM2.5
http://www.airkorea.or.kr/sidoCompare?itemCode=10008

실제 시간별 지역별 데이터가 기록된 데이터는 여기인데
http://www.airkorea.or.kr/sido_compare_p01?itemCode=10008&ymd=2015-12-31%2012&areaCode=031
HTML 파일이 안열림




### SYNCHRONIZING APP UI 내용 참고 아래 두 소스코드 비교해 볼것.

- 1. 가이드 문서:
https://developer.getpebble.com/guides/pebble-apps/communications/appsync/

- 2. 날씨 얻는 예제 소스코드
https://github.com/pebble-examples/pebblekit-js-weather
my local path: "/Users/jihuun/project/devenv/pebble/examples/pebblekit-js-weather/*"


### API study

#### 1. AppSync
https://developer.getpebble.com/docs/c/Foundation/AppSync/#AppSyncTupleChangedCallback

아래 코드는 ~/project/devenv/pebble/examples/synchronizing_App_UI/src/main.c 파일을 참고한 것임.  

- app_sync_init 에서 callback 함수 등록.
이 콜백 함수가 실제 폰앱에서 변경시 호출되는 콜백 함수.

```c
	// Begin using AppSync
	app_sync_init(&s_sync, s_sync_buffer, sizeof(s_sync_buffer), initial_values,
			ARRAY_LENGTH(initial_values), sync_changed_handler, sync_error_handler, NULL);

```
> sync_changed_handler() 가 핸들러

```c
static void sync_changed_handler(const uint32_t key, const Tuple *new_tuple, const Tuple *old_tuple, void *context) {

	static char s_count_buffer[32];
	snprintf(s_count_buffer, sizeof(s_count_buffer), "Count: %d",
		(int)new_tuple->value->int32);
	text_layer_set_text(s_output_layer, s_count_buffer);
}
```
> Tuple 구조체 포인터로 (new_tuple) 어떤 값이 넘어오는 듯. 
값이 어떻게 넘어오는지는 더 확인 필요. 
> text_layer_set_text() API 함수는 init()에서 초기화한 *s_output_layer (TextLayer 구조체) 
에 text값을 업데이트 하는 함수. 위코드에서는 s_count_buffer 값을 출력시킴.  

- TextLayer 초기화 부분

```c
	// Create output TextLayer
	s_output_layer = text_layer_create(GRect(0, 0, window_bounds.size.w, window_bounds.size.h));
	text_layer_set_text_alignment(s_output_layer, GTextAlignmentCenter);
	text_layer_set_text(s_output_layer, "Waiting...");
	layer_add_child(window_layer, text_layer_get_layer(s_output_layer));
```
> init() 에서 바로 사용해도 되고  .load 콜백(main_window_load()) 에서 등록해도됨. 
둘 간의 차이는 무엇일까? 전자는 부팅시 등록? 후자는 앱실행시 등록?
> 마지막에는 window_layer의 child node?로 등록? 왜하는지는 더 공부필요.  


- 보통 AppSync를 등록할떄 아래 3가지를 하는듯.  

```c
	// 1. Setup AppSync
	app_message_open(app_message_inbox_size_maximum(), app_message_outbox_size_maximum());

	// 2. Setup initial values
	Tuplet initial_values[] = {
		TupletInteger(KEY_COUNT, 0),
	};

	// 3. Begin using AppSync
	app_sync_init(&s_sync, s_sync_buffer, sizeof(s_sync_buffer), initial_values,
	... );
```


### 2. Tuple , Tuplet?
### 3. Dictionary

