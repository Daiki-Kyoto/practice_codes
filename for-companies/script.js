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


  var $pastdata = $('.pastCooperations');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 50) {
        $pastdata.fadeIn();
      } else {
        $pastdata.fadeOut();
      }
    } else {
      if ($(this).scrollTop() > 60) {
        $pastdata.fadeIn();
      } else {
        $pastdata.fadeOut();
      }
    }
  });



});
