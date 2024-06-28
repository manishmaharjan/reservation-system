from inspect import getmembers, isfunction

from flasgger import Swagger, swag_from
from flask import Flask, jsonify, request
from marshmallow import Schema, fields  # Add marshmallow for data validation

app = Flask(__name__)
Swagger(app)

# Import your API endpoints from a separate file
from api import api  # Assume `api` is the Flask-RESTful API instance


def get_api_specs():
    """
    Inspects API resources and extracts details for Swagger spec.
    Utilizes Flask-RESTful's `url_for` and marshmallow for schema extraction.
    """
    specs = {}
    for endpoint, resource in api.endpoints.items():
        view_func = resource.view_class
        specs[endpoint] = {
            "description": view_func.__doc__ if view_func.__doc__ else "",
            "parameters": [],  # Initialize parameters list
            "responses": {},  # Initialize responses dictionary
        }

        # Extract request parameters using Flask-RESTful's `url_for` (consider decorator-based approach for clarity)
        for view_args in resource.view_class.decorators:
            if hasattr(view_args, "view_class"):  # Check for Flask-RESTful decorators
                view_class = view_args.view_class  # Access the decorated view class
                for method_name, view_method in getmembers(view_class, isfunction):
                    if (
                        method_name == "get"
                        or method_name == "post"
                        or method_name == "put"
                        or method_name == "delete"
                    ):
                        # Construct the URL for the specific method and endpoint
                        url = app.url_map.bind("localhost").build(
                            endpoint, **view_args.kwargs
                        )
                        for arg_name, arg in getmembers(
                            view_method.__annotations__, isfunction
                        ):
                            if arg_name != "return":
                                specs[endpoint]["parameters"].append(
                                    {
                                        "in": (
                                            "path"
                                            if arg in view_args.kwargs
                                            else "query"
                                        ),  # Determine parameter location (path or query)
                                        "name": arg_name,
                                        "type": arg.__name__,  # Use Marshmallow field type if applicable
                                        "required": (
                                            True
                                            if arg not in view_args.kwargs
                                            else False
                                        ),  # Set required based on kwargs
                                        "description": (
                                            arg.__doc__ if arg.__doc__ else ""
                                        ),  # Include docstring if available
                                    }
                                )

        # Extract response schema using marshmallow (if applicable)
        if hasattr(view_class, "schema"):
            schema = view_class.schema
            if isinstance(schema, Schema):
                specs[endpoint]["responses"]["200"] = {
                    "description": "Successful operation",
                    "schema": schema.dump(),  # Convert schema to a dictionary
                }

    return specs


# Assuming a base path for your API (adjust as needed)
app.config["SWAGGER"] = {
    "title": "Reservation System API Documentation",
    "version": "1.0",
    "specs": get_api_specs(),
}


@swag_from(
    "swagger.yml"
)  # Replace with actual path to your swagger config file if needed
@app.route("/api-docs")
def api_documentation():
    """
    Serves the generated Swagger UI documentation
    """
    return jsonify(app.config["SWAGGER"])


if __name__ == "__main__":
    app.run(debug=True)


# from flask import Flask
# from flasgger import Swagger
# from .api import Api

# app = Flask(__name__, static_folder="static")
# app.config["SWAGGER"] = {
#     "title": "Sensorhub API",
#     "uiversion": 3,
#     "doc_dir": "./doc",
# }

# swagger = Swagger(app)
# #swagger = Swagger(app, template_file="doc/base.yml")

# from flask import Flask, jsonify, request
# from flasgger import Swagger, swag_from
# from api import Api

# app = Flask(__name__, static_folder="static")
# app.config["SWAGGER"] = {
#     "title": "Sensorhub API",
#     "uiversion": 3,
#     "doc_dir": "./doc",
# }

# swagger = Swagger(app)

# api = Api(app)

# @app.route('/api/some_endpoint', methods=['POST'])
# @swag_from('doc/some_endpoint.yml')
# def some_endpoint():
#     """
#     This is using docstrings for specifications
#     ---
#     parameters:
#       - name: some_param
#         in: query
#         type: string
#         required: true
#     responses:
#       200:
#         description: Success
#     """
#     some_param = request.args.get('some_param')
#     return jsonify({'result': 'Success', 'param': some_param})

# if __name__ == '__main__':
#     app.run(debug=True)
