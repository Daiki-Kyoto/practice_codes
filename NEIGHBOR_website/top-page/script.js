$(function() {
  // ヘッダーのナビゲーションを一定スクロールで表示
  var hList = $('.h-list');
  var $win = $(window)
  $win.scroll(function() {
    if ($(this).scrollTop() > 640 && $win.width() > 500) {
      hList.fadeIn();
    } else {
      hList.fadeOut();
    }
  });

  // ミッションを一定スクロールで表示
  var $mis = $('.mission');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 400) {
        $mis.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 200) {
        $mis.fadeIn();
      }
    }
  });

  var $band = $('.band-image img');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 600) {
        $band.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 200) {
        $band.fadeIn();
      }
    }
  });

  // メッセージを一定スクロールで表示
  var $mes = $('.messages');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 1200) {
        $mes.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 300) {
        $mes.fadeIn();
      }
    }
  });


  var $vmtg = $('.visit-mtg');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 2100) {
        $vmtg.fadeIn();
      }
    } else {
      if ($(this).scrollTop() > 500) {
        $vmtg.fadeIn();
      }
    }
  });


});
