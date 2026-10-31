$(function () {
    console.log("✅ product_list.js loaded. jQuery version:", $.fn.jquery);

    //CSRF Token Setup which is REQUIRED for wishlist POST
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


    // Collapse Filter Block
    $('.collapse-btn').on('click',function(){
        const $block=$(this).closest('.filter-block');
        $block.toggleClass('collapsed');
        $(this).css('transform',$block.hasClass('collapsed') ? 'rotate(180deg)' : '');
    });


    // Price Slider
    const $min = $('#minPrice');
    const $max = $('#maxPrice');
    const $minLabel = $('#minPriceValue');
    const $maxLabel = $('#maxPriceValue');
    const $fill = $('#rangeFill');
    const RANGE_MIN = parseInt($min.attr('min'), 10);
    const RANGE_MAX = parseInt($min.attr('max'), 10);
    const GAP = 50;
    function paintSlider() {
        const minVal = parseInt($min.val(), 10);
        const maxVal = parseInt($max.val(), 10);
        $minLabel.text('Rs ' + minVal);
        $maxLabel.text('Rs ' + maxVal);
        const span = RANGE_MAX - RANGE_MIN;
        const leftPct  = ((minVal - RANGE_MIN) / span) * 100;
        const rightPct = ((maxVal - RANGE_MIN) / span) * 100;
        $fill.css({
            left:  leftPct + '%',
            right: (100 - rightPct) + '%'
        });
    }
    $min.on('input', function () {
        const minVal = parseInt($min.val(), 10);
        const maxVal = parseInt($max.val(), 10);
        if (minVal > maxVal - GAP) {
            $min.val(maxVal - GAP);
        }
        paintSlider();
    });
    $max.on('input', function () {
        const minVal = parseInt($min.val(), 10);
        const maxVal = parseInt($max.val(), 10);
        if (maxVal < minVal + GAP) {
            $max.val(minVal + GAP);
        }
        paintSlider();
    });
    paintSlider();


    //    ---------- Color swatches (multi-select) ---------- 
    $(document).on('click', '.swatch', function () {
        $(this).toggleClass('active');
        applyFilters();
    });

    //    ---------- Size buttons (single-select) ---------- 
    $(document).on('click', '.size-btn', function () {
        $(this).siblings().removeClass('active');
        $(this).toggleClass('active');
        applyFilters();
    });

    //    ---------- Category change (submit immediately) ---------- 
    $(document).on('change', 'input[name="category"]', function () {
        applyFilters();
    });

    //    ---------- Apply price button (submit) ---------- 
    $(document).on('click', '#applyPrice', function () {
        applyFilters();
    });

    // ---------- Collect all filter values ---------- 
    function getFilters() {
    const params = {};

    // Category
    const category = $('input[name="category"]:checked').val();
    if (category) {
        params.category = category;
    }
    // MAX & MIN Price
    params.max_price = $('#maxPrice').val();
    params.min_price=$('#minPrice').val();

    // Colors (multi)
    const colors = $('.swatch.active').map(function () {
      return $(this).data('color');
    }).get();
    if (colors.length) {
        params.colors = colors.join(',');
    }

    // Size (single)
    const size = $('.size-btn.active').data('size');
    if (size) {
        params.size = size;
    }
    return params;
  }

  //Wishlist Heart
  $(document).on('click', '.wishlist-btn', function (e) {
        e.preventDefault();
        var $btn = $(this);
        var url = $btn.data('url'); 
        if (!url) {
            console.error("No data-url attribute found on the button.");
            return;
        }
        $.ajax({
            type: 'POST',
            url: url,
            data: { 'csrfmiddlewaretoken': csrftoken },
            success: function (response) {
                if (response.added) {
                    $btn.addClass('active');
                } else {
                    $btn.removeClass('active');
                    if ($('#wishlistGrid').length > 0) {
                        $btn.closest('.product-card').fadeOut(300, function() {
                            $(this).remove();
                            if ($('#wishlistGrid').children().length === 0) {
                                location.reload();
                            }
                        });
                    }
                }
            },
            error: function (xhr) {
                if (xhr.status === 403) {
                    window.location.href = "/accounts_app/login/?next=" + window.location.pathname;
                } else {
                    console.log("Wishlist error:", xhr.responseText);
                }
            }
        });
    });


//   -----------------------AJAX Part------------------------------------------
  function applyFilters(){
    const params=getFilters();

    $.ajax({
        url:window.location.pathname,
        type:'GET',
        data:params,
        headers:{
            'X-Requested-With': 'XMLHttpRequest'
        },
        success:function(html){
            $('#productGrid').html(html);

            const queryString=$.param(params);
            const newUrl=queryString
                ? window.location.pathname +'?'+queryString
                : window.location.pathname;
            window.history.replaceState({},'',newUrl);
        },
        error:function(xhr){
            console.error('AJAX errror:',xhr.status,xhr.responseText);
        }
    })
  }
});