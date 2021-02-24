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

  //
  // var $company = $('.forCompanies');
  // $win.scroll(function() {
  //   if ($win.width() > 500) {
  //     if ($(this).scrollTop() > 150) {
  //       $company.fadeIn();
  //     } else {
  //       $company.fadeOut();
  //     }
  //   } else {
  //     if ($(this).scrollTop() > 200) {
  //       $company.fadeIn();
  //     } else {
  //       $company.fadeOut();
  //     }
  //   }
  // });

  //
  var $pastdata = $('.pastCooperations');
  $win.scroll(function() {
    if ($win.width() > 500) {
      if ($(this).scrollTop() > 400) {
        $pastdata.fadeIn();
      } else {
        $pastdata.fadeOut();
      }
    } else {
      if ($(this).scrollTop() > 200) {
        $pastdata.fadeIn();
      } else {
        $pastdata.fadeOut();
      }
    }
  });



});
