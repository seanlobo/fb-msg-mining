$(document).ready(function(){
  //change select to input to work for non dropdown questions
    $('.word_cloud_type_controller select').change(function() {
        if (this.value == "Default") {
            $(".only_default").fadeIn(750);
            $(".not_layered").fadeIn(750);
            shapeController();
  		} else if (this.value == "Layered") {
            $(".only_default").fadeOut(1000);
            $(".not_layered").fadeOut(1000);
        } else {  // Polarity
            $(".only_default").fadeOut(1000);
            $(".not_layered").fadeIn(750);
            shapeController();
        }
 	});

    function shapeController() {
        console.log($('.shape-controller select').val());
 	    if ($('.shape-controller select').val() == "image") {
 	        $(".only_image").fadeIn(750);
 	    } else {
 	        $(".only_image").fadeOut(1000);
 	    }
 	};
 	$('.shape-controller select').change(shapeController);
 	shapeController();

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
});
