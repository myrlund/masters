// Place all the behaviors and hooks related to the matching controller here.
// All this logic will automatically be available in application.js.

function doSmallVisualization(element) {
    var data = $(element).data();
    var container = element.getElementsByTagName('canvas')[0];
    var ctx = container.getContext('2d');

    var s1 = {
        label: 'Average',
        fillColor: 'rgba(220,220,220,0.5)',
        strokeColor: 'rgba(220,220,220,1)',
        data: data.avgCenter
    }

    var s2 = {
        label: 'Cluster center',
        fillColor: 'rgba(151,187,205,0.5)',
        strokeColor: 'rgba(151,187,205,1)',
        data: data.center
    };

    var data = {
        labels: data.features,
        datasets: [ s1, s2 ]
    }

    var chart = new Chart(ctx).Bar(data, {});

    console.log(chart);
}

function comparativeVisualization(element) {
    var clusterSorter = function (a, b) {
        return -(a.size - b.size);
    };

    var container = element.getElementsByTagName('div')[0],
        data = $(element).data(),
        features = data.features,
        clusters = data.clusters; //.sort(clusterSorter);

    var featureScaling = [];
    for (var i = 0; i < features.length; i++) {
        var vals = [];
        for (var j = 0; j < clusters.length; j++) {
            vals.push(clusters[j].center[i]);
        }
        var max = Math.max.apply(null, vals);
        var scale = max > 0 ? (1 / max) * 10 : 1;
        featureScaling.push(scale);
    }

    var series = [];
    for (var i = 0; i < clusters.length; i++) {
        var label = clusters[i].label || 'Cluster ' + (i + 1);
        series.push({ label: label + ' (' + clusters[i].size + ')', data: [] });

        for (var j = 0; j < clusters[i].center.length; j++) {
            series[i].data.push([j, clusters[i].center[j] * featureScaling[j]]);
        }
        console.log(label);
        console.log(series[i].data);

    }

    var ticks = [];
    for (var i = 0; i < features.length; i++) {
        ticks.push([i, features[i]]);
    }

    var chart = Flotr.draw(container, series, {
        xaxis: {
            ticks: ticks
        },
        yaxis: {
            min: 0,
            max: 10
        },
        grid: {
            circular: true
        },
        radar: {
            show : true
        },
        legend: {
            position: 'se'
        }
    })
}

$(function () {
    comparativeVisualization(document.querySelector('#comparison'));

    var smallVisualizations = document.querySelectorAll('.cluster.small-visualization');
    for (var i = 0; i < smallVisualizations.length; i++) {
        doSmallVisualization(smallVisualizations[i]);
    }
});
