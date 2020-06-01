import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  @app.after_request
  def after_request(response):
    response.headers.add("Access-Control-Allow-Headers","Content-Type, Authoraization, true")
    response.headers.add("Access-Control-Allow-Methods","GET, POST, PATCH, PUT, DELETE, OPTIONS")
    return response
  

  #--------------------------------------------------------------
  #GET Endpoints
  #--------------------------------------------------------------
  
  #Get all categories
  @app.route("/categories")
  def get_categories():
    categories = Category.query.order_by(Category.id).all()
    Formated_Categories = {category.id:category.type for category in categories}

    return jsonify({
      "categories":Formated_Categories,
      "success":True
    })

  #Get all questions with pagination
  @app.route("/questions")
  def get_questions():
    page = request.args.get("page",1,type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    categories = Category.query.order_by(Category.id).all()
    Formated_Categories = {category.id:category.type for category in categories}
    questions = Question.query.all()
    Formated_Questions = [question.format() for question in questions]
    
    return jsonify({
      "questions":Formated_Questions[start:end],
      "total_questions":len(Formated_Questions),
      "categories":Formated_Categories,
      "current_category":None,
      "success":True
    })
  
  #Get all questions for specific category
  @app.route("/categories/<int:category_id>/questions")
  def get_category_questions(category_id):
    page = request.args.get("page",1,type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    questions = Question.query.filter_by(category=category_id).all()
    Formated_questions = [question.format() for question in questions]
    return jsonify({
      "questions":Formated_questions[start:end],
      "total_questions":len(Formated_questions),
      "current_category":Category.query.get(category_id).format(),
      "success":True
    })

  #--------------------------------------------------------------
  #POST Endpoints
  #--------------------------------------------------------------

  #Add new question
  @app.route("/questions",methods=['POST'])
  def add_question():
    body = request.get_json()
    if body is None:
      abort(400)
    question_text = body.get("question",None)
    answer = body.get("answer",None)
    category = body.get("category",None)
    difficulty = body.get("difficulty",None)
    try:
      question = Question(question=question_text,answer=answer,category=category,difficulty=difficulty)
      question.insert()
      
      return jsonify({
        "success":True,
        "created":question.id
      })
    except:
      abort(422)

  #Search for questions with specific word
  @app.route("/questions/search",methods=['POST'])
  def search_questions():
    page = request.args.get("page",1,type=int)
    start = (page-1)*QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE
    body = request.get_json()
    if body is None:
      abort(400)
    search_word = body.get("searchTerm")
    questions = Question.query.filter(Question.question.ilike(f"%{search_word}%"))
    Formated_questions= [question.format() for question in questions]

    return jsonify({
      "questions":Formated_questions[start:end],
      "total_questions":len(Formated_questions),
      "current_category":None,
      "success":True
    })  

  #Play a quiz with specific category or all categories
  @app.route("/quizzes",methods=['POST'])
  def play_quiz():
    body = request.get_json()
    if body is None :
      abort(400)
    previous_questions = body.get("previous_questions")
    quiz_category = body.get("quiz_category")
    questions = []
    non_played_question=None
    
    if quiz_category['id']==0:
      questions = Question.query.all()
    else:
      questions = Question.query.filter_by(category=quiz_category['id']).all()

    #make sure no repeted question , also check if we reach the final question and finish the game
    if not previous_questions:
      random_index = random.randrange(0,len(questions))
      non_played_question=questions[random_index].format()
    elif previous_questions and len(previous_questions)==len(questions):
      non_played_question=None
    else:
      for question in questions:
        if question.id not in previous_questions:
          non_played_question = question.format()
          break
          
    return jsonify({
      "previousQuestions":previous_questions,
      "question":non_played_question,
      "success":True
    })

  #--------------------------------------------------------------
  #Delete Endpoint
  #--------------------------------------------------------------
  
  @app.route("/questions/<int:question_id>",methods=["DELETE"])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      if question is None:
        abort(404)

      question.delete()
      return jsonify({
        "success":True,
        "deleted":question_id
        })
    except:
      abort(422)    

  #--------------------------------------------------------------
  #Error Handlers
  #--------------------------------------------------------------
  @app.errorhandler(404)
  def not_found(error):

    return jsonify({
      "success":False,
      "message":"resource not found",
      "error":404
    }),404

  @app.errorhandler(422)
  def unprocessable(error):

    return jsonify({
      "success":False,
      "message":"unprocessable",
      "error":422
    }),422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success":False,
      "message":"bad request",
      "error":400
    }),400 

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success":False,
      "message":"method not allowed",
      "error":405
    }),405   

  return app

    