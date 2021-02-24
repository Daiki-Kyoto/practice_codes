$(function() {
  // ヘッダーのナビゲーションを一定スクロールで表示
  var hList = $('.h-list');

  $(window).scroll(function() {
    if ($(this).scrollTop() > 340 && $(window).width() > 500) {
      hList.fadeIn();
    } else {
      hList.fadeOut();
    }
  });


});
