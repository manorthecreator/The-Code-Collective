$(function () {
    console.log("✅ product_list.js loaded. jQuery version:", $.fn.jquery);

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
    $('.swatch').on('click', function () {
        $(this).toggleClass('active');
        applyFilters();
    });

    //    ---------- Size buttons (single-select) ---------- 
    $('.size-btn').on('click', function () {
        $(this).siblings().removeClass('active');
        $(this).toggleClass('active');
        applyFilters();
    });

    //    ---------- Category change (submit immediately) ---------- 
    $('input[name="category"]').on('change', function () {
        applyFilters();
    });

    //    ---------- Apply price button (submit) ---------- 
    $('#applyPrice').on('click', function () {
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