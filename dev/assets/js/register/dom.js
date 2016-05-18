var weights = {
  'general': 1,
  'personal': 2,
  'professional': 3,
  'hackathonA': 4,
  'hackathonB': 5
};

var $animator;
var $schoolSelectize, $majorSelectize, $graduationSelectize;

var initialSection = 'general';
var finalSection = 'hackathonB';
var maxFileSize = 2 * 1000000;

var nextEnabled = false;
var backEnabled = false;

var backCallback;
var nextCallback;

backCallback = function (event, animate) {
  if (animate) {
    if ($animator.hasClass('animating')) return;
    $animator.addClass('animating');

    _deactivateForm(undefined, _backCallback);
    $animator.slideDown('slow', 'easeInOutBack', function () { $animator.removeClass('animating'); });
  } else {
    var deactivatedForm = _deactivateForm();
    _backCallback(deactivatedForm);
  }
  return true;
};

nextCallback = function (event, animate) {
  if (animate) {
    if ($animator.hasClass('animating')) return;
    $animator.addClass('animating');

    _validateAndDeactivateForm(_nextCallback);
    $animator.slideDown('slow', 'easeInOutBack', function () { $animator.removeClass('animating'); });
  } else {
    var deactivatedForm = _validateAndDeactivateForm();
    _nextCallback(deactivatedForm);
  }
  return true;
};

function initialize(activeForm) {
  var section = _determineSection(activeForm);
  _handleNavs(section);
  _handleHeaders(section);
  _handleProgress(section);
}

$(document).ready(function() {
  $animator = $('#animator');

  window.ParsleyValidator.addValidator('join',
    function(value, requirement) {
      var valid = true;
      var parsleyGroup = $("[data-parsley-group=" + requirement + "]");
      parsleyGroup.each(function(index) {
        if ($(this).val().trim() === '') {
          valid = false;
        }
      });
      parsleyGroup.each(function(index) {
        if (valid) $(this).removeClass("error");
        else $(this).addClass("error");
      });
      return valid;
    }, 999).addMessage('en', 'join', 'These values are required.');

  window.ParsleyValidator.addValidator('phone',
    function(value, requirement) {
      value = value.replace(/\D/g,'');

      var valid = /^\d{10}$/.test(value);
      if (valid) {
        $(requirement).val(value);
      }

      return valid;
    }, 1).addMessage('en', 'phone', 'Please provide a valid US 10-digit number');

  $(document).on('keydown', function (event) {
      $focus = $(':focus');
      if ($focus.length) {
        // we won't try to move to the next page if the user selecting a radio button
        // or if the user is inside of an input (not a selectize input)
        if ($focus.is(':radio')) return;
        if ($focus.is('input') && $focus.parent().attr('class').indexOf('selectize') < 0) return;
      }

      if (event.keyCode == 39 && nextEnabled) {
        nextCallback(event, true);
      } else if (event.keyCode == 37 && backEnabled) {
        backCallback(event, true);
      }
  });
  $(ids.globals.navBackMobile + ', ' + ids.globals.navBack).on('click', function (event) { backCallback(event, true); });
  $(ids.globals.navNextMobile + ', ' + ids.globals.navNext).on('click', function (event) { nextCallback(event, true); });

  // provides multiple validation functionality
  $(ids.fields.firstName).on('keyup', function(event) {
    _validateActiveForm(true);
  });
  $(ids.fields.graduationYear).on('keyup', function (event) {
    _validateActiveForm(true);
  });
  $(ids.fields.gender).on('change', function (event) {
    _validateActiveForm(true);
  });

  $(ids.misc.resumeUpload + ", " + ids.misc.resumeChange).on('click', function(event) {
    event.preventDefault();
    $(ids.fields.resume).click();
  });

  $(ids.fields.resume).on('change', function(event) {
    var file = this.files[0];
    if (file && file.size > maxFileSize) {
      alert("Please choose a smaller file (max file size 2MB).");
      event.target.value = "";
      file = undefined;
    }
    if (file && file.type !== 'application/pdf') {
      // this won't happen unless someone edits the source
      alert("Resumes must be in PDF format.");
      event.target.value = "";
      file = undefined;
    }

    var resumeSubsection = $(ids.subsections.resume);

    if (!file) {
      resumeSubsection.removeClass('uploaded');
      return;
    }

    resumeSubsection.addClass('uploaded');
    $(ids.misc.resumeFilename).val(file.name).change();
  });

  $("[name='initiatives[]']").on('change', function (event) {
    if (event.target.value === 'HARDWARE') {
      var $hardwareFollowup = $('#hackathon-hardware-followup, #hackathon-hardware-followup-caption');
      if (event.target.checked) {
        $hardwareFollowup.removeClass('hidden');
      } else {
        $hardwareFollowup.addClass('hidden');
      }
    } else if (event.target.value === 'OPEN_SOURCE') {
      var $openSourceFollowup = $('#hackathon-open-source-followup, #hackathon-open-source-followup-caption');
      if (event.target.checked) {
        $openSourceFollowup.removeClass('hidden');
      } else {
        $openSourceFollowup.addClass('hidden');
      }
    }
  });

  $(ids.misc.finalizeClosed).on('click', function(event) {
    event.preventDefault();
    alert("Sorry, but no more changes can be made at this time. Thanks for your interest in HackIllinois 2016! We hope to see you there.");
  });

  $(ids.misc.finalize).on('click', function(event) {
    event.preventDefault();

    var valid = _validateActiveForm();
    if (!valid.result) return;

    var $this = $(this);
    function disableButton() {
      $this.prop('disabled', true);
      if ($this.hasClass('update')) {
        $this.html('Updating...');
      } else {
        $this.html('Submitting...');
      }
    }
    function enableButton() {
      $this.removeProp('disabled');
      if ($this.hasClass('update')) {
        $this.html('Save Changes');
      } else {
        $this.html('Submit');
      }
    }

    disableButton();
    var submission = new FormData();

    $('form input').each(function() {
      if (this.name && this.name.indexOf("[]") < 0) {
        if ((this.type === 'text' && this.value.trim()) || this.type === 'hidden') {
          submission.append(this.name, this.value);
        }
        else if (this.type === 'radio' && this.checked) {
          submission.append(this.name, $(this).val());
        }
        else if (this.type === 'file' && this.files.length) {
          var resume = this.files[0];
          if (resume) {
            submission.append('resume_filename', resume.name);
            submission.append('resume', resume);
          }
        }
      }
    });

    var initiatives = [];
    $('input[name="initiatives[]"]:checked').each(function () {
      initiatives.push(this.value);
    });
    submission.append('initiatives', initiatives.join());

    $.ajax({
      type: 'POST',
      url: '/register',
      data: submission,
      contentType: false,
      processData: false
    }).then(function (data, status, jqXHR) {
      if ($this.hasClass('update')) {
        // we simply reload the page if this is an update
        return window.location.reload();
      }
      return window.location.replace('/register/complete');
    }, function (jqXHR, status, errorThrown) {
      alert("An error occurred while submitting your application. Please try again. " +
              "If this issue persists, let us know via contact@hackillinois.org.");
      enableButton();
    });
  });

  $(ids.fields.gender).selectize(_createSimpleSelectizeConfig(genderOptions));
  $(ids.fields.diet).selectize(_createSimpleSelectizeConfig(dietOptions));
  $(ids.fields.shirtSize).selectize(_createSimpleSelectizeConfig(shirtOptions));
  $(ids.fields.professionalInterest).selectize(_createSimpleSelectizeConfig(professionalOptions));
  $(ids.fields.hackathonAttendance).selectize(_createSimpleSelectizeConfig(hackathonAttendanceOptions));
  $(ids.fields.teamPlayer).selectize(_createSimpleSelectizeConfig(yesNoOptions, function(value) {
      var $teamMembers = $('#hackathon-team-members-followup, #hackathon-team-members-followup-caption');
      if (value === 'YES' || value === 'MAYBE') {
        $teamMembers.removeClass('hidden');
      } else {
        $teamMembers.addClass('hidden');
      }
      _validateActiveForm(true);
    }));

  $schoolSelectize = $(ids.fields.school).selectize({
    options: schoolOptions,
    labelField: 'name',
    valueField: 'value',
    sortField: 'name',
    searchField: ['name', 'search'],
    maxItems: 1,
    create: function (input, callback) {
      return callback({
        'name': input,
        'value': input,
        'search': []
      });
    },
    onChange: function(value) {
      _validateActiveForm(true);
    }
  });

  $majorSelectize = $(ids.fields.major).selectize({
    options: majorOptions,
    labelField: 'name',
    valueField: 'name',
    sortField: 'name',
    searchField: ['name', 'value', 'search'],
    maxItems: 1,
    create: function (input, callback) {
      return callback({
        'name': input,
        'value': input,
        'search': []
      });
    },
    onChange: function(value) {
      _validateActiveForm(true);
    }
  });

  $graduationSelectize = $(ids.fields.graduationYear).selectize({
    options: graduationYearOptions,
    labelField: 'value',
    valueField: 'value',
    sortField: [{field: 'value', direction: 'desc'}, {field: '$score'}],
    searchField: ['value'],
    maxItems: 1,
    onChange: function(value) {
      _validateActiveForm(true);
    },
    create: function(input, callback) {
      if (input == parseInt(input, 10)) {
        return callback({
          'value': input,
          'text': input
        });
      }
      return callback({ value: '', text: '' });
    }
  });

  $(ids.fields.teamMembers).selectize({
    delimiter: ',',
    persist: false,
    maxItems: 3,
    create: function(input, callback) {
      // only allow valid email addresses
      if( /(.+)@(.+){2,}\.(.+){2,}/.test(input) ){
        return callback({
            value: input,
            text: input
        });
      }
      return callback({value: '', text: ''});
    }
  });

  if ($(ids.globals.statusDetail).hasClass('status-complete') || $(ids.globals.statusDetail).hasClass('status-accepted')) {
    var $registrationDate = $('[data-registration-date]');
    var registrationDate = Number($registrationDate.attr('data-registration-date'));
    $registrationDate.html(" on " + moment(registrationDate).format("MMMM DD, YYYY"));

    $('.progress-container, .progress-path-container').addClass('complete');
    $('.progress-icon').css('cursor', 'pointer');
    $('.progress-icon').on('click', function (event) {
      var $parent = $(this).parent();
      var progress = $parent.attr('data-related');
      progress = (progress === 'hackathon') ? 'hackathonA' : progress;
      var desiredProgress = weights[progress];
      var currentProgress = _determineProgress();
      var difference = desiredProgress - currentProgress;

      if (difference === 0) return;

      $animator.slideUp('slow', 'easeInOutBack', function () {
        if (difference < 0) {
          while (difference < 0) {
            if (difference + 1 >= 0) backCallback(undefined, true);
            else backCallback();
            difference++;
          }
        } else {
          while (difference > 0) {
            if (difference - 1 <= 0) nextCallback(undefined, true);
            else nextCallback();
            difference--;
          }
        }
      });
    });

    var customSelectizes = { };
    customSelectizes[ids.fields.school] = $schoolSelectize[0].selectize;
    customSelectizes[ids.fields.major] = $majorSelectize[0].selectize;
    customSelectizes[ids.fields.graduationYear] = $graduationSelectize[0].selectize;

    for (var field in customSelectizes) {
      var selectize = customSelectizes[field];
      var selectizeValue = $(field).attr('data-selectize-value');

      if (!( selectizeValue in selectize.options)) {
        var option = { 'name': selectizeValue, 'value': selectizeValue };
        if (field !== ids.fields.graudationYear) option.search = [];
        selectize.addOption(option);
      }
      selectize.setValue(selectizeValue);
    }

  }

  _initializeParsley();
  initialize();
});
