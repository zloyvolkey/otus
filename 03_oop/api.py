#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import datetime
import hashlib
import uuid
import logging
from argparse import ArgumentParser
from http.server import HTTPServer, BaseHTTPRequestHandler

from http import HTTPStatus

from requests import MethodRequest, OnlineScoreRequest, ClientsInterestsRequest
from scoring import get_score, get_interests
from consts import ADMIN_SALT, SALT, ADMIN_LOGIN
from errors_const import ERRORS



def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(str(datetime.datetime.now().strftime(
            "%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512(
            str(request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def online_score_handler(arguments, ctx, store):
    arguments = OnlineScoreRequest(arguments)

    if not arguments.is_valid:
        return arguments.errors, HTTPStatus.UNPROCESSABLE_ENTITY

    ctx['has'] = arguments.initialized_fields

    if ctx.get('is_admin'):
        score = 42
    else:
        score = get_score(
            store=store,
            phone=str(arguments.phone),
            email=arguments.email,
            birthday=arguments.birthday and datetime.datetime.strptime(
                arguments.birthday, '%d.%m.%Y'),
            gender=arguments.gender,
            first_name=arguments.first_name,
            last_name=arguments.last_name
        )

    return {'score': score}, HTTPStatus.OK


def clients_interests_handler(arguments, ctx, store):
    arguments = ClientsInterestsRequest(arguments)

    if not arguments.is_valid:
        return ', '.join(arguments.errors), HTTPStatus.UNPROCESSABLE_ENTITY

    ctx['nclients'] = len(arguments.client_ids)

    try:
        return {client_id: get_interests(store, client_id) for client_id in arguments.client_ids}, HTTPStatus.OK
    except Exception as e:
        return {'error': str(e)}, HTTPStatus.UNPROCESSABLE_ENTITY


def method_handler(request, ctx, store):

    methods = {
        'online_score': online_score_handler,
        'clients_interests': clients_interests_handler,
    }

    method_request = MethodRequest(request['body'])

    if not method_request.is_valid:
        return ', '.join(method_request.errors), HTTPStatus.UNPROCESSABLE_ENTITY

    if not check_auth(method_request):
        return ERRORS[HTTPStatus.FORBIDDEN], HTTPStatus.FORBIDDEN

    method = methods.get(method_request.method)
    if not method:
        return f'method "{method_request.method}" not allowed', HTTPStatus.UNPROCESSABLE_ENTITY

    ctx['is_admin'] = method_request.is_admin

    return method(method_request.arguments, ctx, store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, HTTPStatus.OK
        context = {"request_id": self.get_request_id(self.headers)}

        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string.decode('utf-8'))
        except Exception as e:
            logging.error(e)
            code = HTTPStatus.BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" %
                         (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception(f"Unexpected error: {e}")
                    code = HTTPStatus.UNPROCESSABLE_ENTITY
            else:
                code = HTTPStatus.NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(
                code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)

        self.wfile.write(json.dumps(r).encode('utf-8'))


if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument(
        "-p", "--port", action="store", type=int, default=8080)
    ap.add_argument("-l", "--log", action="store", default=None)
    args = ap.parse_args()

    logging.basicConfig(filename=args.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", args.port), MainHTTPHandler)

    logging.info("Starting server at %s" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
