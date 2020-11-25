# Standard imports
import json
import logging
import time
import uuid

# Third party imports
import flask
import sqlalchemy

# Application imports
import clients
import config
import lib
import models


LOGGER = logging.getLogger(__name__)
base = flask.Blueprint("base", __name__, template_folder="templates")


def generate_token():
    """
    Generates a unique enough token for users to use as already authenticated

    :returns: Hex token
    :rtype: str
    """
    return uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=time.time().hex()).hex


@base.route("/")
@lib.funcs.is_authenticated()
def default():
    """
    Default controller to forward users to the proper location

    :returns: Text for the user
    :rtype: str
    """
    return flask.redirect("/search")


@base.route("/view")
@lib.funcs.is_authenticated()
def view():
    """
    Page for users to view their saved/favorited gifs

    :returns: Rendered template
    :rtype: str
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    all_bookmarks = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.user == user)
        .all()
    )
    output = []
    for bookmark in all_bookmarks:
        giphy_results = (
            clients.giphy.Client().get(bookmark.giphy_id).get("data", {})
        )
        output.append(
            {
                "type": giphy_results.get("type", "Error Data Lost"),
                "id": giphy_results.get("id", "Error Data Lost"),
                "url": giphy_results.get("url", "Error Data Lost"),
                "title": giphy_results.get("title", "Error Data Lost"),
                "images": giphy_results.get("images", {}),
                "favorited": bookmark.favorite,
                "saved": True,
                "categories": [
                    category.to_dict() for category in bookmark.categories
                ],
            }
        )
    # Get items from GIPHY after grabbing the bookmarked items
    number_of_items = len(output)
    enumerated = enumerate(output)

    return flask.render_template(
        "view.html",
        number_of_items=number_of_items,
        enumerated=enumerated,
        user=user,
    )


@base.route("/search")
@lib.funcs.is_authenticated()
def search():
    """
    Page for users to search Giphy

    :returns: Rendered template
    :rtype: str
    """
    return flask.render_template("search.html")


@base.route("/do_search/<query>")
@lib.funcs.is_authenticated()
def do_search(query):
    """
    REST-like endpoint to search GIPHY and get back a portion of the response
    in json

    :returns: Customized output from GIPHY
    :rtype: json
    """
    # Provided page to search Giphy, load results of each search
    # Allow user to save/favorite images
    # Allow user to categorize image after saving/favoriting
    output = {"count": 0, "data": [], "error": "", "pagination": {}}

    try:
        # Not using get's default in case requester sends blank string
        limit = int(flask.request.args.get("limit") or 25)
        offset = int(flask.request.args.get("offset") or 0)

        results = clients.giphy.Client().search(
            query=query, limit=limit, offset=offset
        )
        output["pagination"] = results["pagination"]

        user = (
            models.database.session.query(models.users.User)
            .filter(
                models.users.User.token
                == flask.request.cookies["X-Auth-Token"]
            )
            .one()
        )

        # Grab existing bookmarks to render on the search page
        gifids = [item.get("id") for item in results.get("data", [])]
        found_bookmarks = (
            models.database.session.query(models.bookmarks.Bookmark)
            .filter(models.bookmarks.Bookmark.giphy_id.in_(gifids))
            .filter(models.bookmarks.Bookmark.user == user)
            .all()
        )

        user_bookmarks = {
            bookmark.giphy_id: {
                "favorited": bookmark.favorite,
                "categories": [
                    category.to_dict() for category in bookmark.categories
                ],
            }
            for bookmark in found_bookmarks
        }

        for item in results.get("data", []):
            # We only want specific information back from GIPHY
            output["data"].append(
                {
                    "type": item.get("type", "Error Data Lost"),
                    "id": item.get("id", "Error Data Lost"),
                    "url": item.get("url", "Error Data Lost"),
                    "title": item.get("title", "Error Data Lost"),
                    "images": item.get("images", {}),
                    "favorited": models.user_models.bookmarks.get(
                        item.get("id"), {}
                    ).get("favorited", False),
                    "saved": item.get("id") in user_bookmarks,
                    "categories": models.user_models.bookmarks.get(
                        item.get("id"), {}
                    ).get("categories", []),
                }
            )

        if not output["data"]:
            output["error"] = "No results for {}".format(flask.escape(query))

        output["count"] = len(output["data"])
    except ValueError:
        message = "Invalid parameters: limit={} and/or offset={}".format(
            flask.escape(flask.request.args.get("limit")),
            flask.escape(flask.request.args.get("offset")),
        )
        output["error"] = message
    except Exception as error:
        LOGGER.exception(error)
        output["error"] = "Unexpected error occurred"

    return json.dumps(output)


@base.route("/get_gif_by_id/<gifid>")
@lib.funcs.is_authenticated()
def get_gif_by_id(gifid):
    """
    REST-like endpoint to get a gif by id from GIPHY

    :returns: Customized output from GIPHY
    :rtype: json
    """
    output = {"data": [], "error": ""}

    try:
        results = clients.giphy.Client().get(gifid=gifid)

        item = results.get("data", {})
        # We only want specific information back from GIPHY
        output["data"] = {
            "type": item.get("type", "Error Data Lost"),
            "id": item.get("id", "Error Data Lost"),
            "url": item.get("url", "Error Data Lost"),
            "title": item.get("title", "Error Data Lost"),
            "images": item.get("images", {}),
            "favorite": False,
            "saved": False,
            "categories": [],
        }

        user = (
            models.database.session.query(models.users.User)
            .filter(
                models.users.User.token
                == flask.request.cookies["X-Auth-Token"]
            )
            .one()
        )

        bookmark = (
            models.database.session.query(models.bookmarks.Bookmark)
            .filter(models.bookmarks.Bookmark.giphy_id == gifid)
            .filter(models.bookmarks.Bookmark.user == user)
            .all()
        )

        if bookmark:
            output["data"]["saved"] = True
            output["data"]["favorite"] = bookmark[0].favorite
            output["data"]["categories"] = [
                category.to_dict() for category in bookmark[0].categories
            ]

        if not output["data"]:
            output["error"] = "No results for {}".format(flask.escape(gifid))

    except Exception as error:
        LOGGER.exception(error)
        output["error"] = "Unexpected error occurred"

    return json.dumps(output)


@base.route("/save_gif_by_id/<gifid>")
@lib.funcs.is_authenticated()
def save_gif_by_id(gifid):
    """
    REST-like endpoint to save gifs to the user's potato space

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    already_bookmarked = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.giphy_id == gifid)
        .filter(models.bookmarks.Bookmark.user == user)
        .all()
    )

    if already_bookmarked:
        return flask.make_response("")  # Already bookmarked
    else:
        models.database.session.add(
            models.bookmarks.Bookmark(user=user, giphy_id=gifid)
        )
        models.database.session.commit()

    return flask.make_response("")


@base.route("/favorite_gif_by_id/<gifid>")
@lib.funcs.is_authenticated()
def favorite_gif_by_id(gifid):
    """
    REST-like endpoint to favorite gifs

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    already_bookmarked = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.giphy_id == gifid)
        .filter(models.bookmarks.Bookmark.user == user)
        .all()
    )

    if already_bookmarked:
        already_bookmarked[0].favorite = True
    else:
        models.database.session.add(
            models.bookmarks.Bookmark(user=user, giphy_id=gifid, favorite=True)
        )

    models.database.session.commit()

    return flask.make_response("")


@base.route("/unfavorite_gif_by_id/<gifid>")
@lib.funcs.is_authenticated()
def unfavorite_gif_by_id(gifid):
    """
    REST-like endpoint to unfavorite gifs

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    already_bookmarked = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.giphy_id == gifid)
        .filter(models.bookmarks.Bookmark.user == user)
        .all()
    )

    if already_bookmarked:
        already_bookmarked[0].favorite = False
        models.database.session.commit()

    return flask.make_response("")


@base.route("/remove_gif_by_id/<gifid>")
@lib.funcs.is_authenticated()
def remove_gif_by_id(gifid):
    """
    REST-like endpoint to remove gifs from the user's potato space

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )
    bookmark = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.giphy_id == gifid)
        .filter(models.bookmarks.Bookmark.user == user)
        .one()
    )

    BookmarkXrefCategory = (
        models.bookmark_xref_models.categories.BookmarkXrefCategory
    )
    (
        models.database.session.query(BookmarkXrefCategory)
        .filter(BookmarkXrefCategory.bookmark_id == bookmark.id)
        .delete()
    )
    models.database.session.delete(bookmark)
    models.database.session.commit()

    return flask.make_response("")


@base.route("/get_categories")
@lib.funcs.is_authenticated()
def get_categories():
    """
    REST-like endpoint to remove gifs from the user's potato space

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    results = [category.to_dict() for category in user.categories]

    return json.dumps(results)


@base.route("/add_categories/<gifid>/<category_id>")
@lib.funcs.is_authenticated()
def add_categories_to(gifid, category_id):
    """
    REST-like endpoint to add a category to a bookmarked gif

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    bookmark = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.giphy_id == gifid)
        .filter(models.bookmarks.Bookmark.user == user)
        .one()
    )

    try:
        models.database.session.add(
            models.bookmark_xref_models.categories.BookmarkXrefCategory(
                bookmark_id=bookmark.id, category_id=category_id
            )
        )

        models.database.session.commit()
    except sqlalchemy.exc.IntegrityError:
        # This should return a non 200 for already being present
        return flask.make_response("")

    return flask.make_response("")


@base.route("/remove_categories/<gifid>/<category_id>")
@lib.funcs.is_authenticated()
def remove_categories_to(gifid, category_id):
    """
    REST-like endpoint to remove a category from a bookmarked gif

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    bookmark = (
        models.database.session.query(models.bookmarks.Bookmark)
        .filter(models.bookmarks.Bookmark.giphy_id == gifid)
        .filter(models.bookmarks.Bookmark.user == user)
        .one()
    )

    BookmarkXrefCategory = (
        models.bookmark_xref_models.categories.BookmarkXrefCategory
    )
    (
        models.database.session.query(BookmarkXrefCategory)
        .filter(BookmarkXrefCategory.bookmark_id == bookmark.id)
        .filter(BookmarkXrefCategory.category_id == category_id)
        .delete()
    )

    models.database.session.commit()

    return flask.make_response("")


@base.route("/categories")
@lib.funcs.is_authenticated()
def view_categories():
    """
    Page users can use to categories from

    :returns: Rendered template
    :rtype: str
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    categories = user.categories
    return flask.render_template(
        "models.categories.html", categories=categories
    )


@base.route("/add_category/<category_name>")
@lib.funcs.is_authenticated()
def add_category(category_name):
    """
    REST-like endpoint to add a category

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    existing_category = (
        models.database.session.query(models.categories.Category)
        .filter(models.categories.Category.name == category_name)
        .filter(models.categories.Category.user == user)
        .all()
    )

    if existing_category:
        # Already exists, move on
        return json.dumps({})

    new_category = models.categories.Category(name=category_name, user=user)
    models.database.session.add(new_category)
    models.database.session.commit()

    return json.dumps(new_category.to_dict())


@base.route("/remove_category/<category_id>")
@lib.funcs.is_authenticated()
def remove_category(category_id):
    """
    REST-like endpoint to remove a category

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        models.database.session.query(models.users.User)
        .filter(
            models.users.User.token == flask.request.cookies["X-Auth-Token"]
        )
        .one()
    )

    BookmarkXrefCategory = (
        models.bookmark_xref_models.categories.BookmarkXrefCategory
    )
    (
        models.database.session.query(BookmarkXrefCategory)
        .filter(BookmarkXrefCategory.category_id == category_id)
        .delete()
    )

    (
        models.database.session.query(models.categories.Category)
        .filter(models.categories.Category.id == category_id)
        .filter(models.categories.Category.user_id == user.id)
        .delete()
    )

    models.database.session.commit()

    return flask.make_response("")


@base.route("/login", methods=("GET", "POST"))
def login():
    """
    Page for existing users to login

    :returns: Rendered template
    :rtype: str
    """
    if flask.request.form:
        next_page = flask.request.headers.get("forward", "/search")
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")

        found_user = (
            models.database.session.query(models.users.User)
            .filter(models.users.User.username == username)
            .all()
        )
        LOGGER.debug(found_user)

        if found_user:
            user = found_user[0]
            LOGGER.debug(user.password)

            if user.password != lib.funcs.encrypt(password):
                # Invalid login
                return flask.render_template("login.html")

            new_token = generate_token()
            user.token = new_token
            models.database.session.commit()

            response = flask.make_response(flask.redirect(next_page))
            response.set_cookie(
                "X-Auth-Token",
                new_token,
                max_age=28800,
                secure=config.app.get("secure"),
            )
            return response
        else:
            # Send this to the template
            # error = "Invalid Login Credentials"
            return flask.render_template("login.html")
    else:
        return flask.render_template("login.html")


@base.route("/register", methods=("GET", "POST"))
def register():
    """
    Page for new users to sign up

    :returns: Rendered template
    :rtype: str
    """
    if flask.request.form:
        next_page = flask.request.headers.get("forward", "/search")
        username = flask.request.form.get("username")
        password1 = flask.request.form.get("password1")
        password2 = flask.request.form.get("password2")

        found_user = (
            models.database.session.query(models.users.User)
            .filter(models.users.User.username == username)
            .all()
        )

        if found_user:
            # Send this to the template
            # error = "Username already exists"
            return flask.render_template("register.html")
        elif password1 != password2:
            # error = "Passwords do not match"
            return flask.render_template("register.html")
        else:
            new_token = generate_token()
            new_user = models.users.User(
                username=username, password=password1, token=new_token
            )
            models.database.session.add(new_user)
            models.database.session.commit()

            response = flask.make_response(flask.redirect(next_page))
            response.set_cookie(
                "X-Auth-Token",
                new_token,
                max_age=28800,
                secure=config.app.get("secure"),
            )
            return response
    else:
        return flask.render_template("register.html")
