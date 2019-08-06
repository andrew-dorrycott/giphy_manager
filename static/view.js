

function addCategory(gifid) {
  var xhttp = new XMLHttpRequest();
  // When the Add button is clicked, add the category to the bookmark
  var categories = document.getElementById("categories_" + gifid);
  var new_category = document.getElementById("categories_for_" + gifid);
  var category_id = new_category.options[new_category.selectedIndex].value;
  var category_name = new_category.options[new_category.selectedIndex].text;

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      categories.innerHTML += (
        "<div id=\"cat_" + gifid + "_" + category_id + "\" align=\"left\">"
        + "<button type=\"button\" onclick=\"removeCategory('" + gifid + "', "
        + category_id + ")\">Remove</button>" + "&nbsp;&nbsp;&nbsp; "
        + category_name + "</div>"
      );
    }
  };

  xhttp.open("GET", "/add_categories/" + gifid + "/" + category_id);
  xhttp.send();
}


function removeCategory(gifid, category_id) {
  var xhttp = new XMLHttpRequest();
  // When the Add button is clicked, add the category to the bookmark
  var category = document.getElementById("cat_" + gifid + "_" + category_id);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      // Remove the category from the div
      category.innerHTML = "";
    }
  };

  xhttp.open("GET", "/remove_categories/" + gifid + "/" + category_id);
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