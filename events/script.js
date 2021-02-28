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

  // ミッションを一定スクロールで表示
  var $mis = $('.mission');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 0) {
        $mis.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 100) {
        $mis.fadeIn();
      }
    }
  });

  var $band = $('.band-image img');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 250) {
        $band.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 540) {
        $band.fadeIn();
      }
    }
  });

  // メッセージを一定スクロールで表示
  var $mes = $('.messages');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 500) {
        $mes.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 700) {
        $mes.fadeIn();
      }
    }
  });


  var $vmtg = $('.visit-mtg');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 1000) {
        $vmtg.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 1300) {
        $vmtg.fadeIn();
      }
    }
  });


});
