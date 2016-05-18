$(function () {
  var $credentialsForm = $('#credentialsUpload');
  $credentialsForm.on('submit', function (event) {
    event.preventDefault();

    var $submit = $credentialsForm.find('button[type="submit"]');
    $submit.prop('disabled', true);
    $submit.html('Uploading...');

    function resetButton() {
      $submit.removeProp('disabled');
      $submit.html('Upload');
    }

    var $credentials = $('#credentials');
    var credentials = $credentials.val();
    if (credentials.trim() === '') return resetButton();

    var data = { 'credentials':  credentials };
    $.ajax({
      type: 'POST',
      url: '/admin/network',
      data: data,
      complete: resetButton
    }).then(function(data, status, jqXHR) {
      alert("All credentials have been uploaded successfully. Please allow up to 30 seconds for" +
              "the related entities to propogate.");
      $credentials.val('');
    }, function(jqXHR, status, errorThrown) {
      var response = jqXHR.responseJSON;
      var error = response.errors[0];
      if (error.type === 'InvalidParameterError') {
        alert(error.message);
      } else {
        alert("A back-end error has occurred.");
      }
    });
  });
});
