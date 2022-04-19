/*global google */
/*eslint no-global-assign: "error"*/


function initMap() {
    const field_address = document.getElementById('field_address').name;
    const center = document.getElementById('field_address').value;
    const input = document.getElementById('id_contacto_form-'.concat(field_address));
    const map = new google.maps.Map(document.getElementById('map'), {
        center: JSON.parse(center),
        zoom: 13,
        mapTypeControl: false,
    });
    if (input.value) {
        const geocoder = new google.maps.Geocoder();
        geocoder.geocode( { 'address' : input.value }, function( results, status ) {
            if( status == google.maps.GeocoderStatus.OK ) {
                //In this case it creates a marker, but you can get the lat and lng from the location.LatLng
                map.setCenter( results[0].geometry.location );
                var marker = new google.maps.Marker( {
                    map     : map,
                    position: results[0].geometry.location
                } );
            }
        } );
    }
    const options = {
        fields: ['formatted_address', 'geometry', 'name'],
        strictBounds: false,
    };

    const autocomplete = new google.maps.places.Autocomplete(input, options);
  
    autocomplete.bindTo('bounds', map);
  
    const infowindow = new google.maps.InfoWindow();
    const infowindowContent = document.getElementById('infowindow-content');
  
    infowindow.setContent(infowindowContent);
  
    const marker = new google.maps.Marker({
        map,
        anchorPoint: new google.maps.Point(0, -29),
    });
  
    autocomplete.addListener('place_changed', () => {
        infowindow.close();
        marker.setVisible(false);

        const place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
            window.alert('No details available for input: "' + place.name + '"');
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);
        }

        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
        infowindowContent.children['place-name'].textContent = place.name;
        infowindowContent.children['place-address'].textContent =
          place.formatted_address;
        infowindow.open(map, marker);
    });
}
