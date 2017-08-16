mapboxgl.accessToken = 'pk.eyJ1IjoidGF0aWFuYWl2YW5uaWtvdmEiLCJhIjoiY2o0bzA3azRnMWd0ZTJ3cGcxdHd2NnUzYSJ9.2ps-jd_6FNsnteFLjqsvog';
var map = new mapboxgl.Map({
  container: 'map',
  center: [37.619733, 55.755401],
  style: 'mapbox://styles/tatianaivannikova/cj5iarso84xtd2rphgy85fypw',
  zoom: 10
});

var prevView = { center: [37.619733, 55.755401], zoom: 10 },
    sensorPanelIsOpen = false,
    demoIsStarted = false,
    interval,
    pointer,
    current = 0,
    speed = 100,
    x,
    y,
    trackData = [],
    margin = {top: 10, right: 10, bottom: 10, left: 20},
    params = ['vehicles', 'people', 'music', 'railway'],
    paramLines = [],
    paramLabels = [],
    audio = document.getElementById("audioTrack"),
    parseTime = d3.timeParse("%H-%m-%S");;

        //linking divs

params.map(p => {
  paramLines[p] = d3.select("#"+p+"Line").append("svg").attr("width", 200).attr("height", 4)
    .append("rect").attr("x",0).attr("y",0).attr("width", 200).attr("height", 4).style("fill","red");
    paramLabels[p] = d3.select("#"+p);
});


var soundtrack = d3.select("#soundtrack"),
    btnDemoStart = d3.select("#btnDemoStart").style("display", "block"),
    btnDemoPause = d3.select("#btnDemoPause").style("display", "none"),
    trackSvg = d3.select("#graphArea").append("svg"),
    graphArea = d3.select("#graphArea"),
    closeBtn = d3.select("#closeBtn");

var sensorData = { "type": "FeatureCollection", "features":
[{ "type": "Feature", "properties": { "level": 76 },
"geometry": { "type": "Point", "coordinates": [37.531477823243925, 55.80127466175835] }}]};


setTimeout(function() {
    document.getElementById("description").style.left = "-100%";
}, 2500);

var description=document.getElementById('description');

function toggleDescription(show) {
  if(show) { description.style.left="0"; }
  else { description.style.left="-100%"; }
}

function hide(obj) {
    var el = document.getElementById(obj);
        el.style.display = 'none';
}

function show(obj) {
   var s=document.getElementById(obj);
   s.style.display = 'block';
}

function openTab(evt,tabName) {
      var i, tabcontent, tablinks;
      tabcontent = document.getElementsByClassName("tabcontent");
      for (i = 0; i < tabcontent.length; i++) {
          tabcontent[i].style.display = "none";
      }
      tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
  }
  // Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();

map.on('load', function () {

    map.addSource('sensor', { type: 'geojson', data: sensorData });

    map.addLayer({
        "id": "sensor-bg",
        "type": "circle",
        "source": "sensor",
        "paint": {
            "circle-color": "#fff",
            "circle-radius": {
              "property": "level",
              "type": "exponential",
              "stops": [[35,16], [100,50]]
            },
            "circle-opacity": 0.3
        }
    });
    map.addLayer({
        "id": "sensor",
        "type": "circle",
        "source": "sensor",
        "paint": {
            "circle-color": "#fff",
            "circle-radius": 8
        }
    });

    map.addLayer({
        "id": "sensor-text",
        "type": "symbol",
        "source": "sensor",
        "paint": {
            "text-color": "#fff"
        },
        "layout": {
          "text-field": "{level} dB",
          "text-offset": [0,-1.6],
          "text-size": 16
        }
    });

    var canvas = map.getCanvasContainer();

    map.on("mousemove", "sensor-bg", function(e) {
    map.setPaintProperty("sensor-bg", "circle-opacity", 0.6);
    canvas.style.cursor = 'pointer';
    });

    map.on("mouseleave", "sensor-bg", function() {
    map.setPaintProperty("sensor-bg", "circle-opacity", 0.3);
    // Set a cursor indicator
    canvas.style.cursor = '';
    });

    map.on('click', function (e) {
      var bbox = [[e.point.x - 32, e.point.y - 32], [e.point.x + 32, e.point.y + 32]];
      var features = map.queryRenderedFeatures(bbox, { layers: ['sensor-bg'] });
      if(!features.length) {
        if(sensorPanelIsOpen) {
          toggleSensorPanel();
          if(demoIsStarted) { toggleDemoMode(); }
          map.flyTo(prevView);
         }
      } else {
        if(!sensorPanelIsOpen) {
          prevView = { center: map.getCenter(), zoom: map.getZoom() };
          toggleSensorPanel();
          map.flyTo({center: features[0].geometry.coordinates, zoom: 13});
         }
      }
    });

});

//var DragPanHandler = new DragPanHandler(map);

function toggleSensorPanel() {
  console.log('sensor panel');
  if(!sensorPanelIsOpen) {
    map.dragPan.disable();
    map.scrollZoom.disable();
    soundtrack.style("display", "block");
    sensorPanelIsOpen = true;
  } else {
    map.dragPan.enable();
    map.scrollZoom.enable();
    soundtrack.style("display", "none");
    sensorPanelIsOpen = false;
  }
}

d3.json("./data/sensor-simulation.json", function(error, json) {
  if (error) throw error;
  json.map((d) => { d['date'] = new Date(d.dt); return d; });

  //receive json data to gloval variable
  trackData = json;
  drawGraph(trackData);

});


toggleDemoMode = () => {
  if(!demoIsStarted) {
    interval = setInterval(moveNext, speed);
    demoIsStarted = true;
    btnDemoStart.style("display", "none");
    btnDemoPause.style("display", "block");
    audio.play();
  } else {
    clearInterval(interval);
    demoIsStarted = false;
    btnDemoStart.style("display", "block");
    btnDemoPause.style("display", "none");
    audio.pause();
  }

}


moveNext = () => {
  if(current>=trackData.length) {
    current = 0;
    audio.currentTime = 0;
  }
  updateParams(trackData[current]);
  current++;
}


updateParams = (d) => {
  params.map(p => {
    paramLabels[p].text(formatValue(d[p]) + '%');
    paramLines[p].attr("width", formatValue(d[p])*2)
  });

  //map radius
  sensorData.features[0].properties.level = d.level;
  map.getSource("sensor").setData(sensorData);


  pointer
    .transition()
    .duration(speed)
    .attr("x", x(d.date));
}

formatValue = (v) => {
  return Math.round(v*100);
}




function drawGraph(data) {
  width = innerWidth - margin.left - margin.right - 400;
  height = 100 - margin.top - margin.bottom;
  x = d3.scaleTime().range([0, width]);
  y = d3.scaleLinear().range([height, 0]);

  var valueline = d3.line()
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d.level); })

  trackSvg.attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Scale the range of the data
  x.domain(d3.extent(data, function(d) { return d.date; }));
  y.domain([30, d3.max(data, function(d) { return d.level; })]);

  trackSvg.append("path")
      .data([data])
      .attr("class", "line")
      .attr("d", valueline);

  pointer = trackSvg.append("rect")
      .attr("x", 10)
      .attr("y", 0)
      .attr("height", y(30))
      .attr("width", 1.5)
      .style("fill", "red");

      // Add the X Axis
  trackSvg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(x)
                  .tickFormat(d3.timeFormat("%H:%M:%S")))
          .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em");

    // Add the Y Axis
    trackSvg.append("g")
          .attr("class", "axis")
          .call(d3.axisLeft(y));

}

closeBtn.on('click', toggleSensorPanel);
btnDemoStart.on('click', toggleDemoMode);
btnDemoPause.on('click', toggleDemoMode);
