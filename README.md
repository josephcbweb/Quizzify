# Quizzify

Quizzify is a web-based quiz platform that allows users to take multiple-choice quizzes on various topics. The quizzes are presented randomly from a chosen category, and users can review their past results.

## Features

- **Multiple-choice quizzes**: Users can select from different categories, and the questions are displayed randomly.
- **User-friendly interface**: Built with Flask and Bootstrap for a responsive design.
- **Results history**: Keeps track of previous quiz results for users to review.
- **Dynamic database**: Uses SQLAlchemy for database management, and the database is created automatically on the first run.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap
- **Database**: SQLAlchemy (SQLite or other relational databases)
- **Version Control**: Git

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/josephcbweb/Quizzify.git
   cd Quizzify

2. Set up a virtual environment:

bash
Copy code
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. Install the required dependencies:

bash
Copy code
pip install -r requirements.txt

4. Run the application:

bash
Copy code
flask run
The database will be created automatically on the first run.

5. Open the app in your browser at http://127.0.0.1:5000


## Usage
1. Start a Quiz: Select a category to begin the quiz, and answer multiple-choice questions.
2. View Results: After completing the quiz, users can view their scores and correct answers.
3. History Page: Access previous quiz results from the history page.



## License
This project is licensed under the MIT License.
