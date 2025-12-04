/* ===================================================================
    
    Author          : Kazi Sahiduzzaman
    Template Name   : Oreg - Organic Shop HTML Template
    Version         : 1.0 (Fixed Preloader Issue - Dec 2025)
    
* ================================================================= */
(function($) {
    "use strict";

    $(document).ready(function() {

        /* ==================================================
            # Data Background
        ===============================================*/
        $("[data-background]").each(function(){
            $(this).css("background-image","url(" + $(this).attr("data-background") +")");
        });
        
        /* ==================================================
            # Fun Factor Init
        ===============================================*/
        $('.timer').countTo();
        $('.fun-fact').appear(function() {
            $('.timer').countTo();
        }, {accY: -100});

        /* ==================================================
            # Quantity
        ===============================================*/
        function wcqib_refresh_quantity_increments() {
            jQuery("div.quantity:not(.buttons_added), td.quantity:not(.buttons_added)").each(function(a, b) {
                var c = jQuery(b);
                c.addClass("buttons_added"), c.children().first().before('<input type="button" value="-" class="minus" />'), c.children().last().after('<input type="button" value="+" class="plus" />')
            })
        }
        String.prototype.getDecimals || (String.prototype.getDecimals = function() {
            var a = this,
                b = ("" + a).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
            return b ? Math.max(0, (b[1] ? b[1].length : 0) - (b[2] ? +b[2] : 0)) : 0
        });
        jQuery(document).ready(function() {
            wcqib_refresh_quantity_increments()
        });
        jQuery(document).on("updated_wc_div", function() {
            wcqib_refresh_quantity_increments()
        });
        jQuery(document).on("click", ".plus, .minus", function() {
            var a = jQuery(this).closest(".quantity").find(".qty"),
                b = parseFloat(a.val()),
                c = parseFloat(a.attr("max")),
                d = parseFloat(a.attr("min")),
                e = a.attr("step");
            b && "" !== b && "NaN" !== b || (b = 0), "" !== c && "NaN" !== c || (c = ""), "" !== d && "NaN" !== d || (d = 0), "any" !== e && "" !== e && void 0 !== e && "NaN" !== parseFloat(e) || (e = 1), jQuery(this).is(".plus") ? c && b >= c ? a.val(c) : a.val((b + parseFloat(e)).toFixed(e.getDecimals())) : d && b <= d ? a.val(d) : b > 0 && a.val((b - parseFloat(e)).toFixed(e.getDecimals())), a.trigger("change")
        });

        /* ==================================================
            # Wow Init
        ===============================================*/
        var wow = new WOW({
            boxClass: 'wow',
            animateClass: 'animated',
            offset: 0,
            mobile: true,
            live: true
        });
        wow.init();

        /* ==================================================
            # Smooth Scroll
        =============================================== */
        $('a.smooth-menu').on('click', function(event) {
            var $anchor = $(this);
            var headerH = '85';
            $('html, body').stop().animate({
                scrollTop: $($anchor.attr('href')).offset().top - headerH + "px"
            }, 1500, 'easeInOutExpo');
            event.preventDefault();
        });

        /* ==================================================
            # MixitUp 
        =============================================== */
        $('#portfolio').mixItUp({  
            selectors: {
                target: '.tile',
                filter: '.filter',
                sort: '.sort-btn'
            },
            animation: {
                animateResizeContainer: false,
                effects: 'fade scale'
            }
        });

        /* ==================================================
            # Accordion Menu
        =============================================== */
        $(document).on('click','.panel-group .panel',function(e) {
            e.preventDefault();
            $(this).addClass('panel-active').siblings().removeClass('panel-active');
        });

        /* ==================================================
            # imagesLoaded active
        ===============================================*/
        $('.filter-active').imagesLoaded(function () {
            var $filter = '.filter-active',
                $filterItem = '.filter-item',
                $filterMenu = '.filter-menu-active';

            if ($($filter).length > 0) {
                var $grid = $($filter).isotope({
                    itemSelector: $filterItem,
                    filter: '*',
                    masonry: {
                        columnWidth: 1
                    }
                });

                $($filterMenu).on('click', 'button', function () {
                    var filterValue = $(this).attr('data-filter');
                    $grid.isotope({ filter: filterValue });
                });

                $($filterMenu).on('click', 'button', function (event) {
                    event.preventDefault();
                    $(this).addClass('active').siblings('.active').removeClass('active');
                });
            }
        });

        /* ==================================================
            # Magnific popup init
        ===============================================*/
        $(".popup-link, .popup-gallery").magnificPopup({
            type: 'image',
            gallery: { enabled: true }
        });

        $(".popup-youtube, .popup-vimeo, .popup-gmaps").magnificPopup({
            type: "iframe",
            mainClass: "mfp-fade",
            removalDelay: 160,
            preloader: false,
            fixedContentPos: false
        });

        /* ==================================================
            # Typed Text
        ===============================================*/
        if ($(".typed").length) {
            $(".typed").typed({
                strings: ["IT Company ", "Software Company ", "Digital Marketplace "],
                typeSpeed: 100,
                startDelay: 1200,
                backSpeed: 10,
                backDelay: 600,
                loop: true,
                loopCount: Infinity,
                showCursor: false,
                cursorChar: "|",
                contentType: 'html'
            });
        }

        /* ==================================================
            # Owl Carousels
        ===============================================*/
        $('.sldr, .hero-sldr, .partner-sldr, .scr-sldr, .rev-sldr, .cate-sol').owlCarousel({
            loop: true,
            margin: 30,
            nav: true,
            dots: false,
            autoplay: true,
            autoplayTimeout: 9000,
            navText: ["<i class='ti-angle-left'></i>","<i class='ti-angle-right'></i>"],
            responsive: {
                0: { items: 1 },
                768: { items: 2 },
                992: { items: 3 },
                1200: { items: 4 }
            }
        });

        /* ==================================================
            # Countdown
        ===============================================*/
        var nextyear = '12/31/' + (new Date().getFullYear() + 1) + ' 23:59:59';
        $('#example').countdown({
            date: nextyear,
            offset: +6,
            day: 'Day',
            days: 'Days'
        });

        /* ==================================================
            # Contact Form
        ===============================================*/
        $('.contact-form').submit(function() {
            var action = $(this).attr('action');
            $("#message").slideUp(750, function() {
                $('#message').hide();
                $('#submit').after('<img src="assets/img/logo/ajax-loader.gif" class="loader" />').attr('disabled','disabled');

                $.post(action, {
                    name: $('#name').val(),
                    email: $('#email').val(),
                    subject: $('#subject').val(),
                    website: $('#website').val(),
                    comments: $('#comments').val()
                }, function(data) {
                    document.getElementById('message').innerHTML = data;
                    $('#message').slideDown('slow');
                    $('.contact-form img.loader').fadeOut('slow',function(){$(this).remove()});
                    $('#submit').removeAttr('disabled');
                });
            });
            return false;
        });

        /* ==================================================
            # Scroll to Top Button
        ===============================================*/
        var mybutton = document.getElementById("scrtop");
        window.onscroll = function() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                mybutton.style.display = "block";
            } else {
                mybutton.style.display = "none";
            }
        };

        /* ==================================================
            # Wodry Animation
        ===============================================*/
        $('.wodryRX').wodry({
            animation: 'rotateX',
            delay: 2000,
            animationDuration: 1600
        });

    }); // End $(document).ready()

    /* ==================================================
        PRELOADER - FIXED & BULLETPROOF (MUST BE OUTSIDE document.ready!)
    ===================================================*/
    $(window).on('load', function() {
        $(".se-pre-con").fadeOut(800);
    });

    // Safety fallback #1: hide after 3.5 seconds max
    setTimeout(function() {
        $(".se-pre-con").fadeOut(600);
    }, 3500);

    // Safety fallback #2: completely remove from DOM after 5 seconds
    setTimeout(function() {
        $(".se-pre-con").remove();
    }, 5000);

})(jQuery); // End jQuery