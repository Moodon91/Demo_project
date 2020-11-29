from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from config import Config
from extensions import db, jwt
from resources.users import UserListResource, UserResource, MeResource, UserRecipeListResource, UserPantryListResource
from resources.users import  UserActivateResource
from resources.recipe import RecipeListResource, RecipeResource, RecipePublic
from resources.token import TokenResource, RefreshResource, RevokeResource, black_list
from resources.pantry_resource import PantryListResource, PantryResource, PantryPublic


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.app_context().push()

    register_extensions(app)
    register_resources(app)

    return app


def register_extensions(app):
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt.init_app(app)

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return jti in black_list


def register_resources(app):
    api = Api(app)

    api.add_resource(UserListResource, '/users')
    api.add_resource(UserResource, '/users/<string:username>')
    api.add_resource(UserRecipeListResource, '/users/<string:username>/recipes')
    api.add_resource(UserPantryListResource, '/users/<string:username>/pantry')
    api.add_resource(UserActivateResource, '/users/activate/<string:token>')
    api.add_resource(MeResource, '/me')
    api.add_resource(RecipeListResource, '/recipes')
    api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
    api.add_resource(RecipePublic, '/recipes/<int:recipe_id>/publish')
    api.add_resource(TokenResource, '/token')
    api.add_resource(RefreshResource, '/refresh')
    api.add_resource(RevokeResource, '/revoke')
    api.add_resource(PantryListResource, '/pantry')
    api.add_resource(PantryResource, '/pantry/<int:pantry_id>')
    api.add_resource(PantryPublic, '/pantry/<int:pantry_id>/publish')


if __name__ == '__main__':
    app = create_app()
    app.run()
