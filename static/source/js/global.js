// static/js/global.js

document.addEventListener("DOMContentLoaded", function () {
  // ---- Helper to imitate link from ".credit" blocks ----
  function imitateLink(element) {
    if (!element) return;
    var url = element.getAttribute("rel");
    if (url) {
      window.location.href = url;
    }
  }

  // Click on ".event .credit"
  document.querySelectorAll(".event .credit").forEach(function (el) {
    el.addEventListener("click", function (e) {
      e.preventDefault();
      imitateLink(el);
    });
  });

  // Click on ".event .credit span"
  document.querySelectorAll(".event .credit span").forEach(function (span) {
    span.addEventListener("click", function (e) {
      e.preventDefault();
      var credit = span.closest(".credit");
      imitateLink(credit);
    });
  });

  // ---- "Show all upcoming events" ----
  var showMoreLinks = document.querySelectorAll(".show-more a");
  showMoreLinks.forEach(function (link) {
    link.addEventListener("click", function (e) {
      e.preventDefault();

      var container = document.querySelector(".upcoming-events .row-container");
      if (container) {
        container.style.maxHeight = "none";
        container.style.overflow = "visible";
      }

      var showMore = document.querySelector(".show-more");
      if (showMore) {
        showMore.style.display = "none";
      }
    });
  });
});














/*
$(document).ready(function() {

    $('.gallery').sss({
        showNav: false
    });

    function imitate_link(element) {
        var url = $(element).attr('rel');
        if (url != undefined) window.location = url;
    }

    $('.event .credit').click(function() {
        imitate_link(this);
        return false;
    });

    $('.event .credit span').click(function() {
        imitate_link(this);
        return false;
    });

    $('.show-more a').click(function(){
        $('.upcoming-events .row-container').css('max-height', '100%');
        $('.upcoming-events .row-container').css('overflow', 'visible');
        $('.show-more').css('display', 'none');
    });
});
*/