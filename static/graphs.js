// MORE GRAPHS TO ADD
// by day - donut chart OR pie with drilldown

$(function () {
    // -------------------------------------------------  GRAPH VARIABLES AND FUNCTIONS ------------------------------------------------- \\

    var names = eval($("#name").text());
    var convo_num = eval($("#convo_num").text());
    var height = $("#graph_over_time").height();
    var width = $("#graph_over_time").width();
    var graphData = { };
    var urlsToNames = { };
    function totalMessagesURL(person, cumulative, forwardShift, negative) {
        var url = window.location.href + "total_messages/" + 
                person.split(" ").join('_') + "/" + cumulative + "/" + forwardShift + "/" + negative + "/";
        urlsToNames[url] = person;
        return url;
    };
    function messageByDayURL(person) {
        var url = window.location.href + "messages_by_day/" + person.split(" ").join('_') + "/";
        urlsToNames[url] = person;
        return url;
    }
    function messageByTimeURL(person, windowSize) {
        var url = window.location.href + "messages_by_time/" + person.split(" ").join('_') + "/" + windowSize;
        urlsToNames[url] = person;
        return url;
    }
    function nameToUnderscores(name) {
        return name.toLowerCase().split().join("_");
    }
    function toTitleCase(str) {
        // http://stackoverflow.com/questions/196972/convert-string-to-title-case-with-javascript
        return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    }
    function numberWithCommas(x) {
        // http://stackoverflow.com/questions/2901102/how-to-print-a-number-with-commas-as-thousands-separators-in-javascript
       return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
    function urlToName(url) {
        return urlsToNames[url];
    }
    function getColors(index) {
        // Generate unique colors
        // http://stackoverflow.com/questions/470690/how-to-automatically-generate-n-distinct-colors
        
        // below colors are modified Bonynton optomized from: http://jsfiddle.net/k8NC2/1/
        var colorList = [
            "#0000FF", // Blue
            "#FF0000", // Red
            "#00FF00", // Green
            "#FFFF00", // Yellow
            "#FF00FF", // Magenta
            "#FF8080", // Pink
            "#800000", // Brown
            "#FF8000", // Orange

            "#000000", // Black
            "#4c4c4c", // dark grey
            "#e2e2e2", // very light grey/ white
        ];

        return colorList[index % colorList.length];
    }


    // -------------------------------------------------  MESSAGE FREQUENCY GRAPHS ------------------------------------------------- \\
    var forwardShift = 0;
    var graphStack = 'normal';
    var graphType = 'area'

    $.getJSON(totalMessagesURL('none', 0, 0, 0)).success(function (data) {
        evaluatedData = data['data'].map(eval);
        graphData[totalMessagesURL('none', 0, 0, 0)] = evaluatedData;
        

        $('#graph_over_time').highcharts({
            chart: {
                zoomType: 'x',
                panning: true,
                panKey: 'shift',
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
                text: 'Click and drag to zoom in, <b>Shift click</b> and drag to pan'
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
            zoomType: 'x',
            panning: true,
            panKey: 'shift',
            height: height,
            width: width
        },
        title: {
            text: 'Message Frequency by Person'
        },
        subtitle: {
            text: 'Click and drag to zoom in, <b>Shift click</b> and drag to pan'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Number of messages'
            }
        },
        tooltip: {
            shared: true,
            valueSuffix: ' messages'
        },
        plotOptions: {
            area: {
                stacking: graphStack, 
                lineColor: '#666666',
                lineWidth: 1,
                marker: {
                    lineWidth: 1,
                    lineColor: '#666666'
                }
            }
        },
        series: [{}]
    });

    var getURLData = function (peopleList, forwardShift, cumulative) {
        // Get a list of urls that aren't in graphData
        var negative;
        if (forwardShift < 0) {
            negative = 1;
        } else {
            negative = 0;
        }
        forwardShift = Math.abs(forwardShift);
        var urlGetter = function(person) {
            return totalMessagesURL(person, cumulative, forwardShift, negative);
        }
        var tmpUrls = peopleList.map(urlGetter);

        var urls = [];
        for (val in tmpUrls) {
            if (!(tmpUrls[val] in graphData)) {
                urls.push(tmpUrls[val]);
            }
        }

        return {
            tmpUrls: tmpUrls,
            urls: urls
        };
    };

    var setDataForGraph4 = function(peopleList, forwardShift) {
        var data = getURLData(peopleList, forwardShift, 0);

        var tmpUrls =  data.tmpUrls;
        var urls =  data.urls;

        var loadData = function () {
            var chart = $('#graph_over_time2').highcharts();
            // http://stackoverflow.com/questions/6604291/proper-way-to-remove-all-series-data-from-a-highcharts-chart
            while (chart.series.length > 0) {
                chart.series[0].remove(true);
            }

            // chart.xAxis[0].setCategories(graphData[tmpUrls[0]].categories);
            // Load graphData into highcharts
            $.each(tmpUrls, function (i, url) {
                var seriesData = {
                    data: graphData[url],
                    type: graphType,
                    stacking: graphStack,
                    name: toTitleCase(urlsToNames[url])
                };
                addColorToSeries(seriesData, $('input[data-color-person="' + urlsToNames[url] + '"]').val());
                chart.addSeries(seriesData);
            });

            $('#graph_over_time').addClass('hide');
            $('#graph_over_time2').removeClass('hide');
        };
        

        if (urls.length == 0) {
            // we already have all the data for urls
            loadData();
        } else {
            // get a list of data values from urls above and add to graphData
            // http://stackoverflow.com/questions/38582200/javascript-load-arbitrary-number-of-urls-with-getjson
            var promises = urls.map(url => $.getJSON(url));

            Promise.all(promises).then(function (data) {
                for (val in data) {
                    graphData[urls[val]] = data[val]['data'].map(eval);
                }

                loadData();
            });
        }
    };

    var setDataforGraph0 = function (peopleList, forwardShift) {
        var data = getURLData(peopleList, forwardShift, 0);

        var tmpUrls =  data.tmpUrls;
        var urls =  data.urls;
        var chart = $('#graph_over_time').highcharts();

        if (urls.length == 1) {
            var url = urls[0];
            $.getJSON(url).success(function (data) {
                graphData[url] = data['data'].map(eval);

                chart.series[0].remove(true);
                chart.addSeries({
                    data: graphData[url],
                    name: toTitleCase(urlsToNames[url]),
                    type: 'area'
                });
            });
        } else {
            var url = tmpUrls[0];
            chart.series[0].remove(true);
            chart.addSeries({
                data: graphData[url],
                name: toTitleCase(urlsToNames[url]),
                type: 'area'
            });
        }
    };

    var addColorToSeries = function (seriesData, color) {
        if (color.match(/^#([0-9a-f]{3}){1,2}$/i)) {
            seriesData['color'] = color;
        } else {
            console.log("Invalid Color: ", color);
        }
    }

    var addTypeToSeries = function (seriesData, cumulative) {
        if (cumulative == 0) {
            seriesData['type'] = graphType;
        } else {
            seriesData['type'] = cumulativeType;
        }
    }

    var addStackingToSeries = function(seriesData, cumulative) {
        if (cumulative == 0) {
            seriesData['stacking'] = graphStack;
        } else {
            seriesData['stacking'] = cumulativeStack;
        }
    }


    // ---------------------------------------- CUMULATIVE MESSAGE FREQUENCY GRAPHS ---------------------------------------- \\
    // global variable values for new data being added
    var cumulativeStack = 'normal';
    var cumulativeType = 'area'

    $.getJSON(totalMessagesURL('none', 1, 0, 0)).success(function (data) {
        evaluatedData = data['data'].map(eval);
        graphData[totalMessagesURL('none', 1, 0, 0)] = evaluatedData;

        $('#cumulative_over_time').highcharts({
            chart: {
                zoomType: 'x',
                panning: true,
                panKey: 'shift',
                height: height,
                width: width
            },
            title: {
                text: 'Cumulative Message Frequency',
                style: {
                    fontWeight: 'bold'
                }
            },
            subtitle: {
                text: 'Click and drag to zoom in, <b>Shift click</b> and drag to pan'
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


    $('#cumulative_over_time2').highcharts({
        chart: {
            zoomType: 'x',
            panning: true,
            panKey: 'shift',
            height: height,
            width: width
        },
        title: {
            text: 'Cumulative Message Frequency by Person',
        },
        subtitle: {
            text: 'Click and drag to zoom in, <b>Shift click</b> and drag to pan'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Number of messages'
            }
        },
        tooltip: {
            shared: true,
            valueSuffix: ' messages'
        },
        plotOptions: {
            area: {
                stacking: cumulativeStack,
                lineColor: '#666666',
                lineWidth: 1,
                marker: {
                    lineWidth: 1,
                    lineColor: '#666666'
                }
            }
        },
        series: [{}]
    });


    var setDataForGraph5 = function(peopleList, forwardShift) {
        var data = getURLData(peopleList, forwardShift, 1);

        var tmpUrls =  data.tmpUrls;
        var urls =  data.urls;

        var loadData = function () {
            var chart = $('#cumulative_over_time2').highcharts();
            // http://stackoverflow.com/questions/6604291/proper-way-to-remove-all-series-data-from-a-highcharts-chart
            while (chart.series.length > 0) {
                chart.series[0].remove(true);
            }

            // chart.xAxis[0].setCategories(graphData[tmpUrls[0]].categories);
            // Load graphData into highcharts
            $.each(tmpUrls, function (i, url) {
                var seriesData = {
                    data: graphData[url],
                    type: cumulativeType,
                    name: toTitleCase(urlsToNames[url]),
                    stacking: cumulativeStack
                };
                addColorToSeries(seriesData, $('input[data-color-person="' + urlsToNames[url] + '"]').val());
                chart.addSeries(seriesData);
            });

            $('#cumulative_over_time').addClass('hide');
            $('#cumulative_over_time2').removeClass('hide');
        };
        

        if (urls.length == 0) {
            // we already have all the data for urls
            loadData();
        } else {
            // get a list of data values from urls above and add to graphData
            // http://stackoverflow.com/questions/38582200/javascript-load-arbitrary-number-of-urls-with-getjson
            var promises = urls.map(url => $.getJSON(url));

            Promise.all(promises).then(function (data) {
                for (val in data) {
                    graphData[urls[val]] = data[val]['data'].map(eval);
                }

                loadData();
            });
        }
    };

     var setDataforGraph1 = function (peopleList, forwardShift) {
        var data = getURLData(peopleList, forwardShift, 1);

        var tmpUrls =  data.tmpUrls;
        var urls =  data.urls;
        var chart = $('#cumulative_over_time').highcharts();

        if (urls.length == 1) {
            var url = urls[0];
            $.getJSON(url).success(function (data) {
                graphData[url] = data['data'].map(eval);

                chart.series[0].remove(true);
                chart.addSeries({
                    data: graphData[url],
                    name: toTitleCase(urlsToNames[url]),
                    type: 'area'
                });
            });
        } else {
            var url = tmpUrls[0];
            chart.series[0].remove(true);
            chart.addSeries({
                data: graphData[url],
                name: toTitleCase(urlsToNames[url]),
                type: 'area'
            });
        }
    };


    // ---------------------------------------- MESSAGES BY DAY OF WEEK ---------------------------------------- \\
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
    var byTimeEveryone = true;  // tracks whether the by time graph has people or the aggregate data
    var byTimeWindow = 60;

    $.getJSON(messageByTimeURL('none', 60)).success(function (data) {
        categories = data['categories'];
        evaluatedData = data['data'];
        graphData[messageByTimeURL('none', 60)] = data;

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
                // headerFormat: '<b>{point.x}</b><br/>',
                pointFormat: '{series.name}: {point.y}<br/>',
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


    function setDataForGraph3(forwardShift, namesForGraph) {
        var chart = $('#time_of_day').highcharts();

        if (byTimeEveryone) {
            while (chart.series.length > 0) {  // delete all the data
                chart.series[0].remove(true);
            }

            var url = messageByTimeURL('none', forwardShift);
            if (url in graphData) {
                chart.addSeries(graphData[url]['data'][0]);
            } else {
                $.getJSON(url).success(function (data) {
                    graphData[url] = data;
                    chart.addSeries(graphData[url]['data'][0]);
                })
            }
        } else {

            function urlGetter(name) {
                return messageByTimeURL(name, forwardShift);
            }

            var tmpUrls = namesForGraph.map(urlGetter);
            
            var urls = [];
            for (val in tmpUrls) {
                if (!(tmpUrls[val] in graphData)) {
                    urls.push(tmpUrls[val]);
                }
            }

            function loadData () {
                for (i in tmpUrls) {
                    var name = urlsToNames[tmpUrls[i]];
                    var color = $('div[data-settings-num="3"] input[data-color-person="' + name + '"]').val();
                    var dataSeries = graphData[tmpUrls[i]]['data'][0];
                    addColorToSeries(dataSeries, color);
                    chart.addSeries(dataSeries);
                }

            }

            if (urls.length == 0) {
                loadData();
            } else {
                var promises = urls.map(url => $.getJSON(url));

                Promise.all(promises).then(function (data) {
                    for (val in data) {
                        graphData[urls[val]] = data[val];
                    }

                    loadData();
                });
            }
        }
    }


    // ------------------------------------------------ Clickable Buttons and mouse features ------------------------------------------------ \\

    $(".header-btn.prev").click(function() {
        window.location = window.location.href + 'prev/';
    });

    $(".header-btn.next").click(function() {
        window.location = window.location.href + 'next/';
    });

    var clearGraphsAndSettings = function() {
        $(".graph").addClass("hide");
        $(".settings-body").addClass("hide");
        $(".graph_type_button").removeClass("graph_button_active");
    };

    // Click functions for graph buttons, hides all graphs+settings and shows only appropriate one
    $(".graph_type_button").click(function() {
        clearGraphsAndSettings();
        $(this).addClass("graph_button_active");
        var button_number = $(this).data("graph-type");
        var settings = $("div").find("[data-settings-num='" + button_number + "']");
        var chart = $("div").find("[data-graph='" + button_number + "']");

        chart.removeClass("hide");
        settings.removeClass("hide");
        
        chartID = chart[0].id;
        var actualChart = $('#' + chartID).highcharts();
    });


    // Goes back to conversation selection screen
    $(".select-conversation").click(function () {
        window.location = window.location.href.substring(0, window.location.href.indexOf('conversation') + 12);
    });


    // helper function for zoom click fn
    var setZoom = function (chart, zoomType) {
        if (zoomType == "xy") {
            chart.pointer.zoomX = true;
            chart.pointer.zoomY = true;
            chart.pointer.zoomHor = true;
            chart.pointer.zoomVert = true;
        } else if (zoomType == "x") {
            chart.pointer.zoomX = true;
            chart.pointer.zoomY = false;
            chart.pointer.zoomHor = true;
            chart.pointer.zoomVert = false;
        } else {
            chart.pointer.zoomX = false;
            chart.pointer.zoomY = true;
            chart.pointer.zoomHor = false;
            chart.pointer.zoomVert = true;
        }
    }
    //  Zoom for graphs 0/4
    $("div[data-settings-num='0'] .zoom-types div.radio input").click(function () {
        var chart1 = $('#graph_over_time').highcharts();
        var chart2 = $('#graph_over_time2').highcharts();
        var zoomType = $(this).val();
        setZoom(chart1, zoomType);
        setZoom(chart2, zoomType);
    });
    //   Zoom for graphs 1/5
    $("div[data-settings-num='1'] .zoom-types div.radio input").click(function () {
        var chart1 = $('#cumulative_over_time').highcharts();
        var chart2 = $('#cumulative_over_time2').highcharts();
        var zoomType = $(this).val();
        setZoom(chart1, zoomType);
        setZoom(chart2, zoomType);
    });


    // Add or remove a person from graphs (4) or (5)
    var selectPersonSettings = function ($personDiv, $chartDiv, color, cumulative) {
        // Removes the class if it present, adds if it isn't
        if ($personDiv.hasClass("people-active")) {
            $personDiv.removeClass("people-active");
            if (!$chartDiv.hasClass("hide")) { // area graph is visible, remove graph data as well
                var chart = $chartDiv.highcharts();
                for (i = 0; i < chart.series.length; i++) {
                    if (chart.series[i]['name'].toLowerCase() == $personDiv.find(".specific-person").data("person")) {
                        chart.series[i].remove(true);
                    }
                }
            }
        } else {
            $personDiv.addClass("people-active");
            if (!$chartDiv.hasClass("hide")) { // area graph is visible, add graph data as well
                var url = totalMessagesURL($personDiv.find(".specific-person").data("person"), cumulative, 0, 0);
                var chart = $chartDiv.highcharts();

                if (url in graphData) {
                    var seriesData = {
                        name: toTitleCase($personDiv.find(".specific-person").data("person")),
                        data: graphData[url],
                    };
                    
                    addStackingToSeries(seriesData, cumulative);
                    addTypeToSeries(seriesData, cumulative);
                    addColorToSeries(seriesData, color);
                    chart.addSeries(seriesData);
                } else {
                    $.getJSON(url).success(function (data) {
                        graphData[url] = data['data'].map(eval);

                        var seriesData = {
                            name: toTitleCase(urlsToNames[url]),
                            data: graphData[url],
                        };

                        addStackingToSeries(seriesData, cumulative);
                        addTypeToSeries(seriesData, cumulative);
                        addColorToSeries(seriesData, color);
                        chart.addSeries(seriesData);
                    });
                }
            }
        }
    };
    // click function for person selection in settings for graph 0/4
    $("div[data-settings-num='0'] .people .tr-left").click(function () {
        var $chartDiv = $("#graph_over_time2");
        var color = $("div[data-settings-num='0'] input[data-color-person='" + $(this).find(".specific-person").data("person") + "']").val();
        selectPersonSettings($(this), $chartDiv, color, 0);
    });
    // click function for person selection in settings for graph 1/5
    $("div[data-settings-num='1'] .people .tr-left").click(function () {
        var $chartDiv = $("#cumulative_over_time2");
        var color = $("div[data-settings-num='1'] input[data-color-person='" + $(this).find(".specific-person").data("person") + "']").val();
        selectPersonSettings($(this), $chartDiv, color, 1);
    });
    // click function for person selection in graph 3
    $("div[data-settings-num='3'] .people .tr-left").click(function () {
        var chart = $("#time_of_day").highcharts();
        var person = $(this).find(".specific-person").data("person");

        if ($(this).hasClass("people-active")) {  // deleting this person
            $(this).removeClass("people-active");
            if (!byTimeEveryone) {
                for (i = 0; i < chart.series.length; i++) {
                    if (person == chart.series[i]['name'].toLowerCase()) {
                        chart.series[i].remove(true);
                    }
                }
            }
        } else {                                // adding this person
            $(this).addClass("people-active");
            if (!byTimeEveryone) {
                setDataForGraph3(byTimeWindow, [person]);
            }
        }
    });


    // Change color of graph
    var changeGraphColor = function ($chartDiv, newColor, person) {
        if (!$chartDiv.hasClass("hide") && newColor.match(/^#([0-9a-f]{3}){1,2}$/i)) { // the graph is visible and color is valid
            var chart = $chartDiv.highcharts();

            for (i = 0; i < chart.series.length; i++) {
                if (chart.series[i].name.toLowerCase() == person) {
                    chart.series[i].options.color = newColor;
                    chart.series[i].update(chart.series[i].options);
                }
            }
        }
    };
    //   Change colors for stacked graph over time (4)
    $("div[data-settings-num='0'] .tr input").change(function () {
        changeGraphColor($('#graph_over_time2'), $(this).val(), $(this).data("color-person"));
    });
    //  Change colors for stacked cumulative graph (5)
    $("div[data-settings-num='1'] .tr input").change(function () {
        changeGraphColor($('#cumulative_over_time2'), $(this).val(), $(this).data("color-person"));
    });
    //  Change colors for stacked messages over time (3)
    $("div[data-settings-num='3'] .tr input").change(function () {
        changeGraphColor($('#time_of_day'), $(this).val(), $(this).data("color-person"));
    });


    //  Clear all people for stacked graph over time (4)
    $("div[data-settings-num='0'] .clear-all").click(function () {
        $("div[data-settings-num='0'] .tr-left").each(function () {
            if ($(this).hasClass("people-active")) {
                $(this).click();
            }
        });
    });
    //  Clear all people for stacked cumulative over time (5)
    $("div[data-settings-num='1'] .clear-all").click(function () {
        $("div[data-settings-num='1'] .tr-left").each(function () {
            if ($(this).hasClass("people-active")) {
                $(this).click();
            }
        });
    });
    //  Clear all people for messages by time of day
    $("div[data-settings-num='3'] .clear-all").click(function () {
        $("div[data-settings-num='3'] .tr-left").each(function () {
            if ($(this).hasClass("people-active")) {
                $(this).click();
            }
        });
    });

    //  Select all people for stacked graph over time (4)
    $("div[data-settings-num='0'] .select-all").click(function () {
        $("div[data-settings-num='0'] .tr-left").each(function () {
            if (!$(this).hasClass("people-active")) {
                $(this).click();
            }
        });
    });
    //  Select all people for stacked cumulative over time (5)
    $("div[data-settings-num='1'] .select-all").click(function () {
        $("div[data-settings-num='1'] .tr-left").each(function () {
            if (!$(this).hasClass("people-active")) {
                $(this).click();
            }
        });
    });
    //  Select all people for messages by time of day
    $("div[data-settings-num='3'] .select-all").click(function () {
        $("div[data-settings-num='3'] .tr-left").each(function () {
            if (!$(this).hasClass("people-active")) {
                $(this).click();
            }
        });
    });


    //  Swaps graphs (0) and (4)
    $("div[data-settings-num='0'] #swap-graphs").click(function () {
        if ($('#graph_over_time2').hasClass("hide")) {
            var namesForGraph = [];
            $("div[data-settings-num='0'] .people-active .specific-person").each(function () {
                namesForGraph.push($(this).data("person"));
            });
            setDataForGraph4(namesForGraph.map(nameToUnderscores), forwardShift);
        } else {
            $("div").find("[data-graph-type='" + 0 + "']").click();
        }
    });
    //  Swaps graphs (1) and (5)
    $("div[data-settings-num='1'] #swap-graphs").click(function () {
        if ($('#cumulative_over_time2').hasClass("hide")) {
            var namesForGraph = [];
            $("div[data-settings-num='1'] .people-active .specific-person").each(function () {
                namesForGraph.push($(this).data("person"));
            });
            setDataForGraph5(namesForGraph.map(nameToUnderscores), forwardShift);
        } else {
            $("div").find("[data-graph-type='" + 1 + "']").click();
        }
    });
    // swap data for graph (3)
    $("div[data-settings-num='3'] #swap-graphs").click(function () {
        byTimeEveryone = !byTimeEveryone;  // reverse the boolean checker of graph types
        
        var namesForGraph = [];  // gather a list of names of active people
        $("div[data-settings-num='3'] .people-active .specific-person").each(function () {
            namesForGraph.push($(this).data("person"));
        });

        if (!byTimeEveryone) {  // if we switched to a graph of individual's delete the aggregate data series
            $("#time_of_day").highcharts().series[0].remove(true)
        }

        setDataForGraph3(byTimeWindow, namesForGraph);
    });


    //  helper function to get new values of stackType
    var getStackType = function (rawStackType) {
        if (rawStackType == "no-stack") {
            return null;
        } else if (rawStackType == "vertical-stack") {
            return "normal";
        } else {
            return "percent";
        }
    }
    // helper function to get new value of type 
    var getType = function (rawStackType) {
        if (rawStackType == "no-stack") {
            return 'line';
        } else {
            return "area";
        }
    }
    // Helper function to change stackType of graph with multiple people
    var changeStackType = function ($chart, stackType) {
        // http://stackoverflow.com/questions/18485939/highcharts-change-column-stacking-on-click
        if (stackType == "no-stack") {
            // update stack type
            for (var i = 0; i < $chart.series.length; i++) {
                $chart.series[i].update({
                    stacking: null,
                    type: 'line'
                }, false);
            }
            // update the y-axis title - http://stackoverflow.com/questions/5880235/change-highcharts-axis-title
            $chart.yAxis[0].axisTitle.attr({
                text: 'Number of messages'
            });

            //  Update tooltip
            $chart.tooltip.options.formatter = function () {
                var tip = Highcharts.dateFormat("%A, %b %e, %Y", this.x, true);
                 // http://php.net/manual/en/function.strftime.php
                 // http://api.highcharts.com/highcharts#Highcharts.dateFormat
                
                $.each(this.points, function () {
                    tip += '<br/>' + this.series.name + ': ' + '<b>' + numberWithCommas(this.y) + '</b>';
                });
                return tip;
            };
            $chart.redraw();
        } else if (stackType == "vertical-stack") {
            // update stack type
            for (var i = 0; i < $chart.series.length; i++) {
                $chart.series[i].update({
                    stacking: 'normal',
                    type: 'area'
                }, false);
            }
            // update the y-axis title
            $chart.yAxis[0].axisTitle.attr({
                text: 'Number of messages (stacked)'
            });

            //  Update tooltip
            $chart.tooltip.options.formatter = function () {
                var tip = Highcharts.dateFormat("%A, %b %e, %Y", this.x, true);
                
                $.each(this.points, function () {
                    tip += '<br/>' + this.series.name + ': ' + '<b>' + numberWithCommas(this.y) + '</b>';
                });
                return tip;
            };
            $chart.redraw();
        } else if (stackType == "percentage") {
            // update stack type
            for (var i = 0; i < $chart.series.length; i++) {
                $chart.series[i].update({
                    stacking: 'percent',
                    type: 'area'
                }, false);
            }
            // update the y-axis title
            $chart.yAxis[0].axisTitle.attr({
                text: "Relative Percentage"
            });

            //  update tooltip
            $chart.tooltip.options.formatter = function () {
                var tip = Highcharts.dateFormat("%A, %b %e, %Y", this.x, true);
                
                var total = 0;
                var length = 0;
                $.each(this.points, function () {
                    total += this.y;
                    length += 1;
                });
                var expectedPercent = 100 / length;
                
                tip += " - " + numberWithCommas(total);
                $.each(this.points, function () {
                    var percent = this.y / total * 100;
                    tip += '<br/>' + this.series.name + ': ' + '<b>' + (percent).toFixed(4) + "%" + '</b>';
                    if (percent > expectedPercent) {
                        tip += '<span style="color: green"> [+' + (percent - expectedPercent).toFixed(2) + '%]</span>';
                    } else {
                        tip += '<span style="color: red"> [-' + (expectedPercent - percent).toFixed(2) + '%]</span>';
                    }
                });
                return tip;
            };
            $chart.redraw();
        } else {
            console.log("stacktype click function recieved an unknown stack type:", stackType);
        }
    };
    // Change stack type for graph (1)
    $("div[data-settings-num='0'] .stack-type div.radio input").click(function () {
        var type = $(this).val();
        graphStack = getStackType(type);
        graphType = getType(type);

        changeStackType($("#graph_over_time2").highcharts(), type);
    });
    // Change stack type for graph (5)
    $("div[data-settings-num='1'] .stack-type div.radio input").click(function () {
        var type = $(this).val();
        cumulativeStack = getStackType(type);
        cumulativeType = getType(type);

        changeStackType($("#cumulative_over_time2").highcharts(), type);
    });


    $("#test").click(function () {
        setDataforGraph0(['none'], 300);
    });


    // ------------------------------------------------ On Page Load Stuff ------------------------------------------------ \\
    $("div").find("[data-graph-type='" + 0 + "']").click()  // Load the first graph


    // Select top 3 participants for area graph
    for (i = 0; i < Math.min(3, names.length); i++) {
        $("div").find("[data-person='" + names[i] + "']").click();
    }

    // Setting default colors
    $(".tr input").each(function () {
        $(this).val( getColors($(this).data("rank") - 1) );
    });



    // Shrink title size
    // Some inspiration http://stackoverflow.com/questions/6112660/how-to-automatically-change-the-text-size-inside-a-div
    var header = $(".header");
    var header_div = $(".header .title");
    while (header_div.outerHeight() > header.height()) {
        header_div.css("font-size", parseInt(header_div.css("font-size")) - 1 + "px");
    }
    header_div.css("visibility", "visible");

});
