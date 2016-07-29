// MORE GRAPHS TO ADD
// messages frequency - stacked area, percentage area
// cumulative - stacked area
// by day - donut chart OR pie with drilldown
// by time - stacked column (might not need to change anything)

$(function () {
    // -------------------------------------------------  GRAPH VARIABLES AND FUNCTIONS ------------------------------------------------- \\

    var names = eval($("#name").text());
    var convo_num = eval($("#convo_num").text());
    var height = $("#graph_over_time").height();
    var width = $("#graph_over_time").width();
    var graphData = { };
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
    var nameToUnderscores = function (name) {
        return name.toLowerCase().split().join("_");
    }
    var toTitleCase = function(str) {
        // http://stackoverflow.com/questions/196972/convert-string-to-title-case-with-javascript
        return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    }
 
    var setDataForGraph4 = function(peopleList, forwardShift) {
        // Get a list of urls that aren't in graphData
        var negative;
        if (forwardShift < 0) {
            negative = 1;
        } else {
            negative = 0;
        }
        forwardShift = Math.abs(forwardShift);
        var urlGetter = function(person) {
            return totalMessagesURL(person, 0, forwardShift, negative);
        }
        var tmpUrls = peopleList.map(urlGetter);
        var URLsToNames = { };
        for (i = 0; i < tmpUrls.length; i++) {
            URLsToNames[tmpUrls[i]] = peopleList[i];
        }
        var urls = [];
        for (val in tmpUrls) {
            if (!(tmpUrls[val] in graphData)) {
                urls.push(tmpUrls[val]);
            }
        }

        var loadData = function () {
            var chart = $('#graph_over_time2').highcharts();
            // remove previous series
            // http://stackoverflow.com/questions/6604291/proper-way-to-remove-all-series-data-from-a-highcharts-chart
            while (chart.series.length > 0) {
                chart.series[0].remove(true);
            }

            chart.xAxis[0].setCategories(graphData[tmpUrls[0]].categories);
            // Load graphData into highcharts
            $.each(tmpUrls, function (i, url) {
                chart.addSeries(graphData[url].data);
            });

            $('#graph_over_time').addClass('hide');
            $('#graph_over_time2').removeClass('hide');
        }
        
        if (urls.length == 0) {
            // we already have all the data for urls
            loadData();
        } else {
            // get a list of data values from urls above and add to graphData
            // http://stackoverflow.com/questions/38582200/javascript-load-arbitrary-number-of-urls-with-getjson
            var promises = urls.map(url => $.getJSON(url));

            Promise.all(promises).then(function (data) {
                for (val in data) {
                    graphData[urls[val]] = {
                        categories: data[val]['categories'],
                        data: data[val]['data']
                    };
                }

                loadData();
            });
        }
    };
    $("#test").click(function () {
        if ($('#graph_over_time2').hasClass("hide")) {
            setDataForGraph4(names.map(nameToUnderscores), '0');
        } else {
            $("div").find("[data-graph-type='" + 0 + "']").click();
        }
    });



    // -------------------------------------------------  MESSAGE FREQUENCY GRAPHS ------------------------------------------------- \\

    $.getJSON(totalMessagesURL('none', 0, 0, 0)).success(function (data) {
        evaluatedData = data['data'].map(eval);
        graphData[totalMessagesURL('none', 0, 0, 0)] = evaluatedData;
        

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


    $('#graph_over_time2').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x',
            height: height,
            width: width
        },
        title: {
            text: 'Message Frequency by Person'
        },
        subtitle: {
            text: ''
        },
        xAxis: {
            categories: [],
            tickmarkPlacement: 'on',
            title: {
                enabled: false
            }
        },
        yAxis: {
            title: {
                text: ''
            }
        },
        tooltip: {
            shared: true,
            // valueSuffix: ' millions'
        },
        plotOptions: {
            area: {
                // stacking: 'percent',
                stacking: 'normal', 
                lineColor: '#666666',
                lineWidth: 1,
                marker: {
                    lineWidth: 1,
                    lineColor: '#666666'
                }
            }
        },
        series: [{}]
        // series: [{
        //     name: 'Asia',
        //     data: [502, 635, 809, 947, 1402, 3634, 5268]
        // }, {
        //     name: 'Africa',
        //     data: [106, 107, 111, 133, 221, 767, 1766]
        // }, {
        //     name: 'Europe',
        //     data: [163, 203, 276, 408, 547, 729, 628]
        // }, {
        //     name: 'America',
        //     data: [18, 31, 54, 156, 339, 818, 1201]
        // }, {
        //     name: 'Oceania',
        //     data: [2, 2, 2, 6, 13, 30, 46]
        // }]
    });


    // ---------------------------------------- CUMULATIVE MESSAGE FREQUENCY GRAPHS ---------------------------------------- \\

    $.getJSON(totalMessagesURL('none', 1, 0, 0)).success(function (data) {
        evaluatedData = data['data'].map(eval);
        graphData[totalMessagesURL('none', 1, 0, 0)] = evaluatedData;

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


    // ---------------------------------------- MESSAGES BY DAY OF WEEK ---------------------------------------- \\

    $.getJSON(messageByDayURL('none')).success(function (data) {
        evaluatedData = data['data'];
        graphData[messageByDayURL('none')] = evaluatedData;
        
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

    
    // ------------------------------------------------ MESSAGES BY TIME OF DAY ------------------------------------------------ \\
    $.getJSON(messageByTimeURL('none', 60)).success(function (data) {
        categories = data['categories'];
        evaluatedData = data['data'];
        graphData[messageByTimeURL('none', 60)] = {
            categories: categories,
            data: evaluatedData
        };


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

    $(".select-conversation").click(function () {
        window.location = window.location.href.substring(0, window.location.href.indexOf('conversation') + 12);
    });

    var button = $("div").find("[data-graph-type='" + 0 + "']");
    button.click();
    // button.focus();  didn't work D:

    // Some inspiration http://stackoverflow.com/questions/6112660/how-to-automatically-change-the-text-size-inside-a-div
    var header = $(".header");
    var header_div = $(".header .title");
    while (header_div.outerHeight() > header.height()) {
        console.log(header.height(), header_div.outerHeight());
        header_div.css("font-size", parseInt(header_div.css("font-size")) - 1 + "px");
    }
    header_div.css("visibility", "visible");

});
