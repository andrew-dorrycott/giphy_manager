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

    :returns: Rendered template
    :rtype: json
    """
    # Provided page to search Giphy, load results of each search
    # Allow user to save/favorite images
    # Allow user to categorize image after saving/favoriting
    output = {"count": 0, "data": [], "error": "", "pagination": {}}

    results = giphy.Client().search(query)
    output["pagination"] = results["pagination"]

    for item in results.get("data", []):
        # We only want specific information back from GIPHY
        output["data"].append(
            {
                "type": item.get("type", "Error Data Lost"),
                "id": item.get("id", "Error Data Lost"),
                "url": item.get("url", "Error Data Lost"),
                "title": item.get("title", "Error Data Lost"),
                "images": item.get("images", {})
            }
        )

    if not output["data"]:
        output["error"] = "No results for {}".format(flask.escape(query))

    output["count"] = len(output["data"])

    return json.dumps(output)


@base.route("/categories")
@is_authenticated()
def categories():
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
