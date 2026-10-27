import logging
import traceback
from flask import render_template, request, jsonify

from werkzeug.exceptions import HTTPException

logger = logging.getLogger('mysterymart.errors')


class MysteryMartConcurrencyError(HTTPException):
    """Documented custom application error: 460 Unboxing Concurrency Exception."""
    code = 460
    description = 'MysteryMart Inventory Concurrency Conflict: The last surprise box in this batch was secured by another customer.'


def wants_json() -> bool:
    """Detect if client expects a JSON error response."""
    return (
        request.path.startswith('/api/') or
        request.is_json or
        request.headers.get('Accept') == 'application/json' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )


def register_error_handlers(app):
    """Register custom error handlers for all required HTTP and application codes."""

    @app.errorhandler(400)
    def bad_request_error(error):
        logger.warning("HTTP 400 Bad Request at %s", request.path)
        if wants_json():
            return jsonify({
                'error': 'Bad Request',
                'status_code': 400,
                'message': 'The server could not understand your request.'
            }), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(401)
    def unauthorized_error(error):
        logger.warning("HTTP 401 Unauthorized at %s", request.path)
        if wants_json():
            return jsonify({
                'error': 'Unauthorized',
                'status_code': 401,
                'message': 'Authentication is required to access this resource.'
            }), 401
        return render_template('errors/401.html', error=error), 401

    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning("HTTP 403 Forbidden at %s", request.path)
        if wants_json():
            return jsonify({
                'error': 'Forbidden',
                'status_code': 403,
                'message': 'Access to this resource is prohibited.'
            }), 403
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        logger.info("HTTP 404 Not Found at %s", request.path)
        if wants_json():
            return jsonify({
                'error': 'Not Found',
                'status_code': 404,
                'message': f"The requested resource '{request.path}' was not found on MysteryMart."
            }), 404
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(429)
    def rate_limit_error(error):
        logger.warning("HTTP 429 Rate Limit Exceeded at %s from IP %s", request.path, request.remote_addr)
        if wants_json():
            return jsonify({
                'error': 'Too Many Requests',
                'status_code': 429,
                'message': 'Rate limit exceeded. Please wait 60 seconds before retrying.'
            }), 429
        return render_template('errors/429.html', error=error), 429

    @app.errorhandler(MysteryMartConcurrencyError)
    def mysterymart_custom_error(error):
        """
        Documented Custom Application Status Code 460:
        MysteryMart Unboxing Concurrency / Stock Allocation Conflict.
        Indicates that inventory was claimed by another customer during the checkout transaction.
        """
        logger.warning("Custom 460 Unboxing Concurrency Exception at %s", request.path)
        if wants_json():
            return jsonify({
                'error': 'MysteryMart Inventory Concurrency Conflict',
                'status_code': 460,
                'is_custom_application_code': True,
                'documentation': 'HTTP 460 is a MysteryMart proprietary application status code denoting an unboxing race condition where stock depleted during final checkout confirmation.',
                'message': 'The last surprise box in this batch was secured by another customer just moments ago.'
            }), 460
        return render_template('errors/460.html', error=error), 460

    @app.errorhandler(500)
    def internal_server_error(error):
        # Record full technical diagnostic traceback safely on the server log
        logger.error(
            "HTTP 500 Internal Server Error at %s: %s\n%s",
            request.path,
            str(error),
            traceback.format_exc()
        )
        if wants_json():
            return jsonify({
                'error': 'Internal Server Error',
                'status_code': 500,
                'message': 'A server-side error occurred. Our engineers have been alerted.'
            }), 500
        # Return friendly user-facing page with NO credentials, stack traces, or internal paths
        return render_template('errors/500.html', error=error), 500

    @app.errorhandler(503)
    def service_unavailable_error(error):
        logger.warning("HTTP 503 Service Unavailable at %s", request.path)
        if wants_json():
            return jsonify({
                'error': 'Service Unavailable',
                'status_code': 503,
                'message': 'MysteryMart service is temporarily undergoing scheduled maintenance.'
            }), 503
        return render_template('errors/503.html', error=error), 503
