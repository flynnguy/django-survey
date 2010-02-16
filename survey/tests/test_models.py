
test_cases = r"""
Test creation of a survey

>>> from survey.models import *
>>> from django.contrib.auth.models import *
>>> import datetime

>>> user = User.objects.create_user('user_test', 'user@test.fr','password')
>>> user.save()
>>> survey = survey = Survey(title="survey 1", slug="survey-1",
... opens=datetime.datetime(2008,03,01,11,11,11),
... closes=datetime.datetime(2008,03,01,11,11,11))
>>> survey.created_by = user
>>> survey.editable_by = user
>>> survey.save()
>>> print survey
survey-1 - survey 1
>>> survey.get_absolute_url()
'/survey/detail/survey-1/'

Test the survey API

>>> survey.open
False
>>> survey.closes= datetime.datetime(2099,03,01,11,11,11)
>>> survey.visible=True
>>> survey.save()
>>> survey.open
True

>>> survey.answer_count
0
>>> survey.interview_count
0
>>> survey.session_key_count
0



Test the creation of a question

>>> question1 = Question(survey=survey, text="Is it working ?")
>>> question1.save()
>>> question2 = Question(survey=survey, text="How are you doing ?")
>>> question2.save()
>>> survey.questions.all()
[<Question: survey-1 - Is it working ?>, <Question: survey-1 - How are you doing ?>]

Test the question API

>>> question1.answer_count
0
>>> question1.choices.all()
[]


Test the creation of a choice

>>> choice1 = Choice(question=question1,text="Yes")
>>> choice1.save()
>>> choice2 = Choice(question=question1,text="No")
>>> choice2.save()

>>> question1.choice_count
2
>>> question1.choices.all()
[<Choice: Yes>, <Choice: No>]

"""
