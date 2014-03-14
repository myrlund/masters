// Place all the behaviors and hooks related to the matching controller here.
// All this logic will automatically be available in application.js.

function doSmallVisualization(element) {
  var data = $(element).data();

  var chartData = { labels: data.features, datasets: [{
    data: data.center,
    fillColor: "rgba(151,187,205,0.5)",
    strokeColor: "rgba(220,220,220,1)"// ,
//     pointColor: "rgba(220,220,220,1)",
//     pointStrokeColor: "#fff"
  }]};

  var ctx = element.querySelector('canvas').getContext('2d');
  var chart = new Chart(ctx).Bar(chartData);

  console.log(chart);
}

window.onload = function () {
  var smallVisualizations = document.querySelectorAll('.cluster.small-visualization');
  for (var i = 0; i < smallVisualizations.length; i++) {
    doSmallVisualization(smallVisualizations[i]);
  }
};
