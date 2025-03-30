import unittest
from unittest.mock import patch
from datetime import datetime, timedelta
from cuoora_social_network import Answer, User, Question, Vote, CuOOra, Topic, QuestionRetrieverFactory

class AnswerTest(unittest.TestCase):
    def setUp(self):
        self.answer = Answer(Question(User('pepe2', 'pepe2'), 'Sample Question', 'Description'), 
                            User('pepe', 'pepe'), 
                            'An answer'
                            )

    def test_votes_for_new_answer(self):
        self.assertEqual(len(self.answer.negative_votes()), 0)
        self.assertEqual(len(self.answer.positive_votes()), 0)

    def test_positive_votes(self):
        vote = Vote(User('pepe33', 'pepe33'), True)
        self.answer.add_vote(vote)
        self.assertEqual(len(self.answer.positive_votes()), 1)

        vote2 = Vote(User('pepe33', 'pepe33'), True)
        self.answer.add_vote(vote2)
        self.assertEqual(len(self.answer.positive_votes()), 2)

    def test_negative_votes(self):
        vote = Vote(User('pepe33', 'pepe33'), False)
        self.answer.add_vote(vote)
        self.assertEqual(len(self.answer.negative_votes()), 1)

        vote2 = Vote(User('pepe33', 'pepe33'), False)
        self.answer.add_vote(vote2)
        self.assertEqual(len(self.answer.negative_votes()), 2)

    def test_positive_and_negative_votes_interference(self):
        vote = Vote(User('pepe33', 'pepe33'), False)
        self.answer.add_vote(vote)
        self.assertEqual(len(self.answer.positive_votes()), 0)

        vote2 = Vote(User('pepe33', 'pepe33'), True)
        self.answer.add_vote(vote2)
        self.assertEqual(len(self.answer.positive_votes()), 1)

        vote3 = Vote(User('pepe33', 'pepe33'), True)
        self.answer.add_vote(vote3)
        self.assertEqual(len(self.answer.positive_votes()), 2)

        vote4 = Vote(User('pepe33', 'pepe33'), False)
        self.answer.add_vote(vote4)
        self.assertEqual(len(self.answer.positive_votes()), 2)

        self.assertEqual(len(self.answer.get_votes()), 4)

    def test_add_votes_same_user(self):
        user = User('pepe33', 'pepe33')
        vote = Vote(user, True)
        self.answer.add_vote(vote)
        self.assertEqual(len(self.answer.positive_votes()), 1)
        vote2 = Vote(user, True)
        with self.assertRaises(ValueError):
            self.answer.add_vote(vote2)

class QuestionTest(unittest.TestCase):
    def setUp(self):
        self.user = User("test_user", "password")
        self.other_user = User("other_user", "password")
        self.question = Question(self.user, "¿Cuál es el mejor lenguaje de programación?", "Opiniones sobre lenguajes.")

        # Crear usuarios únicos para los votos
        users_pos = [User(f"pos_user_{i}", "password") for i in range(8)]
        users_neg = [User(f"neg_user_{i}", "password") for i in range(2)]

        # Respuesta con 80% de votos positivos (8 positivos, 2 negativos)
        self.answer1 = Answer(self.question, self.user, "Python es el mejor.")
        for user in users_pos:
            vote = Vote(user, is_like=True)
            self.answer1.add_vote(vote)
        for user in users_neg:
            vote = Vote(user, is_like=False)
            self.answer1.add_vote(vote)

        # Crear usuarios únicos para los votos de la segunda respuesta
        users_pos2 = [User(f"pos2_user_{i}", "password") for i in range(6)]
        users_neg2 = [User(f"neg2_user_{i}", "password") for i in range(4)]

        # Respuesta con 60% de votos positivos (6 positivos, 4 negativos)
        self.answer2 = Answer(self.question, self.user, "Java es más versátil.")
        for user in users_pos2:
            vote = Vote(user, is_like=True)
            self.answer2.add_vote(vote)
        for user in users_neg2:
            vote = Vote(user, is_like=False)
            self.answer2.add_vote(vote)

    def test_votes_for_new_question(self):
        self.assertEqual(len(self.question.negative_votes()), 0)
        self.assertEqual(len(self.question.positive_votes()), 0)

    def test_positive_votes(self):
        vote = Vote(User('pepe33', 'pepe33'), True)
        self.question.add_vote(vote)
        self.assertEqual(len(self.question.positive_votes()), 1)

        vote2 = Vote(User('pepe33', 'pepe33'), True)
        self.question.add_vote(vote2)
        self.assertEqual(len(self.question.positive_votes()), 2)

    def test_negative_votes(self):
        vote = Vote(User('pepe33', 'pepe33'), False)
        self.question.add_vote(vote)
        self.assertEqual(len(self.question.negative_votes()), 1)

        vote2 = Vote(User('pepe33', 'pepe33'), False)
        self.question.add_vote(vote2)
        self.assertEqual(len(self.question.negative_votes()), 2)

    def test_positive_and_negative_votes_interference(self):
        vote = Vote(User('pepe33', 'pepe33'), False)
        self.question.add_vote(vote)
        self.assertEqual(len(self.question.positive_votes()), 0)

        vote2 = Vote(User('pepe33', 'pepe33'), True)
        self.question.add_vote(vote2)
        self.assertEqual(len(self.question.positive_votes()), 1)

        vote3 = Vote(User('pepe33', 'pepe33'), True)
        self.question.add_vote(vote3)
        self.assertEqual(len(self.question.positive_votes()), 2)

        vote4 = Vote(User('pepe33', 'pepe33'), False)
        self.question.add_vote(vote4)
        self.assertEqual(len(self.question.positive_votes()), 2)

        self.assertEqual(len(self.question.get_votes()), 4)

    def test_add_votes_same_user(self):
        user = User('pepe33', 'pepe33')
        vote = Vote(user, True)
        self.question.add_vote(vote)
        self.assertEqual(len(self.question.positive_votes()), 1)
        vote2 = Vote(user, True)
        with self.assertRaises(ValueError):
            self.question.add_vote(vote2)

    def test_add_topics_to_question(self):
        topic1 = Topic("Python", "A programming language")
        self.question.add_topic(topic1)
        self.assertIn(topic1, self.question.get_topics())
        self.assertEqual(len(self.question.get_topics()), 1)

        topic2 = Topic("Machine Learning", "A subset of AI")
        self.question.add_topic(topic2)
        self.assertIn(topic2, self.question.get_topics())
        self.assertEqual(len(self.question.get_topics()), 2)

    def test_add_duplicate_topics(self):
        topic = Topic("Python", "A programming language")
        self.question.add_topic(topic)
        with self.assertRaises(ValueError):
            self.question.add_topic(topic)
        self.assertEqual(len(self.question.get_topics()), 1)

    def test_initialize_with_topics(self):
        topic1 = Topic("AI", "Artificial Intelligence")
        topic2 = Topic("Deep Learning", "A subset of Machine Learning")
        question_with_topics = Question(User('pepe', 'pepePWD'), 'Sample Question', 'Description', [topic1, topic2])
        topics = question_with_topics.get_topics()
        self.assertIn(topic1, topics)
        self.assertIn(topic2, topics)
        self.assertEqual(len(topics), 2)

    def test_best_answer(self):
        best_answer = self.question.get_best_answer()
        self.assertEqual(best_answer, self.answer1, "El método no retorna la mejor respuesta correctamente.")

    def test_best_answer_changed_by_positive_votes(self):
        best_answer = self.question.get_best_answer()
        self.assertEqual(best_answer, self.answer1, "El método no retorna la mejor respuesta correctamente.")

        # Crear usuarios únicos para los votos adicionales
        new_users = [User(f"new_pos_user_{i}", "password") for i in range(5)]
        
        for user in new_users:
            vote = Vote(user, is_like=True)
            self.answer2.add_vote(vote)

        best_answer = self.question.get_best_answer()
        self.assertEqual(best_answer, self.answer2, "El método no retorna la mejor respuesta correctamente.")

    def test_best_answer_changed_by_negative_votes(self):
        best_answer = self.question.get_best_answer()
        self.assertEqual(best_answer, self.answer1, "El método no retorna la mejor respuesta correctamente.")

        # Crear usuarios únicos para los votos adicionales
        new_users = [User(f"new_neg_user_{i}", "password") for i in range(5)]
        
        for user in new_users:
            vote = Vote(user, is_like=False)
            self.answer1.add_vote(vote)

        best_answer = self.question.get_best_answer()
        self.assertEqual(best_answer, self.answer2, "El método no retorna la mejor respuesta correctamente.")


class CuooraRetrieverTest(unittest.TestCase):
    def setUp(self):
        # Instancias de CuOOra y usuarios
        self.cuoora = CuOOra()
        self.user1 = User('user1', 'pass1')
        self.user2 = User('user2', 'pass2')
        self.user3 = User('user3', 'pass3')

        # Instancia de Topics
        self.topic1 = Topic('Python', 'Programming in Python')
        self.topic2 = Topic('Django', 'Web development with Django')
        self.user1.add_topic(self.topic1)
        self.user2.add_topic(self.topic2)
        
        self.question1 = Question(self.user2, "What is Python?", "Python basics", [self.topic1])
        self.question2 = Question(self.user3, "Django best practices", "Optimizing Django apps", [self.topic2])

        yesterday = datetime.now() - timedelta(days=1)

        with patch("cuoora_social_network.datetime") as mock_datetime:
            mock_datetime.now.return_value = yesterday
            self.question3 = Question(self.user1, "Newest tech trends", "AI and ML trends", [self.topic1])
        
        self.cuoora.add_question(self.question1)
        self.cuoora.add_question(self.question2)
        self.cuoora.add_question(self.question3)
        
        self.user1.follow(self.user2)
        self.user2.follow(self.user3)

    def test_social_retrieval(self):
        retrieved_questions = self.cuoora.get_social_questions_for_user(self.user1)
        self.assertIn(self.question1, retrieved_questions)
        self.assertNotIn(self.question3, retrieved_questions)
        self.user1.stop_follow(self.user2)

        retrieved_questions = self.cuoora.get_social_questions_for_user(self.user1)
        self.assertNotIn(self.question1, retrieved_questions)

    def test_topics_retrieval(self):
        retrieved_questions = self.cuoora.get_topic_questions_for_user(self.user2)
        self.assertIn(self.question2, retrieved_questions)
        self.assertNotIn(self.question1, retrieved_questions)
        self.assertNotIn(self.question3, retrieved_questions)

        self.question3.add_topic(self.topic2)
        retrieved_questions = self.cuoora.get_topic_questions_for_user(self.user2)
        self.assertIn(self.question2, retrieved_questions)
        self.assertIn(self.question3, retrieved_questions)

        self.question1.add_topic(self.topic2)
        retrieved_questions = self.cuoora.get_topic_questions_for_user(self.user2)
        self.assertIn(self.question2, retrieved_questions)
        self.assertIn(self.question3, retrieved_questions)
        self.assertNotIn(self.question1, retrieved_questions)

    def test_news_retrieval(self):
        retrieved_questions = self.cuoora.get_news_questions_for_user(self.user3)
        self.assertIn(self.question1, retrieved_questions)
        self.assertNotIn(self.question2, retrieved_questions)
        self.assertNotIn(self.question3, retrieved_questions)

    def test_popular_today_retrieval(self):
        retrieved_questions = self.cuoora.get_popular_questions_for_user(self.user3)
        self.assertEqual(len(retrieved_questions), 0)
        
        vote = Vote(self.user1)
        self.question1.add_vote(vote)
        
        retrieved_questions = self.cuoora.get_popular_questions_for_user(self.user3)
        self.assertIn(self.question1, retrieved_questions)

class TestUserScore(unittest.TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User("test_user", "password")
        self.other_user = User("other_user", "password")

        # Crear preguntas y respuestas
        self.question1 = Question(self.user, "¿Qué es Python?", "Explicación sobre Python")
        self.question2 = Question(self.user, "¿Cómo funciona la memoria en C?", "Detalles sobre memoria en C")
        
        self.answer1 = Answer(self.question1, self.user, "Python es un lenguaje interpretado.")
        self.answer2 = Answer(self.question2, self.user, "En C, la memoria se maneja con malloc y free.")

        # Crear votos
        vote1 = Vote(self.other_user, is_like=True)  # Voto positivo
        vote2 = Vote(User("negative_voter", "password"), is_like=False)  # Voto negativo

        # Agregar votos a preguntas
        self.question1.add_vote(vote1)  # +1 positivo → cuenta
        self.question2.add_vote(vote2)  # +1 negativo → no cuenta

        # Crear usuarios únicos para los votos de respuestas
        answer_voter1 = User("answer_voter1", "password")
        answer_voter2 = User("answer_voter2", "password")
        
        vote3 = Vote(answer_voter1, is_like=True)  # Voto positivo
        vote4 = Vote(answer_voter2, is_like=False)  # Voto negativo
        
        # Agregar votos a respuestas
        self.answer1.add_vote(vote3)  # +1 positivo → cuenta
        self.answer2.add_vote(vote4)  # +1 negativo → no cuenta

    def test_calculate_score(self):
        expected_score = 10 + 20  # Pregunta 1 (10) + Respuesta 1 (20)
        self.assertEqual(self.user.calculate_score(), expected_score)

    def test_calculate_score_after_new_votes(self):
        initial_expected_score = 10 + 20
        self.assertEqual(self.user.calculate_score(), initial_expected_score)

        # Crear usuarios únicos para los nuevos votos
        new_voter1 = User("new_voter1", "password")
        new_voter2 = User("new_voter2", "password")
        
        new_vote1 = Vote(new_voter1, is_like=True)  
        new_vote2 = Vote(new_voter2, is_like=True)
        
        self.question2.add_vote(new_vote1)
        self.question2.add_vote(new_vote2)

        expected_new_score = initial_expected_score + 10
        self.assertEqual(self.user.calculate_score(), expected_new_score)


if __name__ == '__main__':
    unittest.main()