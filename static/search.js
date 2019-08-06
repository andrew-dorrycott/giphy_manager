
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
      var gifid = data["data"][x]["id"];
      var saved = data["data"][x]["saved"];
      var favorited = data["data"][x]["favorited"];

      // Bunch of images 5 to a row
      if (x % 5 == 0 & x != 0) {
        table += "<tr>";
      }

      var save_button = (
        "<button type=\"button\" id=\"bookmark_" + gifid
        + "\" onclick=\"toggleBookmark('" + gifid + "')\">"
      );
      var favorite_button = (
        "<button type=\"button\" id=\"favorite_" + gifid
        + "\" onclick=\"toggleFavorite('" + gifid + "')\">"
      );

      if (saved) {
        save_button += "Remove</button>";
      }
      else {
        save_button += "Save</button>";
      }

      if (favorited) {
        favorite_button += "Unfavorite</button>";
      }
      else {
        favorite_button += "Favorite</button>";
      }

      table += (
        "<td align=\"center\">"
        + "<img src=\"" + data["data"][x]["images"]["preview_gif"]["url"]
        + "\"/>" + "<br>" + "Title: " + data["data"][x]["title"] + "<br>"
        + "<input type=\"hidden\" id=\"saved_" + gifid + "\" value="
        + saved + ">" + "<input type=\"hidden\" id=\"favorited_" + gifid
        + "\" value=" + favorited + ">" + save_button + "&nbsp;&nbsp;&nbsp;"
        + favorite_button + "<br><div id=\"categories_" + gifid + "\"></div>"
        + "</td>"
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
        result_data.innerHTML = escape(data["error"]);
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


function addCategory(gifid) {
  var xhttp = new XMLHttpRequest();
  // When the Add button is clicked, add the category to the bookmark
  var category = document.getElementById("categories_for_" + gifid);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      // Add the new category to the div
    }
  };

  xhttp.open(
    "GET",
    (
      "/add_categories/" + gifid + "/"
      + category.options[category.selectedIndex].value
    )
  );
  xhttp.send();
}


function removeCategory(gifid) {
  var xhttp = new XMLHttpRequest();
  // When the Add button is clicked, add the category to the bookmark
  var category = document.getElementById("categories_for_" + gifid);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      // Remove the category from the div
    }
  };

  xhttp.open(
    "GET",
    (
      "/remove_categories/" + gifid + "/"
      + category.options[category.selectedIndex].value
    )
  );
  xhttp.send();
}


function loadAndRenderCategories(gifid) {
  var xhttp = new XMLHttpRequest();
  var categories = document.getElementById("categories_" + gifid);

  xhttp.onreadystatechange = function() {
    var output = "";
    if (this.readyState == 4 && this.status == 200) {
      var data = JSON.parse(this.responseText);
      // Give a drop down to add categories
      output = "<select id=\"categories_for_" + gifid + "\">";

      for (var x in data) {
        output += (
          "<option value=\"" + data[x]["id"] + "\">" + data[x]["name"]
          + "</option>"
        );
      }

      output += "</select>";
      output += (
        "<button type=\"button\" onclick=\"addCategory('" + gifid
        + "')\">Add</button>"
      );
    }
    categories.innerHTML = output;
  };

  xhttp.open("GET", "/get_categories");
  xhttp.send();
}


function toggleBookmark(gifid) {
  var xhttp = new XMLHttpRequest();
  var already_saved = document.getElementById("saved_" + gifid);
  var bookmark_button = document.getElementById("bookmark_" + gifid);
  var favorite_button = document.getElementById("favorite_" + gifid);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (already_saved.value == "false") {
        bookmark_button.innerHTML = "Remove";
        already_saved.value = true;
        loadAndRenderCategories(gifid);
      }
      else {
        bookmark_button.innerHTML = "Save";
        favorite_button.innerHTML = "Favorite";
        already_saved.value = false;
        document.getElementById("favorited_" + gifid).value = false;
      }
    }
  };

  if (already_saved.value == "false") {
    xhttp.open("GET", "/save_gif_by_id/" + escape(gifid), true);
  }
  else {
    xhttp.open("GET", "/remove_gif_by_id/" + escape(gifid), true);
  }
  xhttp.send();
}


function toggleFavorite(gifid) {
  var xhttp = new XMLHttpRequest();
  var already_saved = document.getElementById("favorited_" + gifid);
  var bookmark_button = document.getElementById("bookmark_" + gifid);
  var favorite_button = document.getElementById("favorite_" + gifid);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (already_saved.value == "false") {
        bookmark_button.innerHTML = "Remove";
        favorite_button.innerHTML = "Unfavorite";
        already_saved.value = true;
        loadAndRenderCategories(gifid);
      }
      else {
        favorite_button.innerHTML = "Favorite";
        already_saved.value = false;
      }
    }
  };

  if (already_saved.value == "false") {
    xhttp.open("GET", "/favorite_gif_by_id/" + escape(gifid), true);
  }
  else {
    xhttp.open("GET", "/unfavorite_gif_by_id/" + escape(gifid), true);
  }
  xhttp.send();
}