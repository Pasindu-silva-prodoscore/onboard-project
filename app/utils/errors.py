from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": error.description}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"error": "Unauthorized", "message": error.description}), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": error.description}), 404