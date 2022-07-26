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
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    
    @app.route("/")
    def index():
        return jsonify("Welcome to destiny erhabor udacity project")

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def all_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_list = dictionary_categories(categories)
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
    @app.route("/questions", methods=["GET"])
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
            body = Question.query.filter(Question.id == question_id).one_or_none()
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
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    @app.route("/questions", methods=['POST'])
    def create_questions():
        body = request.get_json()
        
        question = body.get('question')
        answer = body.get('answer')
        category = body.get('category')
        difficulty = body.get('difficulty')
        
        try:
            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            question.insert()
            
            selected_question = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selected_question)
            
            return jsonify({
                "success": True,
                "created": question.id,
                "question": current_question,
                "total_questions": len(Question.query.all())            
            })
        except :
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions/search", methods=['POST'])
    def search_question():
        search_term = request.get_json().get('search')
        try:
            searched_questions = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%' + search_term + '%')
            ).all()
            if search_question == None:
                abort(404)
            formatted_searched_questions = [searched_question.format() for searched_question in searched_questions]
            
            return jsonify({
                "success": True,
                "search_questions": formatted_searched_questions
            })
        except:
            abort(500)

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
            formatted_question_by_category = [questions_by_category.format() for questions_by_category in questions_by_category]
            
            if formatted_question_by_category == []:
                abort(404)
            
            return jsonify({
                "success": True,
                "category": category_id,
                "questions": formatted_question_by_category,
                "total_questions": len(Question.query.all()),
                "current_category": "Placeholder"
            })                        
        except:
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
    
    @app.route("/quizzes", methods=["POST"])
    def retrieve_random_question():
        try:
            body = request.get_json()

            past_questions = body.get("previous_questions", None)
            quiz_category = body.get("quiz_category", None)
            category_id = quiz_category["id"]

            if category_id == 0:
                rand_selection = Question.query.order_by(func.random())
                selection = rand_selection.filter(
                    Question.id.not_in(past_questions)).first()

                if selection is not None:
                    question = selection.format()
                    return jsonify(
                        {
                            "success": True,
                            "question": question,
                        }
                    )
                return jsonify(
                    {
                        "question": None,
                    }
                )
            else:
                rand_selection = Question.query.order_by(func.random())
                selection = rand_selection.filter(
                    Question.category == category_id,
                    Question.id.not_in(past_questions)).first()

                if selection is not None:
                    question = selection.format()
                    return jsonify(
                        {
                            "success": True,
                            "question": question,
                        }
                    )
                return jsonify(
                    {
                        "question": None,
                    }
                )
        except BaseException:
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
        }, 404)
        
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message":"Could not process the resource"
        }, 422)
        
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"success": False, "error": 400,
                    "message": "bad request"}),
            400,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({"success": False, "error": 500,
                    "message": "internal server error"}),
            500,
        )

    return app