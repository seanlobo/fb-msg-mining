$(function () {
    //  floatThead library, making the table head visible when scrolling
    var $actualTable = $('table');
    $actualTable.floatThead({
        scrollContainer: function($table) {
            return $table.closest('.table-background');
        },
        position: "fixed"
    });
    $actualTable.floatThead();

    //  Resizes the table to fit to max height while leavign at least 30 pixels on the bottom
    var resizeTable = function() {
        var windowHeight = $(window).height();
        var offsetHeight = $actualTable.offset().top;
        var minBottomPadding = 30;

        var tableHeight = (windowHeight - offsetHeight - minBottomPadding) - (windowHeight - offsetHeight - minBottomPadding) % 40;

        console.log(windowHeight, offsetHeight, tableHeight);

        $("div.table-background").height(tableHeight + 1);
        $actualTable.floatThead();
    };    
    $(window).resize(resizeTable); // add resizeTable fn to window resize action
    resizeTable(); // Resize table on page load

    //  Row click sorting
    $(".th-button").click(function() {
        var sort = $(this).data("row-name");
        var mode;
        if ($(".image-active").data("name") != sort || $(".image-active").data("mode") == "up") {
            mode = "down";
        } else {
            mode = "up";
        }
        // the below effectively appends the following to the url and reloads the page
        window.location = "?sort=" + sort + "&mode=" + mode; 
    })

    //  Page start - applying images to row <image>
    active = $('.image-active')
    if (active.data('mode') == 'down') {
        active.attr("src", "/static/resources/down_arrow.png");
    } else {
        active.attr("src", "/static/resources/up_arrow.png");
    }
});
