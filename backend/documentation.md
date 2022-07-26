## TRIVIA API Documentation 

### Error Handling

Errors are returned as JSON objects in the following format:

```
{
    "success": False,
    "error": 404,
    "message": "resource not found"
}
```

The API will return three error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable
- 500: Internal server error

### Endpoints

#### GET '/categories'

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains an object of id: category_string and a sucess value.
- Sample: `curl http://127.0.0.1:5000/categories`

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true
}
```

#### GET '/questions?page=${integer}'

- Fetches a paginated set of questions, a total number of questions, all categories and current category string.
- Request Arguments: `page` - integer
- Returns: An object with 10 paginated questions, total questions, a dictionary of all categories, current category string, and a sucess value.
- Sample: `curl http://127.0.0.1:5000/questions?page=1`

```
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": "currentCategory",
  "questions": [
    {
      "answer": "Tom Cruise",
      "category": 5,
      "difficulty": 4,
      "id": 4,
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    ......
    {
      "answer": "Agra",
      "category": 3,
      "difficulty": 2,
      "id": 15,
      "question": "The Taj Mahal is located in which Indian city?"
    }
  ],
  "success": true,
  "total_questions": 20
}
```

#### DELETE '/questions/${id}'

- Deletes a specified question using the id of the question
- Request Arguments: `id` - integer
- Returns: Returns a success value.
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions/5`

```json
{
  "success": true
}
```

#### POST '/questions'

- Sends a post request to add a new question
- Request Arguments: A json body containing, `question` - string, `answer` - string, `difficulty` - integer, `category` - integer
- Returns: Returns a success value.
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question": "In what year was the last World Cup?", "answer": "2018", "difficulty": 2, "category":6}'`

```json
{
  "success": true
}
```

#### POST '/questions'

- Sends a post request in order to return any question for whom the search term
  is a substring of the question.
- Request Arguments: A json body containing, `searchTerm` - string
- Returns: any array of questions, a number of totalQuestions that met the search term, the current category string and a success value.
- Sample: `curl -X POST -H "Content-Type: application/json" -d'{"searchTerm":"title"}' http://127.0.0.1:5000/questions`

```json
{
  "current_category": "currentCategory",
  "questions": [
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "success": true,
  "total_questions": 1
}
```

#### GET '/categories/${id}/questions'

Fetches questions for a cateogry specified by id request argument

- Request Arguments: `id` - integer
- Returns: An object with questions for the specified category, total questions, current category string, and a success value.
- Sample: `curl http://127.0.0.1:5000/categories/1/questions`

```json
{
  "current_category": "currentCategory",
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    },
    {
      "answer": "Blood",
      "category": 1,
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

#### POST '/quizzes'

- Sends a post request in order to get the next question which is a random question within the given category (if provided), and that is not one of the previous questions.
- Request Argument: A json body containing, `previous_questions` - array, `quiz_category` - dictionary
- Returns: a single new question object and a success value.
- Sample: `curl -X POST -H "Content-Type: application/json" -d'{"previous_questions":[9], "quiz_category":{"id":0, "type":"no category"}}' http://127.0.0.1:5000/quizzes`

```json
{
  "question": {
    "answer": "Scarab",
    "category": 4,
    "difficulty": 4,
    "id": 23,
    "question": "Which dung beetle was worshipped by the ancient Egyptians?"
  },
  "success": true
}
```
