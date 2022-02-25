/*
 * main.c
 * Creates a Window and output TextLayer, then opens AppSync to 
 * keep up-to-date with a counter running in pebble-js-app.js (see below).
 */

#include <pebble.h>

#define KEY_COUNT 5

static Window *s_main_window;;

static TextLayer *s_output_layer;
static AppSync s_sync;
static uint8_t s_sync_buffer[32];

static void sync_changed_handler(const uint32_t key, const Tuple *new_tuple, const Tuple *old_tuple, void *context) {
	// Update the TextLayer output
	static char s_count_buffer[32];
	snprintf(s_count_buffer, sizeof(s_count_buffer), "Count: %d", (int)new_tuple->value->int32);
	text_layer_set_text(s_output_layer, s_count_buffer);
}

static void sync_error_handler(DictionaryResult dict_error, AppMessageResult app_message_error, void *context) {
	// An error occured!
	APP_LOG(APP_LOG_LEVEL_ERROR, "sync error!");
}

static void main_window_load(Window *window) {
	Layer *window_layer = window_get_root_layer(window);
	GRect window_bounds = layer_get_bounds(window_layer);

	// Create output TextLayer
	s_output_layer = text_layer_create(GRect(0, 0, window_bounds.size.w, window_bounds.size.h));
	text_layer_set_text_alignment(s_output_layer, GTextAlignmentCenter);
	text_layer_set_text(s_output_layer, "Waiting...");
	layer_add_child(window_layer, text_layer_get_layer(s_output_layer));
}

static void main_window_unload(Window *window) {
	// Destroy output TextLayer
	text_layer_destroy(s_output_layer);
}

static void init(void) {
	// Create main Window
	s_main_window = window_create();
	window_set_window_handlers(s_main_window, (WindowHandlers) {
			.load = main_window_load,
			.unload = main_window_unload,
			});
	window_stack_push(s_main_window, true);

	// Setup AppSync
	app_message_open(app_message_inbox_size_maximum(), app_message_outbox_size_maximum());

	// Setup initial values
	Tuplet initial_values[] = {
		TupletInteger(KEY_COUNT, 0),
	};

	// Begin using AppSync
	app_sync_init(&s_sync, s_sync_buffer, sizeof(s_sync_buffer), initial_values,
			ARRAY_LENGTH(initial_values), sync_changed_handler, sync_error_handler, NULL);
}

static void deinit(void) {
	// Destroy main Window
	window_destroy(s_main_window);

	// Finish using AppSync
	app_sync_deinit(&s_sync);
}

int main(void) {
	init();
	app_event_loop();
	deinit();
}
