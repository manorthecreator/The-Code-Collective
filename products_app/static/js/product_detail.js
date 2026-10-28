$(function(){

    // Vertical Thumbnails
    $('.product-thumbnails').slick({
        slidesToShow:4,
        slidesToScroll:1,
        asNavFor:'.product-main-slider',
        dots:false,
        arrows:false,
        focusOnSelect:true,
        vertical:true,
        verticalSwiping:true,
        infinite:true
    });

    //Main Image Slider
    $('.product-main-slider').slick({
        slidesToShow:1,
        slidesToScroll:1,
        arrows:false,
        fade:true,
        asNavFor:'.product-thumbnails',
        infinite:true
    });

    //Color Selection
    $('.color-swatch').on('click', function () {
        $('.color-swatch').removeClass('active');
        $(this).addClass('active');
    });

    //Size Selection
    $('.size-box').on('click', function () {
        $('.size-box').removeClass('active');
        $(this).addClass('active');
    });

    //Quantity Buttons
    $('#qtyPlus').on('click', function () {
        let val = parseInt($('#qtyInput').val());
        $('#qtyInput').val(val + 1);
    });
    $('#qtyMinus').on('click', function () {
        let val = parseInt($('#qtyInput').val());
        if (val > 1) {
            $('#qtyInput').val(val - 1);
        }
    });

    //Tab Switching
    $('.tab-btn').on('click', function () {
        $('.tab-btn').removeClass('active');
        $(this).addClass('active');
        
        $('.tab-content').hide();
        $('#' + $(this).data('target')).show();
    });
});