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
});