jQuery(document).ready(function($){
    var mobileTabs = $('.mobile-nav');
    var desktopTabs = $('.binder-tabs');

    desktopTabs.each(function(){
        var tab = $(this),
            tabContentWrapper = $('.binder-paper .pages'),
            tabItems = tab.find('li');

        tabItems.on('click', 'a', function(event){
            event.preventDefault();
            var selectedItem = $(this);
            if( !selectedItem.find('a').hasClass('tab-active') ) {
                
                var selectedTab = selectedItem.parent().data('content'),
                    selectedContent = tabContentWrapper.find('.page-content[data-content="'+selectedTab+'"]'),
                    selectedContentHeight = selectedContent.innerHeight();
                    
                
                tabItems.find('a.tab-active').removeClass('tab-active');
                selectedItem.addClass('tab-active');
                $('.page-content').removeClass('content-visible');
                selectedContent.addClass('content-visible')
                
                //animate tabContentWrapper height when content changes 
                //tabContentWrapper.animate({
                //   'height': selectedContentHeight
                //}, 200);
            }
        });
    });

    mobileTabs.each(function(){
        var tab = $(this),
            tabContentWrapper = tab.find('.binder-paper .pages'),
            tabItems = tab.find('.tab'),
            tabNavigation = tab.find('nav');

        tabItems.on('click', function(event){
            event.preventDefault();
            var selectedItem = $(this);
            if( !selectedItem.hasClass('.tab-active') ) {
                
                var selectedTab = selectedItem.data('content'),
                    selectedContent = $('.page-content[data-content="'+selectedTab+'"]'),
                    selectedContentHeight = selectedContent.innerHeight();
                
                tabItems.removeClass('tab-active');
                selectedItem.addClass('tab-active');
                selectedContent.addClass('content-visible');
                //.siblings('.page-content').removeClass('content-visible');
                
                //animate tabContentWrapper height when content changes 
                tabContentWrapper.animate({
                  'height': selectedContentHeight
                }, 200);
            }
        });

        //hide the .cd-mobileTabs::after element when tabbed navigation has scrolled to the end (mobile version)
        checkScrolling(tabNavigation);
        tabNavigation.on('scroll', function(){ 
            checkScrolling($(this));
        });
    });

    $('.pagination-link').on('click', function(event){
        event.preventDefault();

        var mobileTabs = $('.mobile-nav .binder-tabs li'),
            tabs = $('.binder-content .binder-tabs li a');

        var clickedPaginationLink = $(this),
            pageToLoad = clickedPaginationLink.data('content'),
            mobileTabToHighlight = $('.mobile-nav .binder-tabs li[data-content="'+pageToLoad+'"]'),
            tabToHighlight = $('.binder-content .binder-tabs li[data-content="'+pageToLoad+'"] a'),
            contentToLoad = $('.page-content[data-content="'+pageToLoad+'"]'),
            contentHeight = contentToLoad.innerHeight();


            mobileTabs.removeClass('tab-active');
            tabs.removeClass('tab-active');

            mobileTabToHighlight.addClass('tab-active');
            tabToHighlight.addClass('tab-active');

            //content divs
            $('.page-content').removeClass('content-visible');
            contentToLoad.addClass('content-visible');

    });
    
    $(window).on('resize', function(){
        mobileTabs.each(function(){
            var tab = $(this);
            checkScrolling(tab.find('nav'));
            tab.find('.cd-mobileTabs-content').css('height', 'auto');
        });
    });

    function checkScrolling(mobileTabs){
        var totalTabWidth = parseInt(mobileTabs.find('ul.binder-mobileTabs').width()),
            mobileTabsViewport = parseInt(mobileTabs.width());

        if( mobileTabs.scrollLeft() === 0) {
            mobileTabs.parent().addClass('is-begun');
        } else {
            mobileTabs.parent().removeClass('is-begun');
        }
            
        if( mobileTabs.scrollLeft() >= totalTabWidth - mobileTabsViewport) {
            mobileTabs.parent().addClass('is-ended');
        } else {
            mobileTabs.parent().removeClass('is-ended');
        }
    }

    // better scroll performance
    var body = document.body,
        timer;

    window.addEventListener('scroll', function() {
      clearTimeout(timer);
      if(!body.classList.contains('disable-pointer-events')) {
        body.classList.add('disable-pointer-events')
      }
      
      timer = setTimeout(function(){
        body.classList.remove('disable-pointer-events')
      },500);
    }, false);


});