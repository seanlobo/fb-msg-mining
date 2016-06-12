$(function () {
    $.getJSON('https://www.highcharts.com/samples/data/jsonp.php?filename=usdeur.json&callback=?', function (data) {

        $('#graph').highcharts({
            chart: {
                zoomType: 'x'
            },
            title: {
                text: 'Message frequency'
            },
            subtitle: {
                text: 'The total number of messages sent each day over time'
                // 'Click and drag the plot area to zoom in'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'Number of messages'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                area: {
                    color: '#956bb2',
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1   
                        },
                        stops: [
                            [0, '#A368D7'], // Highcharts.getOptions().colors[0],
                            [1, '#E4DCEB'] // Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 2
                        }
                    },
                    threshold: null
                }
            },

            series: [{
                type: 'area',
                name: 'Messages sent',
                data: data
            }]
        });
    });
});