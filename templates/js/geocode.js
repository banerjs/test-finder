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
	var input = document.getElementById('geocode_{{ input_name }}');

{% if autocomplete %}
	var autocomplete = new google.maps.places.Autocomplete(input);
	google.maps.event.addListener(autocomplete, 'place_changed', function() {
		var latElement = document.getElementById('geocode_lat');
		var lngElement = document.getElementById('geocode_lng');
		var typeElement = document.getElementById('geocode_type');

		var place = autocomplete.getPlace();
		var lat = place.geometry.location.lat();
		var lng = place.geometry.location.lng();
		var type = place.types;

		latElement.value = lat;
		lngElement.value = lng;
		typeElement.value = type;
	});
{% endif %}

	EventUtil.addHandler(input, "keydown", function(event) {
		var geocoder = new google.maps.Geocoder();
		var place = input.value;

		geocoder.geocode( { 'address': place }, function(results, status) {
			var lat = 1000;
			var lng = 1000;
			var type = "None";

			if (status == google.maps.GeocoderStatus.OK) {
				lat = results[0].geometry.location.lat();
				lng = results[0].geometry.location.lng();
				type = results[0].types;
			}

			var latElement = document.getElementById('geocode_lat');
			var lngElement = document.getElementById('geocode_lng');
			var typeElement = document.getElementById('geocode_type');

			latElement.value = lat;
			lngElement.value = lng;
			typeElement.value = type;
		});
	});

}

google.maps.event.addDomListener(window, 'load', geocode_initialize);
