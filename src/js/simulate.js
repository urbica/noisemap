// mapboxgl.accessToken = 'pk.eyJ1IjoidGF0aWFuYWl2YW5uaWtvdmEiLCJhIjoiY2o0bzA3azRnMWd0ZTJ3cGcxdHd2NnUzYSJ9.2ps-jd_6FNsnteFLjqsvog';
// var map = new mapboxgl.Map({
//     container: 'map',
//     style: 'mapbox://styles/tatianaivannikova/cj5iarso84xtd2rphgy85fypw',
//     center: [37.517577, 55.804814],
//     zoom: 14,
//     interactive: false
// });


var dataLoaded = false,
    data = [],
    interval,
    pointer,
    current = 0,
    speed = 100,
    isDemo = false,
    params = ['vehicles', 'people', 'music', 'railway'],
    paramLines = [],
    paramLabels = [],
    btnDemo = d3.select("#btnDemo"),
    graphArea = d3.select("#graphArea"),
    timeLabel = d3.select('#timeLabel');


var audio = document.getElementById("audioTrack");

    //linking divs
    params.map(p => {
      paramLines[p] = d3.select("#"+p+"Line").append("svg").attr("width", 200).attr("height", 4)
        .append("rect").attr("x",0).attr("y",0).attr("width", 200).attr("height", 4).style("fill","red");
      paramLabels[p] = d3.select("#"+p);
    })

    var sensorValue = d3.select("#sensorValue");


    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 10, bottom: 60, left: 30},
        width = window.innerWidth - margin.left - margin.right,
        height = 200 - margin.top - margin.bottom;

    // parse the date / time
    var parseTime = d3.timeParse("%H-%m-%S");

    // set the ranges
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // define the line
    var valueline = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.level); });

    // moves the 'group' element to the top left margin
    var svg = d3.select("#graphArea").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");

    var sesorArea = d3.select("#sensorPoint").append("svg").attr("width",200).attr("height",200);
    var sensor = sesorArea.append('circle')
                  .attr("cx", 100)
                  .attr("cy", 100)
                  .attr("r", 0)
                  .attr("id", "sensor")
                  .attr("class", "sensor");

    var sensorCore = sesorArea.append('circle').attr("cx", 100).attr("cy", 100).attr("r", 8).attr("id", "sensorCore").attr("class", "sensorCore");


toggleMode = () => {
  if(!isDemo) {
    interval = setInterval(moveNext, speed);
    isDemo = true;
    btnDemo.text('Stop');
    btnDemo.attr('class', 'btnStarted');
    audio.play();
  } else {
    clearInterval(interval);
    isDemo = false;
    btnDemo.text('Start');
    btnDemo.attr('class', 'btn');
    audio.pause();
  }


}

moveNext = () => {
  console.log(data[current]);

  sensor
    .transition()
    .duration(speed-50)
    .attr("r", data[current].level);
  updateParams(data[current]);

  console.log(current);
  current = (current<data.length) ? (current+1) : 0;
}

updateParams = (d) => {
  params.map(p => {
    paramLabels[p].text(formatValue(d[p]) + '%');
    paramLines[p].attr("width", formatValue(d[p])*2)
    console.log(p);
  })
  sensorValue.text(d.level + ' dB');
  timeLabel.text(parseTime(d.date));

  pointer
    .transition()
    .duration(speed)
    .attr("x", x(d.date));
}

formatValue = (v) => {
  return Math.round(v*100);
}

    // Get the data
    d3.json("./data/sensor-simulation.json", function(error, json) {
      if (error) throw error;

      json.map((d) => { d['date'] = new Date(d.dt); return d; });

      //receive json data to gloval variable
      data = json;

      // Scale the range of the data
      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain([30, d3.max(data, function(d) { return d.level; })]);

      // Add the valueline path.
      svg.append("path")
          .data([data])
          .attr("class", "line")
          .attr("d", valueline);

      pointer = svg.append("rect")
          .attr("x", 10)
          .attr("y", 0)
          .attr("height", y(30))
          .attr("width", 1.5)
          .style("fill", "red");

      // Add the X Axis
      svg.append("g")
          .attr("class", "axis")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(x)
                  .tickFormat(d3.timeFormat("%H:%M:%S")))
          .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)");

      // Add the Y Axis
      svg.append("g")
          .attr("class", "axis")
          .call(d3.axisLeft(y));

      btnDemo.on("click", toggleMode)

});
