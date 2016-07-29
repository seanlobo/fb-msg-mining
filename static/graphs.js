$(function () {
    // graph variables
    var names = eval($("#name").text());
    var convo_num = eval($("#convo_num").text());
    var height = $("#graph_over_time").height();
    var width = $("#graph_over_time").width();
    var totalMessagesURL = function (person, cumulative, forwardShift, negative) {
        return window.location.href + "total_messages/" + 
                person + "/" + cumulative + "/" + forwardShift + "/" + negative + "/";
    };
    var messageByDayURL = function (contact) {
        return window.location.href + "messages_by_day/" + contact + "/";
    }
    var messageByTimeURL = function (contact, windowSize) {
        return window.location.href + "messages_by_time/" + contact + "/" + windowSize;
    }


    // message frequency
    $.getJSON(totalMessagesURL('none', 0, 0, 0)).success(function (data) {
        evaluatedData = data['data'].map(eval);

        $('#graph_over_time').highcharts({
            chart: {
                zoomType: 'x',
                height: height,
                width: width
            },
            title: {
                text: 'Message frequency',
                style: {
                    fontWeight: 'bold'
                }
            },
            subtitle: {
                text: document.ontouchstart === undefined ? 
                'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'Number of messages'
                },
                min: 0
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                area: {
                    color: '#f2a85e',
                    cursor: 'pointer',
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            [0, '#f19f4d'],
                            [1, '#fcf0e4']
                        ]
                    },
                    marker: {
                        radius: 3
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 2
                        }
                    }
                }
            },
            series: [{
                type: 'area',
                name: 'Messages sent',
                data: evaluatedData
           }]
        });   
    });


    // cumulative message frequency
    $.getJSON(totalMessagesURL('none', 1, 0, 0)).success(function (data) {
        evaluatedData = data['data'].map(eval);

        $('#cumulative_over_time').highcharts({
            chart: {
                zoomType: 'x',
                height: height,
                width: width
            },
            title: {
                text: 'Cumulative message frequency',
                style: {
                    fontWeight: 'bold'
                }
            },
            subtitle: {
                text: document.ontouchstart === undefined ? 
                'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'Number of messages'
                },
                min: 0
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                line: {
                    color: '#f9cf00',
                    cursor: 'pointer',
                    marker: {
                        radius: 3
                    },
                    lineWidth: 3,
                    states: {
                        hover: {
                            lineWidth: 5
                        }
                    }
                }
            },
            series: [{
                type: 'line',
                name: 'Total messages sent',
                data: evaluatedData
           }]
        });
    });


    // messages by day of week
    $.getJSON(messageByDayURL('none')).success(function (data) {
        evaluatedData = data['data'];
        
        $('#days_of_week').highcharts({
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie',
                height: height,
                width: width
            },
            
            title: {
                text: 'Messages by day of week',
                style: {
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                        style: {
                            color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                        }
                    }
                }
            },
            series: [{
                type: 'line',
                name: 'Total messages sent',
                data: evaluatedData
           }]
        });
    });


    // messages by day of week
    $.getJSON(messageByDayURL('none')).success(function (data) {
        evaluatedData = data['data'];
        
        $('#days_of_week').highcharts({
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                type: 'pie',
                height: height,
                width: width,
            },
            colors: ['#5690d2', '#fceea5', '#f2a85e', '#3669a4', '#ff8845', '#f3cb07', '#9fbceb'],
            title: {
                text: 'Messages by day of week',
                style: {
                    fontWeight: 'bold'
                }
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                    }
                }
            },
            series: [{
                name: 'Percent messages sent',
                data: evaluatedData
            }]
        });
    });

    
    // messages by time of day
    $.getJSON(messageByTimeURL('none', 60)).success(function (data) {
        categories = data['categories'];
        evaluatedData = data['data'];

        $('#time_of_day').highcharts({
            chart: {
                type: 'column',
                height: height,
                width: width
            },
            title: {
                text: 'Messages by time of day',
                style: {
                    fontWeight: 'bold'
                }
            },
            xAxis: {
                categories: categories
            },
            yAxis: {
                min: 0,
                title: {
                    text: 'Percent messages sent'
                },
                stackLabels: {
                    enabled: false,
                    style: {
                        fontWeight: 'bold',
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            },
            legend: {
                align: 'right',
                x: -30,
                verticalAlign: 'top',
                y: 25,
                floating: true,
                backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
                borderColor: '#CCC',
                borderWidth: 1,
                shadow: false
            },
            tooltip: {
                headerFormat: '<b>{point.x}</b><br/>',
                pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
            },
            plotOptions: {
                column: {
                    cursor: 'pointer',
                    stacking: 'normal',
                    dataLabels: {
                        enabled: false,
                        color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',
                        style: {
                            textShadow: '0 0 3px black'
                        }
                    }
                }
            },
            series: evaluatedData
        });
    });

    $(".header-btn.prev").click(function() {
        window.location = window.location.href + 'prev/';
    });

    $(".header-btn.next").click(function() {
        window.location = window.location.href + 'next/';
    });

    var clearGraphsAndSettings = function() {
        $(".graph").addClass("hide");
        $(".settings-body").addClass("hide");
    };

    // Click functions for graph buttons, hides all graphs+settings and shows only appropriate one
    $(".graph_type_button").click(function() {
        clearGraphsAndSettings();
        var button_number = $(this).data("graph-type");
        var settings = $("div").find("[data-settings-num='" + button_number + "']");
        var chart = $("div").find("[data-graph='" + button_number + "']");

        chart.removeClass("hide");
        settings.removeClass("hide");
        
        chartID = chart[0].id;
        var actualChart = $('#' + chartID).highcharts();
    });

    var button = $("div").find("[data-graph-type='" + 0 + "']");
    button.click();
    // button.focus();  didn't work D:

    // Some inspiration http://stackoverflow.com/questions/6112660/how-to-automatically-change-the-text-size-inside-a-div
    var header = $(".header");
    var h1 = $(".header h1");
    while (h1.height() > header.height()) {
        h1.css("font-size", parseInt(h1.css("font-size")) - 1 + "px");
    }
    header.removeClass("hide");

});
