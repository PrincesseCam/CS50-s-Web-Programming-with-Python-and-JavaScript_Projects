from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Topic, Quiz, Question, Answer, UserTopicProgress
from django.core.paginator import Paginator

class ModelTests(TestCase):
    """Tests for the model functionality and relationships"""
    
    def setUp(self):
        # Creation of a test user
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Creation of a test topic
        self.topic = Topic.objects.create(
            name='Python Basics',
            category='Programming',
            description='Learn Python fundamentals',
            difficulty_level='beginner',
            max_attempts=3
        )
        
        # Creation of a test quiz
        self.quiz = Quiz.objects.create(
            user=self.user,
            topic=self.topic,
            score=0
        )
        
        # Test for question and answers
        self.question = Question.objects.create(
            quiz=self.quiz,
            text='What is Python?',
            correct_answer='A programming language',
            explanation='Python is a popular programming language'
        )
        
        self.answers = [
            Answer.objects.create(
                question=self.question,
                text='A programming language',
                is_correct=True
            ),
            Answer.objects.create(
                question=self.question,
                text='A snake 😆',
                is_correct=False
            )
        ]

    def test_topic_creation(self):
        """Test that a topic can be created with all fields"""
        self.assertEqual(self.topic.name, 'Python Basics')
        self.assertEqual(self.topic.category, 'Programming')
        self.assertEqual(self.topic.difficulty_level, 'beginner')

    def test_user_progress_tracking(self):
        """Test that user progress is tracked correctly"""
        progress = UserTopicProgress.objects.create(
            user=self.user,
            topic=self.topic,
            attempts=1,
            best_score=80
        )
        self.assertTrue(progress.can_attempt_quiz())
        self.assertEqual(progress.attempts, 1)
        self.assertEqual(progress.best_score, 80)

    def test_quiz_scoring(self):
        """Test quiz scoring functionality"""
        self.quiz.score = 5
        self.quiz.save()
        self.assertEqual(self.quiz.score, 5)

class ViewTests(TestCase):
    """Tests for view functionality"""
    
    def setUp(self):
        # Create client and test user
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create multiple test topics for pagination testing
        for i in range(15):  # Create 15 topics to test pagination
            Topic.objects.create(
                name=f'Topic {i}',
                category='Programming',
                description=f'Description {i}',
                difficulty_level='beginner',
                max_attempts=3
            )

    def test_topic_list_pagination(self):
        """Test that topic list pagination works correctly"""
        # Log in the user
        self.client.login(username='testuser', password='testpass123')
        
        # Get the topic list page
        response = self.client.get(reverse('topic_list'))
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Check pagination
        self.assertTrue('topics' in response.context)
        self.assertLessEqual(len(response.context['topics']), 12)
        
        # Test second page
        response = self.client.get(reverse('topic_list') + '?page=2')
        self.assertEqual(response.status_code, 200)

    def test_quiz_creation(self):
        """Test that a quiz can be created and started"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a topic
        topic = Topic.objects.create(
            name='Test Topic',
            category='Test',
            description='Test Description',
            difficulty_level='beginner'
        )
        
        # Start a quiz
        response = self.client.get(reverse('start_quiz', args=[topic.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect to quiz question

    def test_quiz_answering(self):
        """Test the quiz answering process"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create a quiz with questions
        topic = Topic.objects.create(name='Test Topic', category='Test')
        quiz = Quiz.objects.create(user=self.user, topic=topic)
        question = Question.objects.create(
            quiz=quiz,
            text='Test Question',
            correct_answer='Correct'
        )
        correct_answer = Answer.objects.create(
            question=question,
            text='Correct',
            is_correct=True
        )
        
        # Submit an answer
        response = self.client.post(
            reverse('quiz_question', args=[quiz.id]),
            {'answer': correct_answer.id}
        )
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access protected pages"""
        # Try to access topic list without logging in
        response = self.client.get(reverse('topic_list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

class APITests(TestCase):
    """Tests for API functionality"""
    
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_question_generation(self):
        """Test the question generation API functionality"""
        from .views import generate_quiz_questions
        
        # Test question generation
        questions = generate_quiz_questions('Python')
        
        # Verify question format
        self.assertTrue(isinstance(questions, list))
        if questions:  # If API returns questions
            first_question = questions[0]
            self.assertTrue('question' in first_question)
            self.assertTrue('answers' in first_question)
            self.assertTrue('explanation' in first_question)

class LeaderboardTests(TestCase):
    """Tests for leaderboard functionality"""
    
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_leaderboard_display(self):
        """Test that the leaderboard displays correctly"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create some test data
        topic = Topic.objects.create(name='Test Topic', category='Test')
        progress = UserTopicProgress.objects.create(
            user=self.user,
            topic=topic,
            best_score=90
        )
        
        # Check leaderboard page
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('rankings' in response.context)