$(document).ready(function() {
    var MAX_COLORS = parseInt($("#max_colors").val());
    var MAX_LAYERS = parseInt($("#max_layers").val());


//  Type controller for form. Hides and shows appropriate elements based on word cloud type
    $('.word_cloud_type_controller select').change(function() {
        if (this.value == "default") {
            $(".only_default").fadeIn(750);
            $(".not_layered").fadeIn(750);
            $(".only_layered").fadeOut(1000);
            $(".only_polarity").fadeOut(1000);
            $('.shape-controller select').trigger("change");
  		} else if (this.value == "layered") {
            $(".only_default").fadeOut(1000);
            $(".only_polarity").fadeOut(1000);
            $(".not_layered").fadeOut(1000);
            $(".only_layered").fadeIn(750);
        } else {  // polarity
            $(".only_layered").fadeOut(1000);
            $(".only_default").fadeOut(1000);
            $(".not_layered").fadeIn(750);
            $(".only_polarity").fadeIn(750);
            $('.shape-controller select').trigger("change");
        }
 	});
 	$('.word_cloud_type_controller select').trigger("change");


//  Shows image specific elements iff shape is image. Does not apply to word clouds of type "layered"
    $('.shape-controller select').change(function () {
 	    if ($(this).val() == "image") {
 	        $(".only_image").fadeIn(750);
 	        $("#only-image-choice").trigger("change");
 	    } else {
 	        $(".only_image").fadeOut(1000);
 	    }
 	});
 	$('.shape-controller select').trigger("change");


// 	Handle number of visible layer sections for "layered" word cloud
 	function handleNumLayers() {
 	    var numLayers = parseInt($(".num_layer_controller input").val());

 	    if (numLayers < 1) {
            $(".num_layer_controller input").val(1)
            numLayers = 1
        } else if (numLayers > MAX_LAYERS) {
            $(".num_layer_controller input").val(MAX_LAYERS)
            numLayers = MAX_LAYERS
        }

        for (i = 1; i <= numLayers; i++) {
            $("[data-layer='" + i + "']").fadeIn(750);
        }
        for (i = numLayers + 1; i <= MAX_LAYERS; i++) {
            $("[data-layer='" + i + "']").fadeOut(1000);
        }
        $(".num-colors").trigger("change");
 	};
 	handleNumLayers();
 	$(".num_layer_controller").change(handleNumLayers);


//    Handling number of colors for all wc types
 	$(".num-colors").change(function () {
 	    var numColors = parseInt($(this).val());
 	    var wcType = $('.word_cloud_type_controller select').val();
        var colorSuffix = null;             // to handle selecting appropriate color
 	    var colorContainerSuffix = null;    // form elements based on word cloud type

        if (wcType == "default") {
        // For the "default" type we don't need a suffix, the selectors below select the elements we want
            colorSuffix = "";
            colorContainerSuffix = "";
        } else if (wcType == "polarity") {
            var polarity = $(this).data("polarity");
            colorSuffix = "'][data-polarity='" + polarity;
            colorContainerSuffix = polarity + "_polarity";
        } else {  // "layered"
            var layerNum = parseInt($(this).data("layer"));
            colorSuffix = "'][data-layer='" + layerNum;
            colorContainerSuffix = "" + layerNum;
        }

        // Edge case testing, set the value to the min or max if out of bounds
        if (numColors < 1) {
            $(this).val(1)
            numColors = 1
        } else if (numColors > MAX_COLORS) {
            $(this).val(MAX_COLORS)
            numColors = MAX_COLORS
        }

        // Hide/Show appropriate number of colors
        for (i = 1; i <= numColors; i++) {
            $("[data-color-ind='" + i + colorSuffix + "']").show();
        }
        for (i = numColors + 1; i <= MAX_COLORS; i++) {
            $("[data-color-ind='" + i + colorSuffix + "']").hide();
        }

        // Set margin on color container element appropriately
        $(".color-container" + colorContainerSuffix).css("margin-bottom", (numColors * 30 + 50) + 'px');
 	});
 	$(".num-colors").trigger("change");


//  For output name
	$(".png-suffix input").keydown(function(e) {
        var oldvalue=$(this).val();
        var field=this;
        setTimeout(function () {
            if (field.value.substr(field.value.length - 4) != ".png" ) {
                $(field).val(oldvalue);
            }
        }, 1);
	});


//	Setting height/width for image clouds and showing preview image
    $("#only-image-choice").change(function () {
        var divData = $("div[data-image-name='" + $(this).val() + "']");

        $(".only_default.only_image img").hide();
        $(".only_default.only_image img[data-img='" + $(this).val() + "']").show();

        var width = parseInt(divData.data("width"));
        var height = parseInt(divData.data("height"));


        $("#width").val(width);
        $("#height").val(height);

    });


    $("#submit").click(function () {
        if (parseInt($("#width").val()) > 0 && parseInt($("#height").val()) > 0) {
            $("form").fadeOut(3000);
            $("h1").fadeIn(6000);
        }
    });



//  On page load hiding
    var wcType = $('.word_cloud_type_controller select').val();
    if (wcType == "default") {
        $(".only_layered").hide();
    	$(".only_polarity").hide();

    } else if (wcType == "layered") {
    	$(".only_polarity").hide();

    } else {  // "polarity"
    	$(".only_layered").hide();

    }

	if ($('.shape-controller select').val() != "image") {
	    $(".only_image").hide();
	}
});
