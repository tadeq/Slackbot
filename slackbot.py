import time
from slackclient import SlackClient
import bot_responses
import api_data_fetching as api
from utils import unescape_html_entities, equals_case_insensitive


class UserStats:
    def __init__(self, uid):
        self.user_id = uid
        self.good_answers = 0
        self.bad_answers = 0


class SlackBot:
    def __init__(self):
        with open('auth.txt') as auth_file:
            self.slack_client = SlackClient(auth_file.readline().strip())
            self.bot_id = auth_file.readline().strip()
        self.current_question = None
        self.users = list()

    def find_user_index(self, uid):
        for ind, user in enumerate(self.users):
            if user.user_id == uid:
                return ind
        new_user = UserStats(uid)
        self.users.append(new_user)
        return len(self.users) - 1

    def connect_to_slack(self):
        return self.slack_client.rtm_connect()

    def read_rtm(self):
        return self.slack_client.rtm_read()

    def parse_input(self, slack_input):
        bot_atid = '<@{}>'.format(self.bot_id)
        if slack_input:
            slack_input = slack_input[0]
            if 'text' in slack_input and bot_atid in slack_input['text']:
                user = slack_input['user']
                message = slack_input['text'].split(bot_atid)[1].strip(' ')
                channel = slack_input['channel']
                return [str(user), str(message), str(channel)]
        return None

    def write(self, channel, message):
        return self.slack_client.api_call('chat.postMessage', channel=channel, text=message, as_user=True)

    def process_input(self, slack_input):
        parsed_input = self.parse_input(slack_input)
        if parsed_input is not None:
            user, message, channel = parsed_input
            self.respond(user, channel, message)

    def wait_for_answer(self):
        while True:
            parsed_input = self.parse_input(self.read_rtm())
            if parsed_input is not None:
                user, message, channel = parsed_input
                return message
            time.sleep(1)

    def respond(self, user, channel, message):
        if not self.current_question:
            if any(word in message.lower() for word in [greeting.lower() for greeting in bot_responses.greetings]):
                self.write(channel, bot_responses.say_hello())

            if any(word in message.lower().split(' ') for word in [api.get_category_names()]):
                for word in message.lower().split(' '):
                    category_names = api.get_category_names()
                    if word in [name.lower() for name in category_names]:
                        question = api.get_question_from_category(word)
                        self.current_question = question
                        self.write(channel, bot_responses.ask_question(question))

            elif any(word in message.lower() for word in ['category', 'categories']):
                found = False
                self.write(channel, bot_responses.show_categories())
                category_name = self.wait_for_answer()
                names = api.get_category_names()
                names = [unescape_html_entities(name) for name in names]
                for name in names:
                    if equals_case_insensitive(category_name, name):
                        question = api.get_question_from_category(category_name)
                        self.current_question = question
                        self.write(channel, bot_responses.ask_question(question))
                        found = True
                        break
                if not found and category_name.lower() in ['any', 'random']:
                    question = api.get_random_question()
                    self.current_question = question
                    self.write(channel, bot_responses.ask_question(question))
                elif not found:
                    self.write(channel, bot_responses.say_no_such_category())

            elif 'questions' in message.lower() and any(
                    word in message.lower() for word in ['amount', 'number', 'how many']):
                self.write(channel, bot_responses.show_questions_amount())

            elif any(word in message.lower() for word in ['question', 'ask me']):
                question = api.get_random_question()
                self.current_question = question
                self.write(channel, bot_responses.ask_question(question))

            elif any(word in message.lower() for word in ['stats', 'my answers']):
                index = self.find_user_index(user)
                self.write(channel, bot_responses.show_stats(self.users[index]))
        else:
            answer_exists = False
            answer = message
            while not answer_exists:
                if equals_case_insensitive(answer, self.current_question['correct_answer']):
                    answer_exists = True
                    index = self.find_user_index(user)
                    self.users[index].good_answers += 1
                    self.write(channel, bot_responses.say_answer_correct())
                elif any(equals_case_insensitive(inc, answer) for inc in self.current_question['incorrect_answers']):
                    answer_exists = True
                    index = self.find_user_index(user)
                    self.users[index].bad_answers += 1
                    self.write(channel, bot_responses.say_answer_incorrect())
                else:
                    self.write(channel, bot_responses.say_no_such_answer())
                    answer = self.wait_for_answer()
            self.current_question = None

    def run(self):
        welcomed = False
        if self.connect_to_slack():
            while True:
                parsed_input = self.parse_input(self.read_rtm())
                if parsed_input is not None:
                    user, message, channel = parsed_input
                    if not welcomed:
                        welcomed = True
                        self.write(channel, bot_responses.welcome())
                    self.respond(user, channel, message)
                time.sleep(1)
        else:
            print('Error while connecting to Slack')


if __name__ == '__main__':
    slack_bot = SlackBot()
    slack_bot.run()
