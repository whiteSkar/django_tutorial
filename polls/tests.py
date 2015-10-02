import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Question


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionTests(TestCase):
    def test_was_published_recently_future_date_returns_false(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_old_date_return_false(self):
        time = timezone.now() - datetime.timedelta(days=30)
        old_question = Question(pub_date=time)
        
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_recent_date_return_true(self):
        time = timezone.now() - datetime.timedelta(hours=1)
        recent_question = Question(pub_date=time)

        self.assertEqual(recent_question.was_published_recently(), True)


class QuestionIndexDetailTests(TestCase):
    def test_detail_view_with_a_future_question_returns_404(self):
        future_q = create_question(question_text='Future', days=5)

        resp = self.client.get(reverse('polls:detail', args=(future_q.id,)))

        self.assertEqual(resp.status_code, 404)

    def test_detail_view_with_a_past_question_returns_question(self):
        past_q = create_question(question_text='Past', days=-5)

        resp = self.client.get(reverse('polls:detail', args=(past_q.id,)))

        self.assertContains(resp, past_q.question_text, status_code=200)



class QuestionViewTests(TestCase):
    def test_index_view_with_no_questions_returns_empty_list(self):
        response = self.client.get(reverse('polls:index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_past_question_returns_question(self):
        question_text = 'Past question.'
        create_question(question_text=question_text, days=-30)
        
        response = self.client.get(reverse('polls:index'))
        
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: %s>" % question_text]
        )

    def test_index_view_with_future_question_returns_empty_list(self):
        create_question(question_text='Future question.', days=30)

        response = self.client.get(reverse('polls:index'))
        
        self.assertContains(response, "No polls are available.", status_code=200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_index_view_with_future_and_past_question_returns_past(self):
        past_question_text = 'Past question.'
        create_question(question_text=past_question_text, days=-30)
        create_question(question_text='Future question.', days=30)

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: %s>" % past_question_text]
        )

    def test_index_view_with_two_past_questions_returns_past_questions(self):
        question_text1 = 'Past question 1.'
        question_text2 = 'Past question 2.'
        create_question(question_text=question_text1, days=-30)
        create_question(question_text=question_text2, days=-5)

        response = self.client.get(reverse('polls:index'))

        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ["<Question: %s>" % question_text2, 
             "<Question: %s>" % question_text1]
        )
