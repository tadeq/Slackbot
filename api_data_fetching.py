import requests
from utils import equals_case_insensitive


def get_categories():
    response = requests.get('https://opentdb.com/api_category.php')
    if response.status_code == 200:
        response = response.json()
        categories = response['trivia_categories']
        return categories
    else:
        print('{}: {}'.format(response.status_code, response.text))
        return None


def get_questions_amount():
    response = requests.get('https://opentdb.com/api_count_global.php')
    if response.status_code != 200:
        print('{}: {}'.format(response.status_code, response.text))
        return None
    return response.json()['overall']['total_num_of_questions']


def get_random_question():
    response = requests.get('https://opentdb.com/api.php?amount=1')
    if response.status_code != 200:
        print('{}: {}'.format(response.status_code, response.text))
        return None
    return response.json()['results'][0]


def get_question_from_category(category_name):
    category_id = get_category_id(category_name)
    response = requests.get('https://opentdb.com/api.php?amount=1&category={}'.format(category_id))
    if response.status_code != 200:
        print('{}: {}'.format(response.status_code, response.text))
        return None
    return response.json()['results'][0]


def get_category_id(category_name):
    categories = get_categories()
    for category in categories:
        if equals_case_insensitive(category['name'], category_name):
            return category['id']
    return None


def get_category_names():
    categories = get_categories()
    result = [category['name'] for category in categories]
    return result
