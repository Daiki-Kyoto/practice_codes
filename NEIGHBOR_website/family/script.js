$(function() {
  // ヘッダーのナビゲーションを一定スクロールで表示
  var hList = $('.h-list');
  var $win = $(window)
  $win.scroll(function() {
    if ($(this).scrollTop() > 340 && $(window).width() > 500) {
      hList.fadeIn();
    } else {
      hList.fadeOut();
    }
  });

  $('.toTopPage').click(function(){
    $('html, body').animate({
      'scrollTop':0
    }, 500);
  });

  $win.scroll(function() {
    if($(this).scrollTop() > 0) {
      $('.toTopPage').fadeIn();
    } else {
      $('.toTopPage').fadeOut();
    }
  });

  $win.scroll(function() {
    if($(this).scrollTop() > 340) {
      $('.sidebanner').addClass('is-fixed');
    } else {
      $('.sidebanner').removeClass('is-fixed');
    }
  });


});
