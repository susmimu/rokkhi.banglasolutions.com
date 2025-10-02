
//--------------------------------------------------------------------------------
// When the user scrolls down 80px from the top of the document, resize the navbar's padding and the logo's font size
window.onscroll = function() {scrollFunction()};

function scrollFunction()
{
  if (document.body.scrollTop > 10 || document.documentElement.scrollTop > 10)
  {
    document.getElementById("navbar").style.height = "80px";

    document.getElementById("logo").style.width = "150px";
    document.getElementById("logo").style.height = "49px";
  }
  else
  {
    document.getElementById("navbar").style.height = "110px";

    document.getElementById("logo").style.width = "230px";
    document.getElementById("logo").style.height = "79px";
  }
}
//--------------------------------------------------------------------------------

//--------------------------------------------------------------------------------
function floating_bar_func()
{
  var x = document.getElementById("user_button");

  if (x.className.indexOf("w3-show") == -1)
  {
    x.className += " w3-show";
  }
  else
  {
    x.className = x.className.replace(" w3-show", "");
  }
}
//--------------------------------------------------------------------------------




$(document).ready(function() {
  $('.nav-button').click(function() {
    $('.nav-button').toggleClass('change');
  });

  $(window).scroll(function() {
    let position = $(this).scrollTop();
    if(position >= 200) {
      $('.nav-menu').addClass('custom-navbar');
    } else {
      $('.nav-menu').removeClass('custom-navbar');
    }
  });

  $(window).scroll(function() {
    let position = $(this).scrollTop();
    if(position >= 650) {
      $('.camera-img').addClass('fromLeft');
      $('.mission-text').addClass('fromRight');
    } else {
      $('.camera-img').removeClass('fromLeft');
      $('.mission-text').removeClass('fromRight');
    }
  });

  $('.gallery-list-item').click(function() {
    let value = $(this).attr('data-filter');
    if(value === 'all') {
      $('.filter').show(300);
    } else {
      $('.filter').not('.' + value).hide(300);
      $('.filter').filter('.' + value).show(300);
    }
  });

  $('.gallery-list-item').click(function() {
    $(this).addClass('active-item').siblings().removeClass('active-item');
  });

  $(window).scroll(function() {
    let position = $(this).scrollTop();
    if(position >= 4300) {
      $('.card-1').addClass('moveFromLeft');
      $('.card-2').addClass('moveFromBottom');
      $('.card-3').addClass('moveFromRight');
    } else {
      $('.card-1').removeClass('moveFromLeft');
      $('.card-2').removeClass('moveFromBottom');
      $('.card-3').removeClass('moveFromRight');
    }
  });

  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  });


});



function helpAlert()
{
  alert("Info! Contact with administrator for help!");
}