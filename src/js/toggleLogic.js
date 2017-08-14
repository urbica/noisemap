mapboxgl.accessToken = 'pk.eyJ1IjoidGF0aWFuYWl2YW5uaWtvdmEiLCJhIjoiY2o0bzA3azRnMWd0ZTJ3cGcxdHd2NnUzYSJ9.2ps-jd_6FNsnteFLjqsvog';
var map = new mapboxgl.Map({
  container: 'map',
  center: [37.619733, 55.755401],
  style: 'mapbox://styles/tatianaivannikova/cj5iarso84xtd2rphgy85fypw',
  zoom: 10
});




setTimeout(function() {
    document.getElementById("description").style.left = "-100%";
}, 2500);



var description=document.getElementById('description');

function toggleDescription(show) {
  if(show) {
    description.style.left="0";
  }
  else {
    description.style.left="-100%";
  }
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




// function openDscr(evt, tabName) {
//
//       var i, tabcontent, tablinks;
//
//       tabcontent = document.getElementsByClassName("tabcontent");
//       for (i = 0; i < tabcontent.length; i++) {
//           tabcontent[i].style.display = "project";
//       }
//
//       tablinks = document.getElementsByClassName("tablinks");
//       for (i = 0; i < tablinks.length; i++) {
//           tablinks[i].className = tablinks[i].className.replace("active", "");
//       }
//
//       document.getElementById(tabName).style.display = "block";
//       evt.currentTarget.className += " active";
//   }



// }
