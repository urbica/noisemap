mapboxgl.accessToken = 'pk.eyJ1IjoidGF0aWFuYWl2YW5uaWtvdmEiLCJhIjoiY2o0bzA3azRnMWd0ZTJ3cGcxdHd2NnUzYSJ9.2ps-jd_6FNsnteFLjqsvog';
var map = new mapboxgl.Map({
    container: 'map',
    center: [37.4301228, 55.75267775],
    style: 'mapbox://styles/tatianaivannikova/cj4o0a947bdzm2rpdqp17yhci',
    zoom: 12
});



var gps_url = 'data/gps.geojson'; // iot.urbica.co/get_gps
var noise_url = 'data/noise_points.geojson';

map.on('load', function () {

  fetch("http://iot.urbica.co/get_gps",
  {
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    },
    method: 'POST',
    body: JSON.stringify({t1:'2017-07-05 18:10', t2:'2017-07-05 19:10'})
  })
  .then(function(res) {
    return res.blob();
  })
  .then(function(res){ console.log(res) })


    window.setInterval(function() {
        map.getSource('gps_points').setData(gps_url);
    }, 5000);

    window.setInterval(function() {
        map.getSource('noise_points').setData(noise_url);
    }, 5000);


    map.addSource('gps_points', { type: 'geojson', data: gps_url });
    map.addSource('noise_points', { type: 'geojson', data: noise_url });

    map.addLayer({
        "id": "gps_points",
        "type": "circle",
        "source": "gps_points",
        "paint": {
          "circle-color": "#FF0000",
          "circle-radius": 2
        }
    });

    map.addLayer({
        "id": "noise_points",
        "type": "circle",
        "source": "noise_points",
        "paint": {
          "circle-color": "#DD55AA",
          "circle-radius": 10,
          "circle-opacity": 0.8
        }
    });

    map.addLayer({
        "id": "drone",
        "type": "symbol",
        "source": "noise_points",
        "layout": {
            "icon-image": {
               property: 'source',
               type: 'categorical',
               stops: [
                 [0,"circle-stroked-15"],
                 [1,"car-15"],
                 [2,"playground-15"],
                 [3,"dog-park-15"],
                 [4,"square-stroked-15"],
                 [5,"square-stroked-15"],
                 [6,"square-stroked-15"],
                 [7,"building-15"],
                 [8,"square-15"],
                 [9,"music-15"]
               ]
            }
        }
    });

});
