from http import HTTPStatus


ERRORS = {
    HTTPStatus.BAD_REQUEST: "Bad Request",
    HTTPStatus.FORBIDDEN: "Forbidden",
    HTTPStatus.NOT_FOUND: "Not Found",
    HTTPStatus.UNPROCESSABLE_ENTITY: "Invalid Request",
    HTTPStatus.INTERNAL_SERVER_ERROR: "Internal Server Error",
}
