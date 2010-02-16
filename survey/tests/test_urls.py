test_cases = r"""

>>> from django.test.client import Client
>>> c = Client()

# Test the view that list the visible surveys
>>> response = c.get("/survey/visible/")
>>> response.status_code #visible surveys
200

# Access a view protected by login_required decorator
# It should redirect me '302'
>>> response = c.get("/survey/editable/")
>>> response.status_code #editable surveys
302

>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user(username="test_urls",email="t@t.fr",password="test_urls")
>>> user.save()
>>> c.login(username="test_urls",password="test_urls")
True

# Note that since now I am authentified I am not redirected
>>> response = c.get("/survey/editable/")
>>> response.status_code
200

Add a survey::

>>> response = c.post("/survey/add/",
... {"title":"test survey addition",
... "opens_0":"2000-12-12", "opens_1":"12:12:12",
... "closes_0":"2099-12-12", "closes_1":"12:12:12",
... "visible":"on", "public":"on","allows_multiple_interviews":"on"})
>>> response.status_code
302

>>> response = c.get("/survey/editable/")
>>> response.content.find("test survey addition") > -1
True

Update a survey::
>>> response =  c.post("/survey/update/test-survey-addition/",
... {"title":"test survey update",
... "opens_0":"2000-12-12", "opens_1":"12:12:12",
... "closes_0":"2099-12-12", "closes_1":"12:12:12",
... "visible":"on", "public":"on","allows_multiple_interviews":"on"})
>>> response.status_code
302
>>> response = c.get("/survey/editable/")
>>> response.content.find("test survey update") > -1
True



Add a question with a radio list representation::

>>> response =  c.post("/survey/question/add/test-survey-update/",
... {"qtype":"R","required":"on",
... "text" : "test question radio list"})
>>> response.status_code
302

Add two choices::
TODO: Remove the magic number 3, it comes from the question_id previously added

>>> response =  c.post("/survey/choice/add/3/",
... {"text" : "yes"})
>>> response.status_code
302
>>> response =  c.post("/survey/choice/add/3/",
... {"text" : "no"})
>>> response.status_code
302

Add an interview ::

>>> response = c.get("/survey/detail/test-survey-update/")
>>> response.status_code
200
>>> response = c.post("/survey/detail/test-survey-update/",
... {"2_3-answer":4})
>>> response.status_code
302
>>> response = c.post("/survey/detail/test-survey-update/",
... {"2_3-answer":4})
>>> response.status_code
302
>>> response = c.post("/survey/detail/test-survey-update/",
... {"2_3-answer":3})
>>> response.status_code
302
>>> response = c.get("/survey/answers/test-survey-update/")
>>> response.status_code
200
>>> response.content.find("33%")>-1
True
>>> response.content.find("67%")>-1
True

Update a question ::

>>> response = c.post("/survey/question/update/test-survey-update/3/",
... {"qtype":"R","required":"on",
... "text" : "test question radio list -- modified"})
>>> response.status_code
302
>>> response = c.get("/survey/detail/test-survey-update/")
>>> response.content.find("test question radio list -- modified") > -1
True

Update a choice::

>>> response = c.post("/survey/choice/update/3/3/",
... {"text": "may be"})
>>> response.status_code
302
>>> response = c.get("/survey/detail/test-survey-update/")
>>> response.content.find("may be") > -1
True


Delete a survey ::
>>> response =  c.post("/survey/delete/test-survey-update/")
>>> response.status_code
302
>>> response = c.get("/survey/editable/")
>>> response.content.find("test survey update") == -1
True


"""
