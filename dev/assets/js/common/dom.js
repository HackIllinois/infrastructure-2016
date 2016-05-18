$(function () {
  $('#logout').on('click', function() {
    $.ajax({
      type: 'GET',
      url: '/logout'
    });

    deleteCookie('auth');
    window.location.href = '/';
  });
});
