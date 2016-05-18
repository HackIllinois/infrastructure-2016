$(document).ready(function() {
  $.ajax({
    url: "https://api.hackillinois.org/items",
    type: "GET",
    dataType: "json",
    success: function(data) {
      $('#hardwareTable').empty();

      var html = "<tr>";
      html+= "<th>Hardware</th>";
      html+= "<th>Quantity</th>";
      html+= "<th>Description</th>";
      html+= "</tr>";

      $('#hardwareTable').append(html);
      html = "";

      for(var i = 0; i < data["items"].length; i++) {
        var description = data["items"][i]["description"];
        var name = data["items"][i]["name"];
        var quantityLeft = data["items"][i]["quantity_left"];

        html+= "<tr>";
        html+= "<td>"+name+"</td>";
        html+= "<td>"+quantityLeft+"</td>";
        html+= "<td>"+description+"</td>";
        html+= "</tr>";
        $('#hardwareTable').append(html);
        html = '';
      }
    }
  });
});
