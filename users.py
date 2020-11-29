from flask import request, url_for, render_template
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
import os

from webargs import fields
from webargs.flaskparser import use_kwargs

from models.recipes import Recipe
from models.user import User
from models.pantry import Pantry

from mailgun import MailgunApi
from utils import generate_token, verify_token


from schemas.userschema import UserSchema
from schemas.recipeschema import RecipeSchema
from schemas.pantryschema import PantrySchema


recipe_list_schema = RecipeSchema(many=True)
pantry_list_schema = PantrySchema(many=True)

mailgun = MailgunApi(domain=os.environ.get('MAILGUN_DOMAIN'),
                     api_key=os.environ.get('MAILGUN_API_KEY'))

# When a not authenticated user accesses other people's /users/<username> endpoint, the email
# address will be hidden
user_schema = UserSchema()
user_public_schema = UserSchema(exclude=('email',))


class UserListResource(Resource):
    def post(self):
        json_data = request.get_json()

        data, errors = user_schema.load(data=json_data)
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        if User.get_by_username(data.get('username')):
            return {'message': 'username already taken'}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(data.get('email')):
            return {'message': 'email already taken'}, HTTPStatus.BAD_REQUEST

        user = User(**data)
        user.save()

        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration'

        link = url_for('useractivateresource', token=token, _external=True)

        text = 'Terve terve tervaperse! Teeppä niiku Michael Jackson ja paina nappulaa: {}'.format(link)

        mailgun.send_email(to=user.email, subject=subject, text=text, html=render_template('email/confirmation.html',
                                                                                           link=link))

        return user_schema.dump(user).data, HTTPStatus.CREATED


class UserResource(Resource):

    @jwt_optional
    def get(self, username):
        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'user not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user == user.id:
            data = user_schema.dump(user).data

        else:
            data = user_public_schema.dump(user).data

        return data, HTTPStatus.OK


'#/users/me will allow to get authenticated user information back using the access_token'


class MeResource(Resource):

    @jwt_required
    def get(self):
        user = User.get_by_id(id=get_jwt_identity())
        return user_schema.dump(user).data, HTTPStatus.OK


class UserRecipeListResource(Resource):

    @jwt_optional
    @use_kwargs({'visibility': fields.Str(missing='public')})
    def get(self, username, visibility):

        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'

        recipes = Recipe.get_all_by_user(user_id=user.id, visibility=visibility)

        return recipe_list_schema.dump(recipes).data, HTTPStatus.OK


class UserPantryListResource(Resource):

    @jwt_optional
    @use_kwargs({'visibility': fields.Str(missing='public')})
    def get(self, username, visibility):

        user = User.get_by_username(username=username)

        if user is None:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'

        pantries = Pantry.get_all_by_user(user_id=user.id, visibility=visibility)

        return pantry_list_schema.dump(pantries).data, HTTPStatus.OK


class UserActivateResource(Resource):
    def get(self, token):

        email = verify_token(token, salt='activate')
        if email is False:
            return {'message': 'Invalid token or token expired'}, HTTPStatus.BAD_REQUEST

        user = User.get_by_email(email=email)
        if not user:
            return {'message': 'User not found'}, HTTPStatus.NOT_FOUND

        if user.is_active is True:
            return {'message': 'The user account is already activated'}, HTTPStatus.BAD_REQUEST

        user.is_active = True

        user.save()

        return {}, HTTPStatus.NO_CONTENT
