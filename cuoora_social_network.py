
from datetime import datetime

class Votes: #clase base para manejar los votos de Answer y Question
    def __init__(self):
        self.votes = []

    def get_votes(self):
        return self.votes
    
    def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes):
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote)
    
    def filter_votes(self, condition): # filtra los votos según la condición dada
        return [vote for vote in self.votes if condition(vote)]
    
    def positive_votes(self):
        return self.filter_votes(lambda vote: vote.is_like()) #votos condicion positiva
    
    def negative_votes(self):
        return self.filter_votes(lambda vote: not vote.is_like()) #votos condicion negativa

class Descripcion: #clase base para manejar la descripción de Answer, Question y Topic
    def __init__(self, description):
        self.description = description

    def get_description(self):
        return self.description
    
    def set_description(self, an_object):
        self.description = an_object

class Answer(object, Votes, Descripcion):
    def __init__(self, question, user, description):
        Votes().__init__()
        Descripcion.__init__(self, description)

        self.timestamp = datetime.now()
        self.user = user
        self.question = question
        self.question.add_answer(self)

    def get_question(self):
        return self.question
		
    def get_user(self):
        return self.user
	
    def get_timestamp(self):
        return self.timestamp
    

class Question(Votes, Descripcion):
    def __init__(self, user, title, description, topics=[]):
        Votes().__init__()
        Descripcion.__init__(self, description)

        self.timestamp = datetime.now()
        self.title = title
        self.answers = []
        self.user = user
        self.user.add_question(self)
        self.topics = []
        for topic in topics:
            self.add_topic(topic)

    def get_topics(self):
        return self.topics

    def get_title(self):
        return self.title
    
    def set_title(self, a_title):
        self.title = a_title

    def get_user(self):
        return self.user

    def get_timestamp(self):
        return self.timestamp

    def add_topic(self, a_topic):
        if a_topic in self.topics: 
            raise ValueError("El tópico ya está agregado.")
        self.topics.append(a_topic)
        a_topic.add_question(self)

    def add_answer(self, answer):
        self.answers.append(answer)

    def get_best_answer(self):
        if not self.answers:
            return None
        
        return sorted(self.answers, key=lambda a: len(a.positive_votes()) - len(a.negative_votes()), reverse=True)[0]


class Topic(Descripcion):
    def __init__(self, name, description):
        Descripcion.__init__(self, description)
        
        self.name = name
        self.questions = []

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_name(self):
        return self.name

    def set_name(self, an_object):
        self.name = an_object

    def get_questions(self):
        return self.questions


class User(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.questions = []
        self.answers = []
        self.topics_of_interest = []
        self.following = []
        self.votes = []

    def add_topic(self, a_topic):
        self.topics_of_interest.append(a_topic)

    def get_votes(self):
        return self.votes

    def questions_of_interest(self):
        return self.question_retriever.retrieve_questions(self)

    def get_question_retriever(self):
        return self.question_retriever

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_username(self):
        return self.username

    def get_questions(self):
        return self.questions

    def follow(self, a_user):
        self.following.append(a_user)

    def stop_follow(self, a_user):
        self.following.remove(a_user)

    def get_answers(self):
        return self.answers

    def get_following(self):
        return self.following

    def add_vote(self, a_vote):
        self.votes.append(a_vote)

    def get_password(self):
        return self.password

    def add_answer(self, an_answer):
        self.answers.append(an_answer)

    def get_topics_of_interest(self):
        return self.topics_of_interest

    def set_password(self, an_object):
        self.password = an_object

    def set_username(self, an_object):
        self.username = an_object

    def claculate_kind_score(kind_votes, score_points):
        score = 0
        for kind in kind_votes:
            pv = len(kind.positive_votes())
            nv = len(kind.negative_votes())
            if pv > nv:
                score += score_points
        return score

    def calculate_score(self):
        question_score = self.claculate_kind_score(self.questions, 10)
        answer_score = self.claculate_kind_score(self.answers, 20)

        return question_score + answer_score
        


class Vote(object):
    
    def __init__(self, user, is_like=True):
        self.is_positive_vote = is_like
        self.timestamp = datetime.now()
        self.user = user

    def is_like(self):
        return self.is_positive_vote

    def get_user(self):
        return self.user

    def like(self):
        self.is_positive_vote = True

    def dislike(self):
        self.is_positive_vote = False

class QuestionRetriever:

    @classmethod
    def create_social(cls):
        return cls._create_with_option("social")

    @classmethod
    def create_topics(cls):
        return cls._create_with_option("topics")

    @classmethod
    def create_news(cls):
        return cls._create_with_option("news")

    @classmethod
    def create_popular_today(cls):
        return cls._create_with_option("popularToday")

    @classmethod
    def _create_with_option(cls, option):
        instance = cls()
        instance._set_option(option)
        return instance
    
    def _set_option(self, an_option):
        self.option = an_option

    def retrieve_questions(self, questions, a_user):
        q_ret = []

        if self.option == "social":
            following_col = []
            for follow in a_user.following:
                following_col.extend(follow.questions)
            temp = sorted(following_col, key=lambda q: len(q.positive_votes()))
            q_ret = temp[-min(100, len(temp)):]

        elif self.option == "topics":
            topics_col = []
            for topic in a_user.get_topics_of_interest():
                topics_col.extend(topic.questions)
            temp = sorted(topics_col, key=lambda q: len(q.positive_votes()))
            q_ret = temp[-min(100, len(temp)):]

        elif self.option == "news":
            news_col = []
            for question in questions:
                if question.timestamp.date() == datetime.today().date():
                    news_col.append(question)
            temp = sorted(news_col, key=lambda q: len(q.positive_votes()))
            q_ret = temp[-min(100, len(temp)):]

        elif self.option == "popularToday":
            today_questions = [q for q in questions if q.timestamp.date() == datetime.today().date()]
            if today_questions:
                average_votes = sum(len(q.positive_votes()) for q in today_questions) / len(today_questions)
                popular_questions = []
                for q in today_questions:
                    if len(q.positive_votes()) > average_votes:
                        popular_questions.append(q)
                temp = sorted(popular_questions, key=lambda q: len(q.positive_votes()))
                q_ret = temp[-min(100, len(temp)):]

        return [q for q in q_ret if q.user != a_user]


class CuOOra:
    def __init__(self):
        self.questions = []

    def add_question(self, a_question):
        self.questions.append(a_question)

    def get_social_questions_for_user(self, user):
        social_retriever = QuestionRetriever.create_social()
        return social_retriever.retrieve_questions(self.questions, user)

    def get_topic_questions_for_user(self, user):
        topic_retriever = QuestionRetriever.create_topics()
        return topic_retriever.retrieve_questions(self.questions, user)

    def get_news_questions_for_user(self, user):
        news_retriever = QuestionRetriever.create_news()
        return news_retriever.retrieve_questions(self.questions, user)

    def get_popular_questions_for_user(self, user):
        popular_retriever = QuestionRetriever.create_popular_today()
        return popular_retriever.retrieve_questions(self.questions, user)
