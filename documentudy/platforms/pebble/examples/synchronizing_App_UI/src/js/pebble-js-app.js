/*
 * pebble-js-app.js
 * Runs a counter that increments a variable and sends the new value 
 * to Pebble for processing in sync_changed_handler().
 */

var count = 0;

var emit = function() {
	count += 1;

	var dict = {"KEY_COUNT": count};

	Pebble.sendAppMessage(dict);
};

Pebble.addEventListener('ready', function(e) {
	console.log('PebbleKit JS ready!');

	// Send periodic updates every 3 seconds
	setInterval(emit, 3000);
});

Pebble.addEventListener('appmessage', function(e) {
	console.log('AppMessage received!');
});
