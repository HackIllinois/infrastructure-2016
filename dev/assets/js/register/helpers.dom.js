function _nextCallback(deactivatedForm) {
    if (!deactivatedForm) return false;

    var currentProgress = _determineProgress(deactivatedForm);
    currentProgress++;
    if (currentProgress >= weights.length) return false;

    var activeForm = _findFormByProgress(currentProgress);
    activeForm.addClass('active');

    initialize(activeForm);
}

function _backCallback(deactivatedForm) {
    if (!deactivatedForm) return;

    var currentProgress = _determineProgress(deactivatedForm);
    currentProgress--;
    if (currentProgress <= 0) return;

    var activeForm = _findFormByProgress(currentProgress);
    activeForm.addClass('active');

    initialize(activeForm);
}

function _findActiveForm() {
  return $('form.active');
}

function _findFormByProgress(currentProgress) {
  return $('form[data-progress-weight=' + currentProgress + ']');
}

function _cleanSectionName(section) {
  if (section === 'hackathonA' || section === 'hackathonB') return 'hackathon';
  return section;
}

function _validateActiveForm(practicalOnly) {
  var activeForm = _findActiveForm();
  if (practicalOnly && !activeForm.hasClass('validating')) return;

  activeForm.addClass("validating");
  return {
    form: activeForm,
    result: activeForm.parsley().validate()
  };
}

function _deactivateForm(activeForm, callback) {
  if (!activeForm) activeForm = _findActiveForm();

  if (!callback) {
    activeForm.removeClass('active');
    return activeForm;
  }

  $animator.slideUp('slow', 'easeInOutBack', function() {
    activeForm.removeClass('active');
    return callback(activeForm);
  });
}

function _validateAndDeactivateForm(callback) {
  var validation = _validateActiveForm();
  if (!validation.result) return false;
  if (!callback) return _deactivateForm(validation.form);

  _deactivateForm(validation.form, callback);
}

function _deactivateElements(clazz) {
  $('.' + clazz).removeClass('active');
}

function _activateElement(clazz, section) {
  $('.' + clazz + '[data-related=' + _cleanSectionName(section) + ']').addClass('active');
}

function _determineSection(activeForm) {
  if (!activeForm) activeForm = _findActiveForm();
  if (!activeForm.length) return;

  // find associated section
  var formId = "#" + activeForm.attr('id');
  var retVal;
  for (var section in ids.sections) {
    var id = ids.sections[section];
    if (id === formId) {
      retVal = section;
      break;
    }
  }
  return retVal;
}

function _determineProgress(activeForm) {
  if (!activeForm) activeForm = _findActiveForm();
  if (!activeForm.length) return -1;
  return parseInt(activeForm.attr('data-progress-weight'));
}

function _handleNavs(section) {
  $('.registration-nav').addClass('visible');
  nextEnabled = true;
  backEnabled = true;
  if (section === initialSection) {
    $(ids.globals.navBackMobile).removeClass('visible');
    $(ids.globals.navBack).removeClass('visible');
    backEnabled = false;
  } else if (section === finalSection) {
    $(ids.globals.navNextMobile).removeClass('visible');
    $(ids.globals.navNext).removeClass('visible');
    nextEnabled = false;
  }
}

function _handleHeaders(section) {
  _deactivateElements('section-title');
  _activateElement('section-title', section);
}

function _handleProgress(section) {
  _deactivateElements('progress-container');
  _deactivateElements('progress-path-container');

  var progress = weights[section];
  $('.progress-container, .progress-path-container').each(function () {
    var $this = $(this);
    if (parseInt($this.attr('data-related-weight')) <= progress) {
      $this.addClass('active');
    }
  });
}

function _initializeParsley() {
  $('form.validatable').each(function () {
    $(this).parsley(parsleyOptions);
  });
}

function _resetParsley(form) {
  if (!form) form = _findActiveForm();
  form.parsley().destroy();
  form.parsley(parsleyOptions);
}

function _createSimpleSelectizeConfig(options, onChange) {
  var config = {
    options: options,
    labelField: 'name',
    valueField: 'value',
    searchField: 'name',
    maxItems: 1,
    create: false
  };
  if (onChange) {
    config.onChange = onChange;
  } else {
    config.onChange = function(value) {
      _validateActiveForm(true);
    };
  }

  return config;
}
