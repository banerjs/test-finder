var EventUtil = {
            
    addHandler: function(element, type, handler){
        if (element.addEventListener){
            element.addEventListener(type, handler, false);
        } else if (element.attachEvent){
            element.attachEvent("on" + type, handler);
        } else {
            element["on" + type] = handler;
        }
    },
            
    removeHandler: function(element, type, handler){
        if (element.removeEventListener){
            element.removeEventListener(type, handler, false);
        } else if (element.detachEvent){
            element.detachEvent("on" + type, handler);
        } else {
            element["on" + type] = null;
        }
    }
            
};

// Add code here to generate the input name from multiple fields if no autocomplete
// is desired. Remember to Django-ize that code

function geocode_initialize() {
{% if autocomplete %}
	var input = document.getElementById('{{ field_id }}_{{ input_name }}');
	var autocomplete = new google.maps.places.Autocomplete(input);

	google.maps.event.addListener(autocomplete, 'place_changed', function() {
		var latElement = document.getElementById('{{ field_id }}_lat');
		var lngElement = document.getElementById('{{ field_id }}_lng');
		var typeElement = document.getElementById('{{ field_id }}_type');

		var place = autocomplete.getPlace();
		var lat = place.geometry.location.lat();
		var lng = place.geometry.location.lng();
		var type = place.types;

		latElement.value = lat;
		lngElement.value = lng;
		typeElement.value = type;
	});
{% else %}
	var input = document.getElementById('{{ field_id }}_{{ input_name }}');
{% endif %}

	EventUtil.addHandler(input, "keydown", function(event) {
		var geocoder = new google.maps.Geocoder();
		var place = input.value;
{% if disable_submit %}
		var button = new Array();
{% for button in submit_buttons %}
		button[{{ forloop.counter0 }}] = document.getElementById('{{ button }}');
		button[{{ forloop.counter0 }}].disabled = true;
{% endfor %}
{% endif %}
		geocoder.geocode( { 'address': place }, function(results, status) {
			var lat = 1000;
			var lng = 1000;
			var type = "None";

			if (status == google.maps.GeocoderStatus.OK) {
				lat = results[0].geometry.location.lat();
				lng = results[0].geometry.location.lng();
				type = results[0].types;
			}

			var latElement = document.getElementById('{{ field_id }}_lat');
			var lngElement = document.getElementById('{{ field_id }}_lng');
			var typeElement = document.getElementById('{{ field_id }}_type');

			latElement.value = lat;
			lngElement.value = lng;
			typeElement.value = type;

{% if disable_submit %}
{% for button in submit_buttons %}
			button[{{ forloop.counter0 }}].disabled = false;
{% endfor %}
{% endif %}
		});
	});

}

google.maps.event.addDomListener(window, 'load', geocode_initialize);
