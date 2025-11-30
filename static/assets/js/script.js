/*-----------------------------------------------------------------------------------
    Template Name: Munfirm - Agriculture & Organic Food HTML Template
    Template URI: https://webtend.net/demo/html/munfirm/
    Author: WebTend
    Author URI:  https://webtend.net/
    Version: 1.0

    Note: This is Main JS File.
-----------------------------------------------------------------------------------
	CSS INDEX
	===================
    01. Header Style
    02. Dropdown menu
    03. Submenu Dropdown
    04. Menu Hidden
    05. Search Box
    06. Product Gallery
    07. Video Popup
    08. Main Slider
    09. Slider Two
    10. Product Slider
    11. Product Slider Two
    12. Team Member
    13. Two Row Team
    14. Category Slider
    15. Gllery Slider 
    16. Gllery Slider Two
    17. Feedback Slider 
    18. Feedback Slider Two
    19. News Slider
    20. Client Logo
    21. Fact Counter
    22. Team skill Counter
    23. Portfolio Filtering
    24. Scroll to Top
    25. CountDown
    26. Nice Select
    27. WOW Animation
    28. Quantity Number
    29. Price Totaling
    30. Preloader
    
-----------------------------------------------------------------------------------*/

(function ($) {

    "use strict";

    $(document).ready(function () {

        // 01. Header Style and Scroll to Top
        function headerStyle() {
            if ($('.main-header').length) {
                var windowpos = $(window).scrollTop();
                var siteHeader = $('.main-header');
                var scrollLink = $('.scroll-top');
                if (windowpos >= 250) {
                    siteHeader.addClass('fixed-header');
                    scrollLink.fadeIn(300);
                } else {
                    siteHeader.removeClass('fixed-header');
                    scrollLink.fadeOut(300);
                }
            }
        }
        headerStyle();
        
        
        // 02. Dropdown menu
        var mobileWidth = 992;
        var navcollapse = $('.navigation li.dropdown');

        navcollapse.hover(function () {
            if ($(window).innerWidth() >= mobileWidth) {
                $(this).children('ul').stop(true, false, true).slideToggle(300);
                $(this).children('.megamenu').stop(true, false, true).slideToggle(300);
            }
        });
        
        // 03. Submenu Dropdown Toggle
        if ($('.main-header .navigation li.dropdown ul').length) {
            $('.main-header .navigation li.dropdown').append('<div class="dropdown-btn"><span class="fas fa-chevron-down"></span></div>');

            //Dropdown Button
            $('.main-header .navigation li.dropdown .dropdown-btn').on('click', function () {
                $(this).prev('ul').slideToggle(500);
                $(this).prev('.megamenu').slideToggle(800);
            });
            
            //Disable dropdown parent link
            $('.navigation li.dropdown > a').on('click', function (e) {
                e.preventDefault();
            });
        }
        
        //Submenu Dropdown Toggle
        if ($('.main-header .main-menu').length) {
            $('.main-header .main-menu .navbar-toggle').click(function () {
                $(this).prev().prev().next().next().children('li.dropdown').hide();
            });
        }
        
        
         
        // 04. Menu Hidden Sidebar Content Toggle
        if($('.menu-sidebar').length){
            //Show Form
            $('.menu-sidebar').on('click', function(e) {
                e.preventDefault();
                $('body').toggleClass('side-content-visible');
            });
            //Hide Form
            $('.hidden-bar .inner-box .cross-icon,.form-back-drop,.close-menu').on('click', function(e) {
                e.preventDefault();
                $('body').removeClass('side-content-visible');
            });
            //Dropdown Menu
            $('.fullscreen-menu .navigation li.dropdown > a').on('click', function() {
                $(this).next('ul').slideToggle(500);
            });
        }
         
        
        // 05. Search Box
		$('.nav-search > button').on('click', function () {
			$('.nav-search form').toggleClass('hide');
		});
        
        
        // Hide Box Search WHEN CLICK OUTSIDE
		if ($(window).width() > 767){
			$('body').on('click', function (event) {
				if ($('.nav-search > button').has(event.target).length == 0 && !$('.nav-search > button').is(event.target)
					&& $('.nav-search form').has(event.target).length == 0 && !$('.nav-search form').is(event.target)) {
					if ($('.nav-search form').hasClass('hide') == false) {
						$('.nav-search form').toggleClass('hide');
					};
				}
			});
		}
        
        
        // 06. Product Gallery Popup
        $('.product-preview-images a').magnificPopup({
            type:'image',
            gallery: {
                enabled: true,
                navigateByImgClick: true,
            },
        });
        
           
        
        // 07. Video Popup
        if ($('.video-play').length) {
            $('.video-play').magnificPopup({
                type: 'video',
            });
        } 
         
        
        /* 08. Main Slider */
        if ($('.main-slider-active').length) {
            $('.main-slider-active').slick({
                infinite: true,
                arrows: true,
                dots: false,
                fade: true,
                autoplay: false,
                autoplaySpeed: 5000,
                pauseOnHover: false,
                slidesToScroll: 1,
                slidesToShow: 1,
                prevArrow: '<button class="slider-prev"><i class="fas fa-chevron-left"></i></button>',
                nextArrow: '<button class="slider-next"><i class="fas fa-chevron-right"></i></button>',
            });
        }
        
        
        /* 09. Slider Two */
        if ($('.slider-two-active').length) {
            $('.slider-two-active').slick({
                infinite: true,
                arrows: true,
                dots: false,
                fade: true,
                autoplay: false,
                autoplaySpeed: 5000,
                pauseOnHover: false,
                slidesToScroll: 1,
                slidesToShow: 1,
                prevArrow: '<button class="slider-prev"><i class="fas fa-chevron-left"></i></button>',
                nextArrow: '<button class="slider-next"><i class="fas fa-chevron-right"></i></button>',
            });
        }
        
        
        // 10. Product Slider
        if ($('.product-active').length) {
            $('.product-active').slick({
                dots: true,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 2000,
                arrows: false,
                speed: 1000,
                focusOnSelect: true,
                slidesToShow: 6,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 1500,
                        settings: {
                            slidesToShow: 5,
                        }
                    },
                    {
                        breakpoint: 1300,
                        settings: {
                            slidesToShow: 4,
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: 3,
                        }
                    },
                    {
                        breakpoint: 768,
                        settings: {
                            slidesToShow: 2,
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1,
                        }
                    }
                ]
            });
        } 
        
        
        // 11. Product Slider Two
        if ($('.product-active-two').length) {
            $('.product-active-two').slick({
                dots: true,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 2000,
                arrows: false,
                speed: 1000,
                focusOnSelect: true,
                slidesToShow: 4,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 1200,
                        settings: {
                            slidesToShow: 3,
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: 2,
                        }
                    },
                    {
                        breakpoint: 575,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1,
                        }
                    }
                ]
            });
        } 
        
        
        
        // 12. Team Member
        if ($('.team-active').length) {
            $('.team-active').slick({
                dots: false,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 2000,
                arrows: true,
                speed: 1000,
                prevArrow: $('.team-prev'),
                nextArrow: $('.team-next'),
                focusOnSelect: false,
                slidesToShow: 4,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 1200,
                        settings: {
                            slidesToShow: 3,
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: 2,
                        }
                    },
                    {
                        breakpoint: 575,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1,
                        }
                    }
                ]
            });
        } 
        

        
        // 13. Two Row Team
        if ($('.two-row-team-active').length) {
            $('.two-row-team-active').slick({
                dots: false,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 2000,
                arrows: true,
                speed: 1000,
                rows: 2,
                prevArrow: $('.team-prev'),
                nextArrow: $('.team-next'),
                focusOnSelect: false,
                slidesToShow: 4,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 1200,
                        settings: {
                            slidesToShow: 3,
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: 2,
                        }
                    },
                    {
                        breakpoint: 575,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1,
                        }
                    }
                ]
            });
        } 
        

        // 14. Category Slider
        if ($('.category-active').length) {
            $('.category-active').slick({
                dots: false,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 2000,
                arrows: true,
                speed: 1000,
                prevArrow: '<button class="slider-prev"><i class="fas fa-chevron-left"></i></button>',
                nextArrow: '<button class="slider-next"><i class="fas fa-chevron-right"></i></button>',
                focusOnSelect: true,
                slidesToShow: 6,
                slidesToScroll: 2,
                responsive: [
                    {
                        breakpoint: 1500,
                        settings: {
                            slidesToShow: 5,
                        }
                    },
                    {
                        breakpoint: 1300,
                        settings: {
                            slidesToShow: 4,
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: 3,
                        }
                    },
                    {
                        breakpoint: 768,
                        settings: {
                            slidesToShow: 2,
                        }
                    },
                    {
                        breakpoint: 480,
                        settings: {
                            slidesToShow: 1,
                            slidesToScroll: 1,
                        }
                    }
                ]
            });
        } 
        
        
        
        // 15. Gllery Slider  
        if ($('.gallery-active').length) {
            $('.gallery-active').slick({
                dots: false,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 5000,
                arrows: true,
                speed: 1000,
                slidesToShow: 1,
                slidesToScroll: 1,
                variableWidth: true,
                prevArrow: $('.gallery-prev'),
                nextArrow: $('.gallery-next'),
            });
        }  
        
        
        
        // 16. Gllery Slider Two
        if ($('.gallery-two-active').length) {
            $('.gallery-two-active').slick({
                dots: false,
                infinite: true,
                autoplay: false,
                autoplaySpeed: 5000,
                arrows: true,
                speed: 1000,
                rows: 2,
                slidesToShow: 1,
                slidesToScroll: 1,
                variableWidth: true,
                prevArrow: $('.gallery-two-prev'),
                nextArrow: $('.gallery-two-next'),
            });
        }  
        
        
        // 17. Feedback Slider  
        if ($('.feedback-active').length) {
            var $slider = $('.feedback-active');
            var $progressBar = $('.progress');
            var $progressBarLabel = $('.slider__label');
            
            $slider.on('beforeChange', function (event, slick, currentSlide, nextSlide) {
                var calc = ((nextSlide) / (slick.slideCount - 1)) * 100;
                
                $progressBar
                    .css('background-size', calc + '% 100%')
                    .attr('aria-valuenow', calc);
                
                $progressBarLabel.text(calc + '% completed');
            });
            
            $slider.slick({
                slidesToShow: 1,
                slidesToScroll: 1,
                speed: 400,
                arrows: false,
                dots: true,
            });
        }
        
        
        // 18. Feedback Slider Two
        if ($('.feedback-two-active').length) {
            $('.feedback-two-active').slick({
                slidesToScroll: 1,
                infinite: true,
                speed: 400,
                centerMode: true,
                arrows: false,
                variableWidth: true,
                dots: true,
                responsive: [
                    {
                        breakpoint: 767,
                        settings: {
                            slidesToShow: 1,
                            centerMode: false,
                            variableWidth: false,
                        }
                    }
                ]
            });
        } 
        
        
        // 19. News Slider
        if ($('.news-slider').length) {
            $('.news-slider').slick({
                slidesToShow: 2,
                slidesToScroll: 1,
                infinite: true,
                speed: 400,
                arrows: false,
                dots: true,
                responsive: [
                    {
                        breakpoint: 767,
                        settings: {
                            slidesToShow: 1,
                            centerMode: false,
                            variableWidth: false,
                        }
                    }
                ]
            });
        } 
        

        // 20. Client Logo
        if ($('.client-logo-wrap').length) {
            $('.client-logo-wrap').slick({
                dots: false,
                infinite: true,
                autoplay: true,
                autoplaySpeed: 2000,
                arrows: false,
                speed: 1000,
                slidesToShow: 6,
                slidesToScroll: 1,
                responsive: [
                    {
                        breakpoint: 1200,
                        settings: {
                            slidesToShow: 5,
                        }
                    },
                    {
                        breakpoint: 992,
                        settings: {
                            slidesToShow: 4,
                        }
                    },
                    {
                        breakpoint: 767,
                        settings: {
                            slidesToShow: 3,
                        }
                    },
                    {
                        breakpoint: 575,
                        settings: {
                            slidesToShow: 2,
                        }
                    }
                ]
            });
        } 
        
        
         /* 21. Fact Counter + Text Count - Our Success */
        if ($('.counter-item').length) {
            $('.counter-item').appear(function () {

                var $t = $(this),
                    n = $t.find(".count-text").attr("data-stop"),
                    r = parseInt($t.find(".count-text").attr("data-speed"), 10);

                if (!$t.hasClass("counted")) {
                    $t.addClass("counted");
                    $({
                        countNum: $t.find(".count-text").text()
                    }).animate({
                        countNum: n
                    }, {
                        duration: r,
                        easing: "linear",
                        step: function () {
                            $t.find(".count-text").text(Math.floor(this.countNum));
                        },
                        complete: function () {
                            $t.find(".count-text").text(this.countNum);
                        }
                    });
                }

            }, {
                accY: 0
            });
        }
        
        
         /* 22. Team skill Counter */
		if ($.fn.circleProgress) {
			var progress1 = $('.one.progress-content')
			if($.fn.circleProgress) {
			  progress1.appear(function () {
				progress1.circleProgress({
					value: 0.76,
					size: 140,
                    thickness: 7,
					fill: "#76a713",
                    lineCap: 'square',
                    startAngle: -Math.PI / 4 * 2,
					animation : { duration: 2000},
				  }).on('circle-animation-progress', function(event, progress) {
					$(this).find('h2').html(Math.round(76 * progress) + '<span>%</span>');
				  });
			  });
			};
		};
		if ($.fn.circleProgress) {
			var progress2 = $('.two.progress-content')
			if($.fn.circleProgress) {
			  progress2.appear(function () {
				progress2.circleProgress({
					value: 0.83,
					size: 140,
                    thickness: 7,
					fill: "#ff7800",
                    lineCap: 'square',
                    startAngle: -Math.PI / 4 * 2,
					animation : { duration: 2000},
				  }).on('circle-animation-progress', function(event, progress) {
					$(this).find('h2').html(Math.round(83 * progress) + '<span>%</span>');
				  });
			  });
			};
		};
        
        
        // 23. Portfolio Filtering
        $(".portfolio-filter li").on('click', function () {
            $(".portfolio-filter li").removeClass("current");
            $(this).addClass("current");

            var selector = $(this).attr('data-filter');
            $('.portfolio-active').imagesLoaded(function () {
                $(".portfolio-active").isotope({
                    itemSelector: '.item',
                    filter: selector,
                });
            });

        });
        

        
        // 24. Scroll to Top
        if ($('.scroll-to-target').length) {
            $(".scroll-to-target").on('click', function () {
                var target = $(this).attr('data-target');
                // animate
                $('html, body').animate({
                    scrollTop: $(target).offset().top
                }, 1000);

            });
        }
        
        
        /* 25. CountDown Start */
		if($('.count-down').length !== 0){
            var $date = $('.count-down').attr('data-date');
                const second = 1000,
				  minute = second * 60,
				  hour = minute * 60,
				  day = hour * 24;
				let	countDown = new Date($date).getTime(),
			x = setInterval(function() {
			  let now = new Date().getTime(),
				  distance = countDown - now;
				document.getElementById('days').innerText = Math.floor(distance / (day)),
				document.getElementById('hours').innerText = Math.floor((distance % (day)) / (hour)),
				document.getElementById('minutes').innerText = Math.floor((distance % (hour)) / (minute)),
				document.getElementById('seconds').innerText = Math.floor((distance % (minute)) / second);
			  //do something later when date is reached
			  //if (distance < 0) {
			  //  clearInterval(x);
			  //  'IT'S MY BIRTHDAY!;
			  //}
			}, second)
        };
        
        
        // 26. Nice Select
        $('select').niceSelect();
        
        
        // 27. WOW Animation
        if ($('.wow').length) {
            var wow = new WOW({
                boxClass: 'wow', // animated element css class (default is wow)
                animateClass: 'animated', // animation css class (default is animated)
                offset: 0, // distance to the element when triggering the animation (default is 0)
                mobile: false, // trigger animations on mobile devices (default is true)
                live: true // act on asynchronously loaded content (default is true)
            });
            wow.init();
        }
        
        
        // 28. Quantity Number js
        $('.quantity-down').on('click', function(){
            var numProduct = Number($(this).next().val());
            if(numProduct > 1) $(this).next().val(numProduct - 1);
        });
        $('.quantity-up').on('click', function(){
            var numProduct = Number($(this).prev().val());
            $(this).prev().val(numProduct + 1);
        });


        // 29. Price Totaling Function
        function priceTotaling() {
            var quantity = $(this).parent().find('.quantity').val();
            var price = $(this).parent().parent().find('.product-price').text();
            $(this).parent().parent().find('.product-total-price').text(quantity*price);

            var subTotal = 0;

            $('.product-total-price').each(function(){
                var singleVal = $(this).text();
                if($.isNumeric(singleVal)){
                    subTotal += parseFloat(singleVal);
                }
            });

            $('.sub-total-price').text(subTotal);
            var shipping = $('.shipping-price').text();
            $('.total-price').text((+subTotal) + (+shipping));
        }

        //  Cart Single Item box removed with Animation and Price Totaling
        $(".cart-single-item .close").on('click', function(){
            $(this).parent().fadeOut(500, function(){
                $(this).remove();
                priceTotaling();
            });
        });

        //  Price Totaling when product quantity increment or decrement
        $(".quantity-input button").on('click', priceTotaling);

        //  Price Totaling when input in product quantity number in input field
        $(".quantity-input").on('input', '.quantity', priceTotaling);
 
    });
    
    
    /* ==========================================================================
       When document is resize, do
       ========================================================================== */

    $(window).on('resize', function () {
        var mobileWidth = 992;
        var navcollapse = $('.navigation li.dropdown');
        navcollapse.children('ul').hide();
        navcollapse.children('.megamenu').hide();

    });


    /* ==========================================================================
       When document is scroll, do
       ========================================================================== */

    $(window).on('scroll', function () {

        // Header Style and Scroll to Top
        function headerStyle() {
            if ($('.main-header').length) {
                var windowpos = $(window).scrollTop();
                var siteHeader = $('.main-header');
                var scrollLink = $('.scroll-top');
                if (windowpos >= 100) {
                    siteHeader.addClass('fixed-header');
                    scrollLink.fadeIn(300);
                } else {
                    siteHeader.removeClass('fixed-header');
                    scrollLink.fadeOut(300);
                }
            }
        }

        headerStyle();

    });

    /* ==========================================================================
       When document is loaded, do
       ========================================================================== */

    $(window).on('load', function () {

        // 30. Preloader
        function handlePreloader() {
            if ($('.preloader').length) {
                $('.preloader').delay(200).fadeOut(500);
            }
        }
        handlePreloader();
        
        
        // 23. Portfolio Filtering
       if ($('.portfolio-active').length) {
            $(".portfolio-active").isotope({
                itemSelector: '.item',
            });
        };
          
        
    });

})(window.jQuery);
