(function () {
  var tagXML = '<?xml version="1.0" encoding="utf-8"?><DieCutLabel Version="8.0" Units="twips"><PaperOrientation>Landscape</PaperOrientation><Id>Address</Id><PaperName>30252 Address</PaperName><DrawCommands><RoundRectangle X="0" Y="0" Width="1581" Height="5040" Rx="270" Ry="270"/></DrawCommands><ObjectInfo><TextObject><Name>FULL_NAME</Name><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/><BackColor Alpha="0" Red="255" Green="255" Blue="255"/><LinkedObjectName></LinkedObjectName><Rotation>Rotation0</Rotation><IsMirrored>False</IsMirrored><IsVariable>True</IsVariable><HorizontalAlignment>Center</HorizontalAlignment><VerticalAlignment>Middle</VerticalAlignment><TextFitMode>ShrinkToFit</TextFitMode><UseFullFontHeight>True</UseFullFontHeight><Verticalized>False</Verticalized><StyledText><Element><String>Full Name</String><Attributes><Font Family="Gotham" Size="18" Bold="False" Italic="False" Underline="False" Strikeout="False"/><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/></Attributes></Element></StyledText></TextObject><Bounds X="331.2" Y="131.4236" Width="4370.537" Height="485.5448"/></ObjectInfo><ObjectInfo><BarcodeObject><Name>BARCODE</Name><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/><BackColor Alpha="255" Red="255" Green="255" Blue="255"/><LinkedObjectName></LinkedObjectName><Rotation>Rotation0</Rotation><IsMirrored>False</IsMirrored><IsVariable>False</IsVariable><Text>0000000000000000</Text><Type>Code39</Type><Size>Small</Size><TextPosition>Bottom</TextPosition><TextFont Family="Gotham" Size="5" Bold="False" Italic="False" Underline="False" Strikeout="False"/><CheckSumFont Family="Helvetica" Size="10" Bold="False" Italic="False" Underline="False" Strikeout="False"/><TextEmbedding>None</TextEmbedding><ECLevel>0</ECLevel><HorizontalAlignment>Center</HorizontalAlignment><QuietZonesPadding Left="0" Right="0" Top="0" Bottom="0"/></BarcodeObject><Bounds X="331.2" Y="892.8" Width="4370.979" Height="600"/></ObjectInfo><ObjectInfo><TextObject><Name>WIFI_LOGIN</Name><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/><BackColor Alpha="0" Red="255" Green="255" Blue="255"/><LinkedObjectName></LinkedObjectName><Rotation>Rotation0</Rotation><IsMirrored>False</IsMirrored><IsVariable>True</IsVariable><HorizontalAlignment>Center</HorizontalAlignment><VerticalAlignment>Middle</VerticalAlignment><TextFitMode>ShrinkToFit</TextFitMode><UseFullFontHeight>True</UseFullFontHeight><Verticalized>False</Verticalized><StyledText><Element><String>wifi_username</String><Attributes><Font Family="Gotham" Size="12" Bold="False" Italic="False" Underline="False" Strikeout="False"/><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/></Attributes></Element></StyledText></TextObject><Bounds X="1698.268" Y="595.0789" Width="1495.296" Height="203.8331"/></ObjectInfo><ObjectInfo><TextObject><Name>WIFI_SSID</Name><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/><BackColor Alpha="0" Red="255" Green="255" Blue="255"/><LinkedObjectName></LinkedObjectName><Rotation>Rotation0</Rotation><IsMirrored>False</IsMirrored><IsVariable>True</IsVariable><HorizontalAlignment>Right</HorizontalAlignment><VerticalAlignment>Middle</VerticalAlignment><TextFitMode>ShrinkToFit</TextFitMode><UseFullFontHeight>True</UseFullFontHeight><Verticalized>False</Verticalized><StyledText><Element><String>IllinoisNet</String><Attributes><Font Family="Gotham" Size="12" Bold="False" Italic="False" Underline="False" Strikeout="False"/><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/></Attributes></Element></StyledText></TextObject><Bounds X="331.2" Y="599.8314" Width="1249.342" Height="203.8331"/></ObjectInfo><ObjectInfo><TextObject><Name>WIFI_PASSWORD</Name><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/><BackColor Alpha="0" Red="255" Green="255" Blue="255"/><LinkedObjectName></LinkedObjectName><Rotation>Rotation0</Rotation><IsMirrored>False</IsMirrored><IsVariable>True</IsVariable><HorizontalAlignment>Left</HorizontalAlignment><VerticalAlignment>Middle</VerticalAlignment><TextFitMode>ShrinkToFit</TextFitMode><UseFullFontHeight>True</UseFullFontHeight><Verticalized>False</Verticalized><StyledText><Element><String>wifi_password</String><Attributes><Font Family="Gotham" Size="12" Bold="False" Italic="False" Underline="False" Strikeout="False"/><ForeColor Alpha="255" Red="0" Green="0" Blue="0"/></Attributes></Element></StyledText></TextObject><Bounds X="3317.558" Y="585.785" Width="1476.407" Height="203.8331"/></ObjectInfo></DieCutLabel>';
  var tagRenderParams = dymo.label.framework.createLabelRenderParamsXml({ shadowDepth: 0.5 });
  var tagPrintParams = dymo.label.framework.createLabelWriterPrintParamsXml();
  var printerName;
  var tag;
  var dymoError = false;

  var $action = $('#action');
  var $checkinStatus = $('#checkinStatus');
  var $shirtCollected = $('#shirtCollected');
  var $swagCollected = $('#swagCollected');
  var $tagCaption = $('#tag-caption');
  var $tagDetails = $('#tag-details');

  var checkinId;

  function isCheckedIn() {
    return $action.attr('data-checked-in') === '1';
  }

  function setCheckinDate(checkinDate) {
    $checkinStatus.text("Checked in " + moment(checkinDate).fromNow());
  }

  function handleCheckin($target) {
    $target.html('Checking in...');

    var data = {
      'shirtCollected': $shirtCollected.is(':checked'),
      'swagCollected': $swagCollected.is(':checked')
    };

    $.ajax({
      type: 'POST',
      url: '/admin/checkin/' + checkinId,
      data: data,
      complete: function () {
        $target.removeProp('disabled');
      }
    }).then(function(data, status, jqXHR){
      var response = data.data;
      $tagCaption.addClass('hidden');

      if (response.credentials) {
        $tagDetails.attr('data-network-login', response.credentials.login);
        $tagDetails.attr('data-network-password', response.credentials.password);
      }

      $action.html("Print");
      $action.attr('data-checked-in', '1');

      setCheckinDate(Date.now());
      renderTagPreview();
    }, function(jqXHR, status, errorThrown){
      alert("A back-end error has occurred.");
      $action.html("Check In");
    });
  }

  function printLabel($target) {
    tag.print(printerName);
    $target.removeProp('disabled');
  }

  function initializePrinters() {
    var printers = dymo.label.framework.getPrinters();
    if (printers.length === 0) {
      alert("No DYMO printers are available. If you have not installed the DYMO drivers, please do so now. Otherwise, ensure that all cables are connected and that the DYMO service is running.");
      dymoError = true;
      return;
    }

    var printerName = "";
    for (var i = 0; i < printers.length; ++i) {
      var printer = printers[i];
      if (printer.printerType == "LabelWriterPrinter") return printer.name;
    }

    alert("The connected printer is not of type 'LabelWriterPrinter', as required. Unexpected behavior may follow.");
  }

  function renderTagPreview() {
    if (dymoError) return;

    printerName  = (printerName) ? printerName : initializePrinters();
    tag = (tag) ? tag : dymo.label.framework.openLabelXml(tagXML);

    tag.setObjectText("\FULL_NAME", $tagDetails.attr('data-first-name') + " " + $tagDetails.attr('data-last-name'));
    if (isCheckedIn()) {
      tag.setObjectText("\BARCODE", $action.attr('data-checkin-id'));
      if ($tagDetails.attr('data-network-login')) {
        tag.setObjectText("\WIFI_LOGIN", $tagDetails.attr('data-network-login'));
        tag.setObjectText("\WIFI_PASSWORD", $tagDetails.attr('data-network-password'));
      } else {
        tag.setObjectText("\WIFI_SSID", "");
        tag.setObjectText("\WIFI_LOGIN", "");
        tag.setObjectText("\WIFI_PASSWORD", "");
      }
    }

    var source = "data:image/png;base64," + tag.render(tagRenderParams, printerName);
    $('#tag-preview').attr('src', source);

    $action.removeProp('disabled');
  }

  $(function () {
      dymo.label.framework.init(renderTagPreview);

      checkinId = Number($action.attr('data-checkin-id'));
      if (isCheckedIn()) {
        var checkinDate = Number($checkinStatus.attr('data-checkin-date'));
        setCheckinDate(checkinDate);
      }

      $action.on('click', function (event) {
        event.preventDefault();

        var $this = $(this);
        $this.prop('disabled', true);

        if (isCheckedIn()) {
          printLabel($this);
        } else {
          handleCheckin($this);
        }
      });
  });
})();
