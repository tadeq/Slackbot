from random import shuffle, randint
from utils import unescape_html_entities
import api_data_fetching as api

greetings = ['Hi', 'Hello', 'Welcome', 'Greetings', 'Good day', 'Hey']


def welcome():
    return 'Hello!\nI am the quiz bot. You can ask me to pick a question for you whenever you want. ' \
           'You can also specify category of your question. I will count your good and bad answers.'


def say_hello():
    shuffle(greetings)
    return greetings[randint(0, len(greetings) - 1)]


def ask_question(question):
    answers = question['incorrect_answers']
    answers.append(question['correct_answer'])
    answers = [unescape_html_entities(answer) for answer in answers]
    question_text = unescape_html_entities(question['question'])
    shuffle(answers)
    return '{}\n{} or {}?'.format(question_text, ', '.join(answers[:-1]), answers[-1])


def show_categories():
    return 'The categories are: {}\nFrom which of them should I pick a question?'.format(
        ', '.join(api.get_category_names()))


def show_questions_amount():
    return 'I know {} questions and I can ask you any of them'.format(api.get_questions_amount())


def show_stats(user):
    return 'You have {} correct answers and {} incorrect answers'.format(user.good_answers, user.bad_answers)


def say_no_such_category():
    return 'I don\'t know such category. Please choose the one that I know or tell me to pick random question'


def say_answer_correct():
    good = ['Good', 'Very good', 'Nice', 'Great', 'Excellent', 'Wonderful', 'Super', 'Correct']
    shuffle(good)
    return '{}!'.format(good[randint(0, len(good) - 1)])


def say_answer_incorrect():
    return 'Your answer was incorrect.'


def say_no_such_answer():
    return 'There is no such answer. Please choose one of the answers which I mentioned earlier'
