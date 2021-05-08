function geoFindMe(e) {

    e.preventDefault();

    const mapCoordinates = document.querySelector('#id_location');

    function success(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        mapCoordinates.value = `${longitude},${latitude}`;
    }

    function error() {
        console.log('Unable to retrieve your location');
    }
    

    if (!navigator.geolocation) {
        console.log('Geolocation is not supported by your browser');
    } else {
        navigator.geolocation.getCurrentPosition(success, error);
    }

}

document.querySelector('#find-me').addEventListener('click', geoFindMe);