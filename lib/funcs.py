# Standard imports
import functools
import hashlib

# Third party imports
import flask

# Application imports
import config
import models


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
                models.database.session.query(models.users.User)
                .filter(models.users.User.token == token)
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


def encrypt(value):
    """
    Encrypts the input

    :param value: Input to be encrypted
    :type value: str
    :returns: Returns the encrypted value
    :rtype: byte
    """
    return hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=value.encode("utf-8"),
        salt=config.postgresql["salt"].encode("utf-8"),
        iterations=100000,
    )
