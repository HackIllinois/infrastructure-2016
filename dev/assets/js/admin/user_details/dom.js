$(function () {
    var $shirtCollected = $('#shirtCollected');
    var $swagCollected = $('#swagCollected');
    var $isVolunteering = $('#isVolunteering');
    var $meals = $('#meals');
    var $mealsTable = $('#mealsTable');
    var $hardwareTable = $('#hardwareTable');
    var $hardwareCheckoutId = $('#hardwareCheckoutId');
    var $hardwareReturnId = $('#hardwareReturnId');
    var $hardwareCheckout = $('#hardware-checkout');
    var $hardwareReturn = $('#hardware-return');
    var userId;
    var secret;

    var populateTable = function(items){
      $hardwareTable.empty();

      var html = "<tr>";
      html+= "<th>Hardware Checked Out</th>";
      html+= "</tr>";

      $hardwareTable.append(html);
      html = "";
      for(var i = 0; i < items.length; i ++){
        html+= "<tr>";
        html+= "<td>"+items[i]+"</td>";
        html+= "</tr>";
        $('#hardwareTable').append(html);
        html = '';
      }
    };

    $(document).ready(function(){
      var date = new Date();
      var hours = date.getHours();
      var path = window.location.pathname;
      userId = path.substring(path.lastIndexOf('/') + 1);

      if (0 <= hours && hours < 2) {
        $('#snack').removeClass('hidden');
      } else if (3 <= hours && hours < 5) {
        $('#mini-meal').removeClass('hidden');
      } else if (8 <= hours && hours < 10) {
        $('#breakfast').removeClass('hidden');
      } else if (11 <= hours && hours < 13) {
        $('#lunch').removeClass('hidden');
      } else if (19 <= hours && hours < 21) {
        $('#dinner').removeClass('hidden');
      }

      $.ajax({
        url: "/admin/hardwaresecret",
        type: 'GET',
        dataType: "json",
        success: function(data) {
          secret = data['secret'];
        },
        error : function(){
          alert('Unable to fetch hardware-api secret.');
        }
      });

      $.ajax({
          url: "https://api.hackillinois.org/hacker/" + userId,
          type: "GET",
          dataType: "json",
          success: function(data) {
            var barcode = data["barcode"];
            var id = data["id"];
            var items = data["items_checked_out"].split(',');
            populateTable(items);
          },

          error: function(jqXHR, textStatus, errorThrown) {
            var items = [];
            populateTable(items);
          }
      });
    });

    $hardwareCheckout.on('submit', function (event) {
      event.preventDefault();

      var isValid = $hardwareCheckout.parsley().validate();
      if (!isValid) return;

      var id = $hardwareCheckoutId.val();

      $.ajax({
          url: "https://api.hackillinois.org/items/checkout",
          type: "POST",
          data: {
                  'secret': secret,
                  'item_barcode': id,
                  'hacker_barcode': userId
                },
          dataType: "json",
          success: function(data) {
              var items = data["info"][0]["items_checked_out"].split(',');
              populateTable(items);
              var name = data["info"][1]["name"];
              alert('Successfully checked out ' + name);
          },

          error: function(jqXHR, textStatus, errorThrown) {
                alert('Item checkout unsuccessful.');
          }
      });
    });

    $hardwareReturn.on('submit', function (event) {
      event.preventDefault();

      var isValid = $hardwareReturn.parsley().validate();
      if (!isValid) return;

      var id = $hardwareReturnId.val();

      $.ajax({
          url: "https://api.hackillinois.org/items/return",
          type: "POST",
          data: {
                  'secret': secret,
                  'item_barcode': id,
                  'hacker_barcode': userId
                },
          dataType: "json",
          success: function(data) {
              var items = data["items_checked_out"].split(',');
              populateTable(items);
              alert('Successfully returned item.');
          },

          error: function(jqXHR, textStatus, errorThrown) {
                alert('Item return unsuccessful.');
          }
      });
    });

    $hardwareCheckoutId.add($hardwareReturnId).on('click', function (event) {
      $(this).val('');
    });

    $('[data-timestamp]').each(function(){
      var $this = $(this);
      var timestamp = Number($this.attr('data-timestamp'));
      $this.html(moment(timestamp).fromNow());
    });

    $shirtCollected.change(function(){
      if($shirtCollected.is(":checked")) {
        $shirtCollected.prop('disabled', true);
        $.ajax({
          type: 'PUT',
          url: window.location.pathname,
          data: {'shirt_collected': true}
        }).then(function(data, status, jqXHR){
        }, function(jqXHR, status, errorThrown){
          alert("A back-end error has occurred.");
          $shirtCollected.prop("checked", false);
          $shirtCollected.prop('disabled', false);
        });
      }
    });

    $swagCollected.change(function(){
      if($swagCollected.is(":checked")) {
        $swagCollected.prop('disabled', true);
        $.ajax({
          type: 'PUT',
          url: window.location.pathname,
          data: {'swag_collected': true}
        }).then(function(data, status, jqXHR){
        }, function(jqXHR, status, errorThrown){
          alert("A back-end error has occurred.");
          $swagCollected.prop("checked", false);
          $swagCollected.prop('disabled', false);
        });
      }
    });

      $isVolunteering.change(function(){
        if($isVolunteering.is(":checked")) {
          $isVolunteering.prop('disabled', true);
          $.ajax({
            type: 'PUT',
            url: window.location.pathname,
            data: {'is_volunteering': true}
          }).then(function(data, status, jqXHR){
          }, function(jqXHR, status, errorThrown){
            alert("A back-end error has occurred.");
            $isVolunteering.prop("checked", false);
            $isVolunteering.prop('disabled', false);
          });
        }
      });

      $meals.on('click', function(event){
        if (event.target.getAttribute('disabled')) return;

        var meal = $(event.target).attr('value');
        $.ajax({
          type: 'PUT',
          url: window.location.pathname,
          data: {'meal': meal}
        }).then(function(data, status, jqXHR){
          window.location.reload();
        }, function(jqXHR, status, errorThrown){
          alert("A back-end error has occurred.");
        });
      });

});
