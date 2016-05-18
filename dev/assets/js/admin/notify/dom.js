$(function () {
  var parsleyOptions = {
    excluded: "input[type=button], input[type=submit], input[type=reset], input[type=hidden], :hidden"
  };

  $form = $('#send-wave');
  $wave = $('#wave');
  $submit = $('#submit');

  $form.parsley(parsleyOptions);
  $form.on('submit', function (event) {
    event.preventDefault();

    var isValid = $form.parsley().validate();
    if (!isValid) return;

    $submit.prop('disabled', true);
    $.ajax({
      type: 'POST',
      url: '/admin/notify/' + $wave.val(),
      complete: function () {
        $submit.removeProp('disabled');
      }
    }).then(function(data, status, jqXHR){
      alert('The notifications for this wave have been queued. Note that the entire process may take up to five minutes to finish, at which point this wave will be disabled for future use.');
      window.location.reload();
    }, function(jqXHR, status, errorThrown){
        alert("An error occurred. Please try again and check your console for errors.");
    });
  });
});
