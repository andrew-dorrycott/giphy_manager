
function buildUX() {
  var search = document.getElementById("search");
  search.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      document.getElementById("submit").click();
    }
  });
}

function renderResults(data) {
  var table = "";

  if (data["data"]) {
    table += "<table>";

    for (var x in data["data"]) {
      // Bunch of images 5 to a row
      if (x % 5 == 0) {
        table += "<tr>";
      }

      table += (
        "<td align=\"center\">"
        + "<img src=\"" + data["data"][x]["images"]["preview_gif"]["url"]
        + "\"/>" + "<br>" + "Title: " + data["data"][x]["title"] + "</td>"
      );

      if (x % 5 == 0) {
        table += "</tr>";
      }
    }
    table += "</table>";

    result_data.innerHTML = table;
  }

  return table;
}


function executeSearch() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var data = JSON.parse(this.responseText);
      if (data["error"]) {
        document.getElementById("result_count").innerHTML = "Results: 0";
        document.getElementById("result_data").innerHTML = data["error"];
      }
      else {
        document.getElementById("result_count").innerHTML = (
          "Results: " + data["pagination"]["offset"] + " - "
          + (data["pagination"]["count"] * (data["pagination"]["offset"] + 1))
          + " of " + data["pagination"]["total_count"]
        );
        result_data = document.getElementById("result_data")
        result_data.innerHTML = renderResults(data);
      }
    }
    else {
      document.getElementById("result_count").innerHTML = "Bad request";
      document.getElementById("result_data").innerHTML = "Bad request";
    }
  };

  document.getElementById("result_count").innerHTML = "Loading...";
  document.getElementById("result_data").innerHTML = "Loading...";
  xhttp.open(
    "GET",
    "/do_search/" + escape(document.getElementById("search").value),
    true
  );
  xhttp.send();
}