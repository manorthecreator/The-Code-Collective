$(function(){
    // CSRF Token setup required for AJAX POST
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

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

    //Review form
    $('#toggleReviewForm').on('click', function () {
        const $form = $('#reviewFormContainer');
        if ($form.is(':visible')) {
            $form.slideUp();
            $(this).text('Write a Review');
        } else {
            $form.slideDown();
            $(this).text('Cancel Review');
        }
    });
    //AJAX PART
    $('#reviewForm').on('submit', function(e) {
        e.preventDefault();
        var $form = $(this);
        var url = $form.data('url');
        var $btn = $form.find('.btn-submit-review');
        $btn.prop('disabled', true).text('Submitting...');

        $.ajax({
            type: 'POST',
            url: url,
            data: $form.serialize(),
            success: function(response) {
                if (response.success) {
                    var starsHtml = '';
                    for (var i = 1; i <= 5; i++) {
                        starsHtml += (i <= response.rating) ? '★' : '☆';
                    } 
                    var $newReview = $('<div class="review-card" style="display: none;"></div>');
                    var $avatar = $('<div class="review-avatar"></div>').html(
                        '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">' +
                            '<circle cx="12" cy="12" r="12" fill="#4A3028"/>' +
                            '<circle cx="12" cy="8" r="4" fill="#FFFFFF"/>' +
                            '<path d="M4 20C4 16.6863 6.68629 14 10 14H14C17.3137 14 20 16.6863 20 20" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>' +
                        '</svg>'
                    );
                    var $content = $('<div class="review-content"></div>');
                    $content.append($('<h4 class="review-name"></h4>').text(response.name));
                    $content.append($('<div class="review-stars"></div>').text(starsHtml));
                    $content.append($('<p class="review-text"></p>').text(response.comment));

                    $newReview.append($avatar);
                    $newReview.append($content);
                    $('.no-reviews-text').remove();
                    $('#reviewsList').prepend($newReview);
                    $newReview.fadeIn(400);
                    $form.trigger('reset');
                    $btn.prop('disabled', false).text('Submit Review');
                    $('#toggleReviewForm').trigger('click');
                }
            },
            error: function(xhr) {
                $btn.prop('disabled', false).text('Submit Review');
                console.log(xhr.responseText);
                alert('There was an error submitting. Check the console.');
            }
        });
    });

    //Wishlist
    $(document).on('click', '.wishlist-btn-detail, .wishlist-toggle-btn', function (e) {
        e.preventDefault();
        var $btn = $(this);
        var url = $btn.data('url'); 

        $.ajax({
            type: 'POST',
            url: url,
            data: { 'csrfmiddlewaretoken': csrftoken },
            success: function (response) {
                var $imageHeart = $('.wishlist-btn-detail');
                var $bottomBtn = $('.wishlist-toggle-btn');
                var $btnText = $bottomBtn.find('.wishlist-btn-text');

                if (response.added) {
                    $imageHeart.addClass('active');
                    $bottomBtn.addClass('active');
                    $btnText.text('Remove from Wishlist');
                } else {
                    $imageHeart.removeClass('active');
                    $bottomBtn.removeClass('active');
                    $btnText.text('Add to Wishlist');
                }
            },
            error: function (xhr) {
                if (xhr.status === 403) {
                    window.location.href = "/accounts_app/login/?next=" + window.location.pathname;
                } else {
                    console.log("Wishlist error:", xhr.responseText);
                    alert("Something went wrong. Please try again.");
                }
            }
        });
    });
});