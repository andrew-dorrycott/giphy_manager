# Standard imports
import functools
import json
import logging
import time
import uuid

# Third party imports
import flask

# Application imports
from clients import giphy
from models import bookmarks
from models import categories
from models import database
from models import users
import config


LOGGER = logging.getLogger(__name__)
base = flask.Blueprint("base", __name__, template_folder="templates")


def generate_token():
    return uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=time.time().hex()).hex


# This belongs in lib.funcs
def is_authenticated():
    """
    Handles checking if the requestor is authenticated. If not, sends them to
    the login page
    """

    def wrapper(function):
        """The outer wrapper for :func:`is_authenticated`.

        :param function: The function to execute if authenticated.
        :type function: function
        :returns: The wrapped function.
        :rtype: function
        """

        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            """The inner wrapper for :func:`is_authenticated`.

            :param args: Argument list, passed to `function`.
            :type args: list
            :param kwargs: Argument keyword dict, passed to `function`.
            :returns: The called function.
            :rtype: the return type of `function` from :func:`wrapper`
            """
            token = flask.request.cookies.get("X-Auth-Token")
            found_user = (
                database.session.query(users.User)
                .filter(users.User.token == token)
                .all()
            )
            if found_user:
                # Very simple authentication
                return function(*args, **kwargs)
            else:
                response = flask.make_response(flask.redirect("/login"))
                response.headers["forward"] = flask.request.url
                return response

        # Des be important, hehehe (whoops)
        return wrapped

    return wrapper


@base.route("/")
@is_authenticated()
def default():
    """
    Default controller to forward users to the proper location

    :returns: Text for the user
    :rtype: str
    """
    return flask.redirect("/search")


@base.route("/view")
@is_authenticated()
def view():
    """
    Page for users to view their saved/favorited gifs

    :returns: Rendered template
    :rtype: str
    """
    # Load all saved images (includes favorites)
    return flask.render_template("view.html")


@base.route("/search")
@is_authenticated()
def search():
    """
    Page for users to search Giphy

    :returns: Rendered template
    :rtype: str
    """
    return flask.render_template("search.html")


@base.route("/do_search/<query>")
@is_authenticated()
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

        results = giphy.Client().search(
            query=query, limit=limit, offset=offset
        )
        output["pagination"] = results["pagination"]

        user = (
            database.session.query(users.User)
            .filter(users.User.token == flask.request.cookies["X-Auth-Token"])
            .one()
        )

        # Grab existing bookmarks to render on the search page
        gifids = [item.get("id") for item in results.get("data", [])]
        found_bookmarks = (
            database.session.query(bookmarks.Bookmark)
            .filter(bookmarks.Bookmark.giphy_id.in_(gifids))
            .filter(bookmarks.Bookmark.user == user)
            .all()
        )
        user_bookmarks = {
            bookmark.giphy_id: {
                "favorite": bookmark.favorite,
                "categories": [
                    category.to_dict() for category in bookmark[0].categories
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
                    "favorite": user_bookmarks.get(item.get("id"), {}).get(
                        "favorite", False
                    ),
                    "saved": item.get("id") in user_bookmarks,
                    "categories": user_bookmarks.get(item.get("id"), {}).get(
                        "categories", []
                    ),
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
@is_authenticated()
def get_gif_by_id(gifid):
    """
    REST-like endpoint to get a gif by id from GIPHY

    :returns: Customized output from GIPHY
    :rtype: json
    """
    output = {"data": [], "error": ""}

    try:
        results = giphy.Client().get(gifid=gifid)

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
            database.session.query(users.User)
            .filter(users.User.token == flask.request.cookies["X-Auth-Token"])
            .one()
        )

        bookmark = (
            database.session.query(bookmarks.Bookmark)
            .filter(bookmarks.Bookmark.giphy_id == gifid)
            .filter(bookmarks.Bookmark.user == user)
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
@is_authenticated()
def save_gif_by_id(gifid):
    """
    REST-like endpoint to save gifs to the user's potato space

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        database.session.query(users.User)
        .filter(users.User.token == flask.request.cookies["X-Auth-Token"])
        .one()
    )

    already_bookmarked = (
        database.session.query(bookmarks.Bookmark)
        .filter(bookmarks.Bookmark.giphy_id == gifid)
        .filter(bookmarks.Bookmark.user == user)
        .all()
    )

    if already_bookmarked:
        return  # Already bookmarked
    else:
        database.session.add(bookmarks.Bookmark(user=user, giphy_id=gifid))
        database.session.commit()


@base.route("/favorite_gif_by_id/<gifid>")
@is_authenticated()
def favorite_gif_by_id(gifid):
    """
    REST-like endpoint to save gifs to the user's potato space

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        database.session.query(users.User)
        .filter(users.User.token == flask.request.cookies["X-Auth-Token"])
        .one()
    )

    already_bookmarked = (
        database.session.query(bookmarks.Bookmark)
        .filter(bookmarks.Bookmark.giphy_id == gifid)
        .filter(bookmarks.Bookmark.user == user)
        .all()
    )

    if already_bookmarked:
        already_bookmarked[0].favorite = True
    else:
        database.session.add(
            bookmarks.Bookmark(user=user, giphy_id=gifid, favorite=True)
        )

    database.session.commit()


@base.route("/remove_gif_by_id/<gifid>")
@is_authenticated()
def remove_gif_by_id(gifid):
    """
    REST-like endpoint to remove gifs from the user's potato space

    :returns: Customized output from GIPHY
    :rtype: json
    """
    user = (
        database.session.query(users.User)
        .filter(users.User.token == flask.request.cookies["X-Auth-Token"])
        .one()
    )

    bookmark = (
        database.session.query(bookmarks.Bookmark)
        .filter(bookmarks.Bookmark.giphy_id == gifid)
        .filter(bookmarks.Bookmark.user == user)
        .all()
    )

    if bookmark:
        bookmark[0].delete()
        database.session.commit()


@base.route("/categories")
@is_authenticated()
def get_categories():
    """
    Page users can use to categories from

    :returns: Rendered template
    :rtype: str
    """
    # Allow user to add/change/remove categories
    return flask.render_template("categories.html")


@base.route("/login", methods=("GET", "POST"))
def login():
    """
    Page for existing users to login

    :returns: Rendered template
    :rtype: str
    """
    LOGGER.debug(flask.request.form)
    LOGGER.debug(flask.g.get("tokens"))
    if flask.request.form:
        next_page = flask.request.headers.get("forward", "/search")
        username = flask.request.form.get("username")
        password = flask.request.form.get("password")

        found_user = (
            database.session.query(users.User)
            .filter(users.User.username == username)
            .filter(users.User.password == password)
            .all()
        )

        if found_user:
            user = found_user[0]
            new_token = generate_token()
            user.token = new_token
            database.session.commit()

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
            error = "Invalid Login Credentials"
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
            database.session.query(users.User)
            .filter(users.User.username == username)
            .all()
        )

        if found_user:
            # Send this to the template
            error = "Username already exists"
            return flask.render_template("register.html")
        elif password1 != password2:
            error = "Passwords do not match"
            return flask.render_template("register.html")
        else:
            new_token = generate_token()
            new_user = users.User(
                username=username, password=password1, token=new_token
            )
            database.session.add(new_user)
            database.session.commit()

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
