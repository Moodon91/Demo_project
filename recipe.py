from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional

from models.recipes import Recipe

from schemas.recipeschema import RecipeSchema

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)

'#Using GET, get a list of public recipes'
'#Using POST, create a new recipe'


class RecipeListResource(Resource):

    def get(self):

        recipes = Recipe.get_all_published()

        return recipe_list_schema.dump(recipes).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()

        data, errors = recipe_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        recipe = Recipe(**data)
        recipe.user_id = current_user
        recipe.save()

        return recipe_schema.dump(recipe).data, HTTPStatus.CREATED

    @jwt_required
    def patch(self, recipe_id):

        json_data = request.get_json()

        data, errors = recipe_schema.load(data=json_data, partial=('name',))
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.duration = data.get('duration') or recipe.duration
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.directions = data.get('directions') or recipe.directions
        recipe.cost = data.get('cost') or recipe.cost

        recipe.save()

        return recipe_schema.dump(recipe).data, HTTPStatus.OK


'#Using GET, get a specific recipe'
'#Using PUT, update an recipe'
'#Using DELETE, delete an recipe'


class RecipeResource(Resource):

    @jwt_optional
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if recipe.is_publish == False and recipe.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def put(self, recipe_id):
        json_data = request.get_json()

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = json_data['name']
        recipe.description = json_data['description']
        recipe.num_of_servings = json_data['num_of_servings']
        recipe.ingredients = json_data['ingredients']
        recipe.directions = json_data['directions']
        recipe.cost = json_data['cost']
        recipe.duration = json_data['duration']

        recipe.save()

        return recipe_schema.dump(recipe).data, HTTPStatus.OK

    @jwt_required
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.delete()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def patch(self, recipe_id):

        json_data = request.get_json()

        data, errors = recipe_schema.load(data=json_data, partial=('name',))
        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        recipe = Recipe.get_by_id(recipe_id=recipe_id)
        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.name = data.get('name') or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.duration = data.get('duration') or recipe.duration
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.ingredients = data.get('ingredients') or recipe.ingredients
        recipe.directions = data.get('directions') or recipe.directions
        recipe.cost = data.get('cost') or recipe.cost

        recipe.save()

        return recipe_schema.dump(recipe).data, HTTPStatus.OK


'#Making recipes public or not-public'


class RecipePublic(Resource):

    @jwt_required
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = True
        recipe.save()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def delete(self, recipe_id):

        recipe = Recipe.get_by_id(recipe_id=recipe_id)

        if recipe is None:
            return {'message': 'Recipe not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != recipe.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        recipe.is_publish = False
        recipe.save()

        return {}, HTTPStatus.NO_CONTENT
