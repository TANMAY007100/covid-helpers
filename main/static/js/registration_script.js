function geoFindMe(e) {

    e.preventDefault();

    const mapCoordinates = document.querySelector('#id_location');

    function success(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        mapCoordinates.value = `${longitude},${latitude}`;
    }

    function error() {
        alert('Unable to retrieve your location. GPS Location is mandatory to register');
    }


    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser. GPS Location is mandatory to register');
    } else {
        navigator.geolocation.getCurrentPosition(success, error);
    }

}

document.querySelector('#find-me').addEventListener('click', geoFindMe);