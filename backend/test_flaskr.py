import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_HOST = os.getenv('DB_HOST', 'localhost:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
        self.DB_NAME = os.getenv('DB_NAME', 'trivia')
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "In what year was the last World Cup?",
            "answer": "2018",
            "difficulty": 2,
            "category": 6
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation,
    and for expected errors.
    """
    # Test for endpoints that handles GET requests for all available
    # categories.

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(isinstance(data["categories"], dict))

    def test_404_requesting_unknown_category(self):
        res = self.client().get("/categories/1000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not find the resource")

    # Test for endpoints that handles GET requests for questions

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(isinstance(data["questions"], list))
        self.assertTrue(isinstance(data["categories"], dict))
        # self.assertTrue(data["current_category"])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not find the resource")

    # Test for endpoints to DELETE a question using a question ID.
    # A question is deleted from the database in each attempt.

    def test_delete_question(self):
        question_id = (Question.query.first().format())["id"]
        res = self.client().delete("/questions/" + str(question_id))
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question_id
        ).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(question, None)

    def test_422_if_question_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not process the resource")

    # Test for endpoints that handles POST requests to create a new question,
    # and POST request to get questions based on a search term.

    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "What"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["current_category"])
        self.assertTrue(isinstance(data["questions"], list))

    def test_get_search_question_without_results(self):
        res = self.client().post("/questions",
                                 json={"searchTerm": "para parece que no"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(isinstance(data["questions"], list))
        self.assertTrue(data["current_category"])

    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_get_400_search_or_create_question_with_noInput(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    # Test for POST endpoints that gets questions based on category.

    def test_get_questions_basedOn_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["current_category"])
        self.assertTrue(isinstance(data["questions"], list))

    def test_404_requesting_question_unknown_category(self):
        res = self.client().get("/categories/10000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not find the resource")

    # Test POST endpoints that gets questions to play the quiz.

    def test_get_quiz_question(self):
        res = self.client().post('/quizzes', json={
            "previous_questions": [1, 3, 18],
            "quiz_category": {
                "id": 5,
                "type": "Science"
            }
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_get_400_retrieve_question_with_noInput(self):
        res = self.client().post("/quizzes")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not find the resource")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
