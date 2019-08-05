
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
      if (x % 5 == 0 & x != 0) {
        table += "<tr>";
      }

      table += (
        "<td align=\"center\">"
        + "<img src=\"" + data["data"][x]["images"]["preview_gif"]["url"]
        + "\"/>" + "<br>" + "Title: " + data["data"][x]["title"] + "</td>"
      );

      if (x % 5 == 0 & x != 0) {
        table += "</tr>";
      }
    }
    table += "</table>";

    result_data.innerHTML = table;
  }

  return table;
}


function renderPagination(data) {
  var output = "";
  var button_id = "";
  var onclick = "";
  var max_pages = parseInt(
    data["pagination"]["total_count"] / data["pagination"]["count"]
  );
  var limit = data["pagination"]["count"];
  var offset = data["pagination"]["offset"];
  var total = data["pagination"]["total_count"];
  var current_page = offset / limit;

  output += (
    "Results: " + offset + " - " + (limit + offset) + " of " + total
    + "<input type=\"hidden\" id=\"limit\" value=\"" + limit + "\">" + "<br>"
    + "Page: "
  );

  var separator = false;
  for (var x = 0; x < max_pages; x++) {
    // Limit buttons to the first few, last few, and some around current page 
    if (
      (x < 3) | ((x > current_page - 3) & (x < current_page + 3))
      | (x > max_pages - 4)
    ) {
      button_id = "page_" + x;
      onclick = "newPage(" + x + ")";
      output += (
        "<button type=\"button\" id=\"" + button_id + "\" onclick=\"" + onclick
        + "\">" + (x + 1) + "</button>&nbsp;"
      );
      separator = false;
    }
    else if (separator == false) {
      output += "..&nbsp;";
      separator = true;
    }
  }
  return output;
}


function newPage(page) {
  executeSearch((page + 1) * parseInt(document.getElementById("limit").value));
}


function executeSearch(offset=0) {
  var xhttp = new XMLHttpRequest();
  var result_count = document.getElementById("result_count");
  var result_data = document.getElementById("result_data");

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var data = JSON.parse(this.responseText);
      if (data["error"]) {
        result_count.innerHTML = "Results: 0";
        result_data.innerHTML = data["error"];
      }
      else {
        result_count.innerHTML = renderPagination(data);
        result_data.innerHTML = renderResults(data);
      }
    }
    else {
      result_count.innerHTML = "Bad request";
      result_data.innerHTML = "Bad request";
    }
  };

  result_count.innerHTML = "Loading...";
  result_data.innerHTML = "Loading...";
  xhttp.open(
    "GET",
    (
      "/do_search/" + escape(document.getElementById("search").value)
      + "?limit=25&offset=" + escape(offset)
    ),
    true
  );
  xhttp.send();
}