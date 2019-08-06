

function buildUX() {
  var search = document.getElementById("new_category");
  search.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
      event.preventDefault();
      document.getElementById("submit").click();
    }
  });
}


function deleteCategory(category_id) {
  var xhttp = new XMLHttpRequest();
  // When the Add button is clicked, add the category to the bookmark
  var category = document.getElementById("cat_" + category_id);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      category.innerHTML = "";
    }
  };

  xhttp.open("GET", "/remove_category/" + category_id);
  xhttp.send();
}


function addCategory() {
  var xhttp = new XMLHttpRequest();

  var new_category = document.getElementById("new_category");
  var categories_table = document.getElementById("categories_table");

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var data = JSON.parse(this.responseText);
      // There's a failure when handling duplicates, leaving it for now
      if (data) {
        categories_table.innerHTML += (
          "<tr id=\"cat_" + data["id"] + "\">" + "<td align=\"left\">"
          + "<button type=\"button\" onclick=\"deleteCategory(" + data["id"]
          + ")\">Remove</button>" + "&nbsp;&nbsp;&nbsp;" + data["name"]
          + "</td></tr>"
        );
        console.log(categories_table.innerHTML)
      }
    }
  };

  xhttp.open("GET", "/add_category/" + escape(new_category.value));
  xhttp.send();
}