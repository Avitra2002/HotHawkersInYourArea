import os
from flask import Blueprint

def register_blueprints(app):
    """Dynamically import and register blueprints."""
    for file in os.listdir(os.path.dirname(__file__)):
        if file.endswith('.py') and file != '__init__.py':
            module_name = file[:-3]  # Remove .py extension
            module = __import__(f'routes.{module_name}', fromlist=['*'])
            blueprint = getattr(module, f"{module_name}_bp", None)
            if isinstance(blueprint, Blueprint):
                app.register_blueprint(blueprint)