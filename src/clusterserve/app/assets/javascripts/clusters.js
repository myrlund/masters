// Place all the behaviors and hooks related to the matching controller here.
// All this logic will automatically be available in application.js.

function doSmallVisualization(element) {
    var data = $(element).data();
    var container = element.getElementsByTagName('div')[0];

    var center = [];
    for (var i = 0; i < data.center.length; i++) {
        center.push([i, data.center[i]]);
    }

    var s1 = {
        label: element.title,
        data: center
    };

    console.log(data.features);

    var chart = Flotr.draw(container, [s1], {
        xaxis: {
            min: -0.5,
            max: 1.5,
            tickDecimals: 0,
            noTicks: data.features.length,
            tickFormatter: function (n) { console.log("EHHHHHY: " + n); return data.features[n]; }
        },
        yaxis: {
            min: 0,
            autoscale: true
        },
        bars: {
            show: true,
            horizontal: false,
            shadowSize: 0,
            barWidth: 0.5
        }
    });

    console.log(chart);
}

function comparativeVisualization(element) {
    var container = element.getElementsByTagName('div')[0],
        data = $(element).data(),
        features = data.features,
        clusters = data.clusters;

    var featureScaling = [];
    for (var i = 0; i < features.length; i++) {
        var vals = [];
        for (var j = 0; j < clusters.length; j++) {
            vals.push(clusters[j].center[i]);
        }
        var max = Math.max.apply(null, vals);
        featureScaling.push((1 / max) * 10);
    }

    var series = [];
    for (var i = 0; i < clusters.length; i++) {
        var label = clusters[i].label || 'Cluster ' + (i + 1);
        series.push({ label: label + ' (' + clusters[i].size + ')', data: [] });

        for (var j = 0; j < clusters[i].center.length; j++) {
            series[i].data.push([j, clusters[i].center[j] * featureScaling[j]]);
        }
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
