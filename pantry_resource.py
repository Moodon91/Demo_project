from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional

from models.pantry import Pantry

from schemas.pantryschema import PantrySchema

pantry_schema = PantrySchema()
pantry_list_schema = PantrySchema(many=True)

'#Using GET, get a list of pantry ingredients'
'#Using POST, create a new pantry'


class PantryListResource(Resource):

    def get(self):

        pantries = Pantry.get_all_published()

        return pantry_list_schema.dump(pantries).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()

        data, errors = pantry_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        pantry = Pantry(**data)
        pantry.user_id = current_user
        pantry.save()

        return pantry_schema.dump(pantry).data, HTTPStatus.CREATED

    @jwt_required
    def patch(self, pantry_id):

        json_data = request.get_json()

        data, errors = pantry_schema.load(data=json_data, partial=('name',))
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        pantry = Pantry.get_by_id(pantry_id=pantry_id)
        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != pantry.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        pantry.name = data.get('name') or pantry.name
        pantry.dry = data.get('dry') or pantry.dry
        pantry.fridge = data.get('fridge') or pantry.fridge
        pantry.freezer = data.get('freezer') or pantry.freezer

        pantry.save()

        return pantry_schema.dump(pantry).data, HTTPStatus.OK


'#Using GET, get a specific pantry'
'#Using PUT, update an pantry'
'#Using DELETE, delete an pantry'


class PantryResource(Resource):

    @jwt_optional
    def get(self, pantry_id):
        pantry = Pantry.get_by_id(pantry_id=pantry_id)

        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if pantry.is_publish is False and pantry.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return pantry_schema.dump(pantry).data, HTTPStatus.OK

    @jwt_required
    def put(self, pantry_id):
        json_data = request.get_json()

        pantry = Pantry.get_by_id(pantry_id=pantry_id)

        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != pantry.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        pantry.name = json_data['name']
        pantry.dry = json_data['dry']
        pantry.fridge = json_data['fridge']
        pantry.freezer = json_data['freezer']

        pantry.save()

        return pantry_schema.dump(pantry).data, HTTPStatus.OK

    @jwt_required
    def delete(self, pantry_id):
        pantry = Pantry.get_by_id(pantry_id=pantry_id)

        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != pantry.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        pantry.delete()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def patch(self, pantry_id):

        json_data = request.get_json()

        data, errors = pantry_schema.load(data=json_data, partial=('name',))
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        pantry = Pantry.get_by_id(pantry_id=pantry_id)
        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != pantry.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        pantry.name = data.get('name') or pantry.name
        pantry.dry = data.get('dry') or pantry.dry
        pantry.fridge = data.get('fridge') or pantry.fridge
        pantry.freezer = data.get('freezer') or pantry.freezer

        pantry.save()

        return pantry_schema.dump(pantry).data, HTTPStatus.OK


'#Making pantries public or not-public'


class PantryPublic(Resource):

    @jwt_required
    def put(self, pantry_id):
        pantry = Pantry.get_by_id(pantry_id=pantry_id)

        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != pantry.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        pantry.is_publish = True
        pantry.save()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def delete(self, pantry_id):

        pantry = Pantry.get_by_id(pantry_id=pantry_id)

        if pantry is None:
            return {'message': 'Pantry not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != pantry.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        pantry.is_publish = False
        pantry.save()

        return {}, HTTPStatus.NO_CONTENT
