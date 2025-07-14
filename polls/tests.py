import datetime
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice 
from django.contrib.auth.models import User

# Create your tests here.
class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the given number of `days` offset to now (negative for questions published in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question])

    def test_future_question(self):
        """
        Questions with a pub_date in the future are not displayed on the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question],)

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [question2, question1])
 

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Future question.",  days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        reponse = self.client.get(url)
        self.assertEqual(reponse.status_code, 200)

class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        reponse = self.client.get(url)
        self.assertEqual(reponse.status_code, 200)

class VoteAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.question = Question.objects.create(
            question_text="What's up?",
            pub_date=timezone.now()
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text="Not much",
            votes=0
        )

    def test_redirect_vote_if_not_logged_in(self):
        vote_url = reverse("polls:vote", args=(self.question.id,))
        response = self.client.post(vote_url, {"choice": self.choice.id})
        self.assertRedirects(response, f"/polls/login/?next={vote_url}")

    def test_authenticated_user_can_vote(self):
        self.client.login(username="testuser", password="password")
        vote_url = reverse("polls:vote", args=(self.question.id,))
        response = self.client.post(vote_url, {"choice": self.choice.id})
        self.assertRedirects(response, reverse("polls:results", args=(self.question.id,)))
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)

    def test_vote_without_selecting_choice(self):
        self.client.login(username="testuser", password="password")
        vote_url = reverse("polls:vote", args=(self.question.id,))
        response = self.client.post(vote_url, {})  # No 'choice'
        self.assertContains(response, "You didn")


    def test_auth_user_can_log_out(self):
        self.client.login(username="testuser", password="password")
        logout_url = reverse("polls:logout")
        response = self.client.get(logout_url)
        self.assertRedirects(response, reverse("polls:index"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_login_success(self):
        response = self.client.post(reverse("polls:login"), {
            "username": "testuser",
            "password": "password"
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.url.startswith("/"))  # Usually index or `next`

    def test_login_failure(self):
        response = self.client.post(reverse("polls:login"), {
            "username": "testuser",
            "password": "wrongpassword"
        })
        self.assertContains(response, "Please enter a correct username and password")


    