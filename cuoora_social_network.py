from datetime import datetime
from abc import ABC, abstractmethod

# =================== INTERFACES =================== #
class Votable(ABC): # Interfaz para objetos que pueden recibir votos
    @abstractmethod
    def add_vote(self, vote):
        pass
    
    @abstractmethod
    def get_votes(self):
        pass
    
    @abstractmethod
    def positive_votes(self):
        pass
    
    @abstractmethod
    def negative_votes(self):
        pass

class Describable(ABC): # Interfaz para objetos que tienen una descripción
    @abstractmethod
    def get_description(self):
        pass
    
    @abstractmethod
    def set_description(self, new_description):
        pass


# =================== CLASES DE CONTROL =================== #
class VotesManager: # Gestiona la colección de votos y proporciona operaciones sobre ellos
    def __init__(self):
        self.votes = []

    def get_votes(self):
        return self.votes

    def add_vote(self, a_vote):
        if any(vote.user == a_vote.user for vote in self.votes):
            raise ValueError("Este usuario ya ha votado")
        self.votes.append(a_vote)
    
    def filter_votes(self, condition):
        return [vote for vote in self.votes if condition(vote)]

class DescriptionManager: # Encapsula la gestión de la descripción de un objeto
    def __init__(self, description):
        self.description = description

    def get_description(self):
        return self.description
    
    def set_description(self, an_object):
        self.description = an_object


# =================== ENTIDADES PRINCIPALES =================== #
class Answer(Votable, Describable): # Representa una respuesta a una pregunta, puede recibir votos y tiene descripción
    def __init__(self, question, user, description):
        self.votes_manager = VotesManager()
        self.description_manager = DescriptionManager(description)
        self.timestamp = datetime.now()
        self.user = user
        self.question = question
        question.add_answer(self)
        user.add_answer(self)

    def add_vote(self, vote): self.votes_manager.add_vote(vote)
    
    def get_votes(self): return self.votes_manager.get_votes()
    
    def positive_votes(self): return self.votes_manager.filter_votes(lambda vote: vote.is_like())
    
    def negative_votes(self): return self.votes_manager.filter_votes(lambda vote: not vote.is_like())

    def get_description(self): return self.description_manager.get_description()
    
    def set_description(self, new_description): self.description_manager.set_description(new_description)

    def get_question(self): return self.question
    
    def get_user(self): return self.user
    
    def get_timestamp(self): return self.timestamp

class Question(Votable, Describable): # Representa una pregunta del sistema, puede recibir votos y tiene descripción
    def __init__(self, user, title, description, topics=None):
        if topics is None:
            topics = []
            
        self.votes_manager = VotesManager()
        self.description_manager = DescriptionManager(description)
        self.timestamp = datetime.now()
        self.title = title
        self.answers = []
        self.user = user
        self.user.add_question(self)
        self.topics = []
        
        for topic in topics:
            self.add_topic(topic)

    def add_vote(self, vote): self.votes_manager.add_vote(vote)
    
    def get_votes(self): return self.votes_manager.get_votes()
    
    def positive_votes(self): return self.votes_manager.filter_votes(lambda vote: vote.is_like())
    
    def negative_votes(self): return self.votes_manager.filter_votes(lambda vote: not vote.is_like())

    def get_description(self): return self.description_manager.get_description()
    
    def set_description(self, new_description): self.description_manager.set_description(new_description)

    def get_topics(self): return self.topics.copy()

    def get_title(self): return self.title
    
    def set_title(self, new_title):
        if not new_title or not isinstance(new_title, str):
            raise ValueError("El título debe ser un string no vacío")
        self.title = new_title

    def get_user(self): return self.user

    def get_timestamp(self): return self.timestamp

    def add_topic(self, topic):
        if topic in self.topics: 
            raise ValueError("El tópico ya está agregado")
        self.topics.append(topic)
        topic.add_question(self)

    def add_answer(self, answer):
        if answer not in self.answers:
            self.answers.append(answer)

    def get_best_answer(self):
        if not self.answers:
            return None
        
        return max(self.answers, key=lambda a: len(a.positive_votes()) - len(a.negative_votes()))

class Topic(Describable): # Representa un tema o categoría para clasificar preguntas
    def __init__(self, name, description):
        self.description_manager = DescriptionManager(description)
        self.name = name
        self.questions = []

    def add_question(self, a_question):
        if a_question not in self.questions:
            self.questions.append(a_question)

    def get_name(self): return self.name

    def set_name(self, an_object): self.name = an_object

    def get_questions(self): return self.questions.copy()
    
    def get_description(self): return self.description_manager.get_description()
    
    def set_description(self, new_description): self.description_manager.set_description(new_description)


class User: # Representa un usuario del sistema con sus preguntas, respuestas y relaciones
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.questions = []
        self.answers = []
        self.topics_of_interest = []
        self.following = []
        self.votes = []

    def add_topic(self, a_topic):
        if a_topic not in self.topics_of_interest:
            self.topics_of_interest.append(a_topic)

    def get_votes(self): return self.votes.copy()

    def add_question(self, a_question): self.questions.append(a_question)

    def get_username(self): return self.username

    def get_questions(self): return self.questions.copy()

    def follow(self, a_user):
        if a_user not in self.following:
            self.following.append(a_user)

    def stop_follow(self, a_user):
        if a_user in self.following:
            self.following.remove(a_user)

    def get_answers(self): return self.answers.copy()

    def get_following(self): return self.following.copy()

    def add_vote(self, a_vote): self.votes.append(a_vote)

    def get_password(self): return self.password

    def add_answer(self, an_answer): self.answers.append(an_answer)

    def get_topics_of_interest(self): return self.topics_of_interest.copy()

    def set_password(self, an_object): self.password = an_object

    def set_username(self, an_object): self.username = an_object

    def calculate_kind_score(kind_votes, score_points):
        score = 0
        for kind in kind_votes:
            pv = len(kind.positive_votes())
            nv = len(kind.negative_votes())
            if pv > nv:
                score += score_points
        return score

    def calculate_score(self):
        question_score = User.calculate_kind_score(self.questions, 10)
        answer_score = User.calculate_kind_score(self.answers, 20)
        return question_score + answer_score

class Vote: # Representa un voto dado por un usuario
    def __init__(self, user, is_like=True):
        self.is_positive_vote = is_like
        self.timestamp = datetime.now()
        self.user = user
        user.add_vote(self)

    def is_like(self): return self.is_positive_vote

    def get_user(self): return self.user

    def like(self): self.is_positive_vote = True

    def dislike(self): self.is_positive_vote = False


# =================== SISTEMA DE RECUPERACIÓN DE PREGUNTAS =================== #
class IQuestionRetriever(ABC): # Interfaz base para recuperar preguntas
    @abstractmethod
    def retrieve_questions(self, all_questions, user): pass

    def _filter_and_sort(self, questions_collection, user, limit=100):
        if not questions_collection:
            return []
            
        # Ordenar por número de votos positivos
        temp = sorted(questions_collection, key=lambda q: len(q.positive_votes()))
        
        # Limitar a 'limit' resultados (máximo 100)
        result = temp[-min(limit, len(temp)):]
        
        # Filtrar preguntas hechas por el usuario actual
        return [q for q in result if q.get_user() != user]

# =============== ESTRATEGIAS DE RECUPERACIÓN DE PREGUNTAS =================== #
class SocialQuestionRetriever(IQuestionRetriever): # Recupera preguntas basadas en los usuarios
    def retrieve_questions(self, all_questions, user):
        following_col = []
        for follow in user.get_following():
            following_col.extend(follow.get_questions())
        
        return self._filter_and_sort(following_col, user)

class TopicsQuestionRetriever(IQuestionRetriever): # Recupera preguntas basadas en los temas de interés del usuario
    def retrieve_questions(self, all_questions, user):
        topics_col = []
        for topic in user.get_topics_of_interest():
            topics_col.extend(topic.get_questions())
        
        return self._filter_and_sort(topics_col, user)


class TodayQuestionRetriever(IQuestionRetriever): # Clase base para recuperadores que trabajan con preguntas de hoy
    def _get_today_questions(self, all_questions):
        return [q for q in all_questions if q.get_timestamp().date() == datetime.today().date()]


class NewsQuestionRetriever(TodayQuestionRetriever): # Recupera preguntas creadas hoy
    def retrieve_questions(self, all_questions, user):
        today_questions = self._get_today_questions(all_questions)
        return self._filter_and_sort(today_questions, user)


class PopularTodayQuestionRetriever(TodayQuestionRetriever): # Recupera praguntas creadas hoy con muchos votos positivos
    def retrieve_questions(self, all_questions, user):
        today_questions = self._get_today_questions(all_questions)
        
        if not today_questions:
            return []
        
        average_votes = sum(len(q.positive_votes()) for q in today_questions) / len(today_questions)
        popular_questions = [q for q in today_questions if len(q.positive_votes()) > average_votes]
        
        return self._filter_and_sort(popular_questions, user)


# =================== FÁBRICA Y SISTEMA PRINCIPAL =================== #
class QuestionRetrieverFactory: # Fábrica que crea las diferentes implementaciones de recuperadores de preguntas
    @staticmethod
    def create_social():
        return SocialQuestionRetriever()

    @staticmethod
    def create_topics():
        return TopicsQuestionRetriever()

    @staticmethod
    def create_news():
        return NewsQuestionRetriever()

    @staticmethod
    def create_popular_today():
        return PopularTodayQuestionRetriever()


class CuOOra: # Clase principal que representa todo el sistema CuOOra
    def __init__(self):
        self.questions = []
        self.retriever_factory = QuestionRetrieverFactory()

    def add_question(self, a_question):
        self.questions.append(a_question)
        
    def get_questions(self):
        return self.questions.copy()

    def get_social_questions_for_user(self, user):
        retriever = self.retriever_factory.create_social()
        return retriever.retrieve_questions(self.questions, user)

    def get_topic_questions_for_user(self, user):
        retriever = self.retriever_factory.create_topics()
        return retriever.retrieve_questions(self.questions, user)

    def get_news_questions_for_user(self, user):
        retriever = self.retriever_factory.create_news()
        return retriever.retrieve_questions(self.questions, user)

    def get_popular_questions_for_user(self, user):
        retriever = self.retriever_factory.create_popular_today()
        return retriever.retrieve_questions(self.questions, user)