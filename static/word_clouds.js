$(document).ready(function(){
  //change select to input to work for non dropdown questions
    $('.word_cloud_type_controller select').change(function() {
        if (this.value == "default") {
            $(".only_default").fadeIn(750);
            $(".not_layered").fadeIn(750);
            $(".only_layered").fadeOut(1000);
            shapeController();
  		} else if (this.value == "layered") {
            $(".only_default").fadeOut(1000);
            $(".not_layered").fadeOut(1000);
            $(".only_layered").fadeIn(750);
        } else {  // polarity
            $(".only_layered").fadeOut(1000);
            $(".only_default").fadeOut(1000);
            $(".not_layered").fadeIn(750);
            shapeController();
        }
 	});
 	$('.word_cloud_type_controller select').trigger("change");

    function shapeController() {
 	    if ($('.shape-controller select').val() == "image") {
 	        $(".only_image").fadeIn(750);
 	    } else {
 	        $(".only_image").fadeOut(1000);
 	    }
 	};
 	$('.shape-controller select').change(shapeController);
 	shapeController();

//    For default form
 	function handleNumColors() {
 	    var numColors = parseInt($(".num-colors-default").val());

        if (numColors < 1) {
            $(".num-colors-default").val(1)
            numColors = 1
        } else if (numColors > 5) {
            $(".num-colors-default").val(5)
            numColors = 5
        }

        for (i = 1; i <= numColors; i++) {
            $("[data-color-ind='" + i + "']").show();
        }
        for (i = numColors + 1; i <= 5; i++) {
            $("[data-color-ind='" + i + "']").hide();
        }
        $(".color-container").css("margin-bottom", (numColors * 30 + 50) + 'px');
 	};
 	handleNumColors();
 	$(".num-colors-default").change(handleNumColors);

// 	For layered form
 	function handleNumLayers() {
 	    var numLayers = parseInt($(".num_layer_controller input").val());

 	    console.log(numLayers);

 	    if (numLayers < 1) {
            $(".num_layer_controller input").val(1)
            numLayers = 1
        } else if (numLayers > 5) {
            $(".num_layer_controller input").val(5)
            numLayers = 5
        }

        for (i = 1; i <= numLayers; i++) {
            $("[data-layer='" + i + "']").fadeIn(750);
        }
        for (i = numLayers + 1; i <= 5; i++) {
            $("[data-layer='" + i + "']").fadeOut(1000);
        }
        $(".num-colors-layer").trigger("change");
 	};
 	handleNumLayers();
 	$(".num_layer_controller").change(handleNumLayers);

// 	For layered form
 	$(".num-colors-layer").change(function () {
 	    var numColors = parseInt($(this).val());
        var layerNum = parseInt($(this).data("layer"));

        if (numColors < 1) {
            $(this).val(1);
            numColors = 1;
        } else if (numColors > 5) {
            $(this).val(5);
            numColors = 5;
        }

        for (i = 1; i <= numColors; i++) {
            $("[data-color-ind='" + i + "'][data-layer='" + layerNum + "']").show();
        }
        for (i = numColors + 1; i <= 5; i++) {
            $("[data-color-ind='" + i + "'][data-layer='" + layerNum + "']").hide();
        }
        $(".color-container" + layerNum).css("margin-bottom", (numColors * 30 + 50) + 'px');
 	});
 	for (i = 1; i <= 2; i++) {
 	    $(".num-colors-layer[data-layer='" + i + "']").trigger("change");
 	}


	$(".png-suffix input").keydown(function(e) {
        var oldvalue=$(this).val();
        var field=this;
        setTimeout(function () {
            if (field.value.substr(field.value.length - 4) != ".png" ) {
                $(field).val(oldvalue);
            }
        }, 1);
	});



	$(".only_image").hide();
	$(".only_layered").hide();
	$(".num-colors-layer").trigger("change");

});
