
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

  if (data["results"]) {
    table += "<table><tr>";

    for (var key in data["results"][0]) {
      table += ("<th align=\"center\">" + key + "</th>");
    }
    table += "</tr>";

    for (var x in data["results"]) {
      table += "<tr>";
      for (var key in data["results"][x]) {
        table += ("<td align=\"center\">" + data["results"][x][key] + "</td>");
      }
      table += "</tr>";
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
      if ("error" in data) {
        document.getElementById("result_count").innerHTML = "Results: 0";
        document.getElementById("result_data").innerHTML = data["error"];
      }
      else {
        document.getElementById("result_count").innerHTML = "Results: " + data["count"];
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
    "GET", "/search/" + escape(document.getElementById("search").value), true
  );
  xhttp.send();
}