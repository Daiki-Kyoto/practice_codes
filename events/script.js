$(function() {

  $(window).scroll(function() {
    document.getElementById('count').innerText = $(this).scrollTop();
  });

  $('.menu-icon').click(function() {
    $('#sidemenu').toggle();
  });


  // ヘッダーのナビゲーションを一定スクロールで表示
  var $win = $(window)

  var menubar = $('#menubar');
  $win.scroll(function() {
    if ($(this).scrollTop() > 200 && $win.width() > 600) {
      menubar.fadeIn();
    } else {
      menubar.fadeOut();
    }
  });

  var bars = $('#bars')
  $win.scroll(function() {
    if ($(this).scrollTop() > 200 && $win.width() <= 600) {
      bars.fadeIn();
    } else {
      bars.fadeOut();
    }
  });




});
