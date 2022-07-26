import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql import func

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def dictionary_categories(selection):
    categories = [category.format() for category in selection]
    data = {}
    for category in categories:
        data.update(category)

    return data


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route("/")
    def index():
        return jsonify("Welcome to destiny erhabor udacity project")

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def all_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_list = dictionary_categories(categories)

        if len(categories_list) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": categories_list
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        categories_list = dictionary_categories(categories)
        # pagination
        questions_list = paginate_questions(request, questions)

        if len(questions_list) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": questions_list,
            "categories":  categories_list,
            "total_questions": len(Question.query.all()),
            "current_category": "History"
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            body = Question.query.filter(
                Question.id == question_id).one_or_none()
            if body is None:
                abort(404)
            body.delete()

            selected_question = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selected_question)

            return jsonify({
                "success": True,
                "question": current_question,
                "delete": question_id,
                "total_questions": len(Question.query.all()),
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions", methods=["POST"])
    def search_or_create_question():

        try:
            body = request.get_json()

            new_question = body.get("question", None)
            new_answer = body.get("answer", None)
            new_difficulty = body.get("difficulty", None)
            new_category = body.get("category", None)
            search = body.get("searchTerm", None)
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                questions = [question.format() for question in selection]

                return jsonify(
                    {
                        "success": True,
                        "questions": questions,
                        "total_questions": len(selection.all()),
                        "current_category": "Placeholder"
                    }
                )
            elif new_question:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    difficulty=new_difficulty,
                    category=new_category)
                question.insert()

                return jsonify(
                    {
                        "success": True,
                    }
                )

        except BaseException:
            abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        try:
            questions_by_category = Question.query.order_by(Question.id).filter(
                Question.category == category_id
            )
            questions = [questions_by_category.format()
                         for questions_by_category in questions_by_category]

            if len(questions) == 0:
                abort(404)

            return jsonify({
                "success": True,
                "questions": questions,
                "total_questions": len(Question.query.all()),
                "current_category": "Placeholder"
            })
        except BaseException:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()

        try:
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            if previous_questions is None:
                abort(404)

            # Fetch all the questions if category is not specified
            if quiz_category == None or quiz_category['id'] == 0:
                questions = Question.query.all()
            else:
                # Fetch questions based on category
                questions = Question.query.filter_by(
                    category=quiz_category['id']).all()

            # Filter out the previous_questions
            available_questions = filter(
                lambda q: q.id not in previous_questions, questions)
            available_questions = list(available_questions)

            if len(available_questions) == 0:
                return jsonify({
                    "success": False,
                    "message": 'No questions available'
                })

            # Choose a random question from the available questions
            random_question = random.choice(available_questions).format()

            return jsonify({
                "success": True,
                "question": random_question
            })
        except:
            abort(404)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Could not find the resource"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Could not process the resource"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({"success": False, "error": 500,
                    "message": "internal server error"})), 500

    return app
