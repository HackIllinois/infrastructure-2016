$(function () {
  var parsleyOptions = {
    excluded: "input[type=button], input[type=submit], input[type=reset], input[type=hidden], :hidden"
  };

  window.ParsleyValidator.addValidator('present',
    function(value, requirement) {
      return value.strip() !== "";
    }, 1).addMessage('en', 'present', 'Please select a value');

  $statusChange = $('#status-change');
  $statusChange.parsley(parsleyOptions);

  $('input[name="status"]').on('change', function (event) {
    $initiativeSelect = $('#initiative-select');
    if (event.target.value == 'ACCEPTED') {
      $initiativeSelect.removeClass('hidden');
    } else {
      $initiativeSelect.addClass('hidden');
    }
  });

  $statusChange.on('submit', function (event) {
      event.preventDefault();

      var isValid = $statusChange.parsley().validate();
      if (!isValid) return;

      var statusValue = $('input[name="status"]:checked').val();
      var initiativeValue = (statusValue === 'ACCEPTED') ?
        $('input[name="initiative"]:checked').val() : undefined;
      var waveValue = $('#wave').val();
      var data = { 'status': statusValue, 'initiative': initiativeValue, 'wave': waveValue };
      var $submit = $('#status-submit');

      $submit.attr('disabled', true);
      $submit.html('Saving...');
      $.ajax({
        url: window.location.pathname,
        method: 'PUT',
        data: data,
        complete: function (jqXHR, textStatus) {
          $submit.attr('disabled', false);
          $submit.html('Save Changes');
        }
      }).then(function (result, textStatus, jqXHR) {
        window.location.reload();
      }, function (jqXHR, textStatus, errorThrown) {
        alert("A back-end error occurred. Please try again.");
      });
  });
});
