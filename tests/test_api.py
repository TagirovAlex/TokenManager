import pytest
import os
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app, db
from app.models import Category, Object, Template, TemplateItem, TemplateResult


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class TestCategoryAPI:
    def test_get_categories_empty(self, client):
        response = client.get('/api/categories')
        assert response.status_code == 200
        assert response.json == []
    
    def test_create_category(self, client):
        data = {
            'name': 'character',
            'display_name': 'Персонаж',
            'description': 'Люди и существа'
        }
        response = client.post('/api/categories', json=data)
        assert response.status_code == 201
        assert response.json['name'] == 'character'
        assert response.json['display_name'] == 'Персонаж'
    
    def test_create_category_duplicate_name(self, client):
        data = {'name': 'character', 'display_name': 'Персонаж'}
        client.post('/api/categories', json=data)
        
        response = client.post('/api/categories', json=data)
        assert response.status_code == 400
    
    def test_create_category_missing_required(self, client):
        response = client.post('/api/categories', json={'name': 'test'})
        assert response.status_code == 400
    
    def test_get_category_by_id(self, client):
        create_resp = client.post('/api/categories', 
            json={'name': 'character', 'display_name': 'Персонаж'})
        cat_id = create_resp.json['id']
        
        response = client.get(f'/api/categories/{cat_id}')
        assert response.status_code == 200
        assert response.json['name'] == 'character'
    
    def test_update_category(self, client):
        create_resp = client.post('/api/categories', 
            json={'name': 'character', 'display_name': 'Персонаж'})
        cat_id = create_resp.json['id']
        
        response = client.put(f'/api/categories/{cat_id}', 
            json={'display_name': 'Человек'})
        assert response.status_code == 200
        assert response.json['display_name'] == 'Человек'
    
    def test_delete_category(self, client):
        create_resp = client.post('/api/categories', 
            json={'name': 'character', 'display_name': 'Персонаж'})
        cat_id = create_resp.json['id']
        
        response = client.delete(f'/api/categories/{cat_id}')
        assert response.status_code == 200
        
        get_resp = client.get(f'/api/categories/{cat_id}')
        assert get_resp.status_code == 404


class TestObjectAPI:
    @pytest.fixture
    def category(self, client):
        resp = client.post('/api/categories', 
            json={'name': 'character', 'display_name': 'Персонаж'})
        return resp.json['id']
    
    def test_get_objects_empty(self, client):
        response = client.get('/api/objects')
        assert response.status_code == 200
        assert response.json == []
    
    def test_create_object(self, client, category):
        data = {
            'category_id': category,
            'name': 'Воин',
            'description': 'Сильный воин',
            'prompt': 'warrior, armored, sword'
        }
        response = client.post('/api/objects', json=data)
        assert response.status_code == 201
        assert response.json['name'] == 'Воин'
        assert response.json['prompt'] == 'warrior, armored, sword'
    
    def test_create_object_missing_required(self, client, category):
        response = client.post('/api/objects', json={'name': 'test'})
        assert response.status_code == 400
    
    def test_get_objects_by_category(self, client, category):
        client.post('/api/objects', json={
            'category_id': category, 'name': 'obj1', 'prompt': 'p1'})
        
        response = client.get(f'/api/objects?category_id={category}')
        assert response.status_code == 200
        assert len(response.json) == 1
    
    def test_update_object(self, client, category):
        create_resp = client.post('/api/objects', json={
            'category_id': category, 'name': 'Воин', 'prompt': 'warrior'})
        obj_id = create_resp.json['id']
        
        response = client.put(f'/api/objects/{obj_id}', 
            json={'prompt': 'warrior, strong'})
        assert response.status_code == 200
        assert response.json['prompt'] == 'warrior, strong'
    
    def test_delete_object(self, client, category):
        create_resp = client.post('/api/objects', json={
            'category_id': category, 'name': 'obj', 'prompt': 'p'})
        obj_id = create_resp.json['id']
        
        response = client.delete(f'/api/objects/{obj_id}')
        assert response.status_code == 200


class TestTemplateAPI:
    @pytest.fixture
    def category(self, client):
        resp = client.post('/api/categories', 
            json={'name': 'character', 'display_name': 'Персонаж'})
        return resp.json['id']
    
    @pytest.fixture
    def obj(self, client, category):
        resp = client.post('/api/objects', json={
            'category_id': category, 'name': 'warrior', 'prompt': 'warrior'})
        return resp.json['id']
    
    def test_create_template(self, client):
        data = {
            'name': 'Warrior in location',
            'description': 'Персонаж в локации',
            'template_text': '{char} stands in {loc}'
        }
        response = client.post('/api/templates', json=data)
        assert response.status_code == 201
        assert response.json['name'] == 'Warrior in location'
    
    def test_create_template_with_items(self, client, obj):
        data = {
            'name': 'Test template',
            'template_text': '{obj}',
            'items': [
                {'object_id': obj, 'position': 0, 'custom_text': 'идет'}
            ]
        }
        response = client.post('/api/templates', json=data)
        assert response.status_code == 201
        assert len(response.json['items']) == 1
    
    def test_get_template_items(self, client, obj):
        template_resp = client.post('/api/templates', json={
            'name': 'Test', 'template_text': '{obj}',
            'items': [{'object_id': obj, 'position': 0}]})
        tmpl_id = template_resp.json['id']
        
        response = client.get(f'/api/templates/{tmpl_id}/items')
        assert response.status_code == 200
        assert len(response.json) == 1


class TestGeneratorAPI:
    @pytest.fixture
    def category(self, client):
        resp = client.post('/api/categories', 
            json={'name': 'character', 'display_name': 'Персонаж'})
        return resp.json['id']
    
    @pytest.fixture
    def obj(self, client, category):
        resp = client.post('/api/objects', json={
            'category_id': category, 'name': 'warrior', 'prompt': 'warrior'})
        return resp.json['id']
    
    @pytest.fixture
    def template(self, client, obj):
        resp = client.post('/api/templates', json={
            'name': 'Test', 'template_text': '{obj}',
            'items': [{'object_id': obj, 'position': 0}]})
        return resp.json['id']
    
    def test_generate_prompt(self, client, template, obj):
        response = client.post('/api/generate', json={
            'template_id': template,
            'items': [{'object_id': obj, 'custom_text': 'идет'}]
        })
        assert response.status_code == 200
        assert 'warrior' in response.json['generated_prompt']
        assert 'warrior идет' in response.json['generated_prompt']
    
    def test_generate_with_save_result(self, client, template, obj):
        response = client.post('/api/generate', json={
            'template_id': template,
            'items': [{'object_id': obj}],
            'save_result': True
        })
        assert response.status_code == 200
        assert 'result_id' in response.json
    
    def test_get_results(self, client, template, obj):
        client.post('/api/generate', json={
            'template_id': template,
            'items': [{'object_id': obj}],
            'save_result': True})
        
        response = client.get('/api/generate/results')
        assert response.status_code == 200
        assert len(response.json) == 1


class TestAdminAPI:
    def test_get_stats_empty(self, client):
        response = client.get('/api/admin/stats')
        assert response.status_code == 200
        assert response.json['categories'] == 0
        assert response.json['objects'] == 0
    
    def test_get_stats_with_data(self, client):
        client.post('/api/categories', 
            json={'name': 'char', 'display_name': 'Персонаж'})
        client.post('/api/categories', 
            json={'name': 'loc', 'display_name': 'Локация'})
        
        response = client.get('/api/admin/stats')
        assert response.status_code == 200
        assert response.json['categories'] == 2
