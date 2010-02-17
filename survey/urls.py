from django.conf.urls.defaults import patterns, url
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list_detail import object_list
from django.conf.urls.defaults import *

from views import answers_list, answers_detail,\
                survey_detail, survey_edit, survey_add,\
                editable_survey_list, survey_update,\
                question_add, question_update,\
                choice_add, choice_update, delete_image,\
                visible_survey_list, object_delete


urlpatterns = patterns('',

    url(r'^visible/$', visible_survey_list, name='surveys-visible'),
    url(r'^editable/$', editable_survey_list, name='surveys-editable'),

    url(r'^detail/(?P<survey_slug>[-\w]+)/$', survey_detail,   name='survey-detail'),

    url(r'^answers/(?P<survey_slug>[-\w]+)/$',
        answers_list,    name='survey-results'),
    url(r'^answers/(?P<survey_slug>[-\w]+)/(?P<key>[a-fA-F0-9]{10,40})/$',
        answers_detail,  name='answers-detail'),

    url(r'^edit/(?P<survey_slug>[-\w]+)/$', survey_edit,   name='survey-edit'),
    url(r'^add/$', survey_add,   name='survey-add'),
    url(r'^update/(?P<survey_slug>[-\w]+)/$', survey_update,   name='survey-update'),
    url(r'^delete/(?P<survey_slug>[-\w]+)/$', object_delete, {'object_type': 'survey', }, name='survey-delete'),

    url(r'^question/add/(?P<survey_slug>[-\w]+)/$', question_add,   name='question-add'),
    url(r'^question/update/(?P<survey_slug>[-\w]+)/(?P<question_id>\d+)/$', question_update,   name='question-update'),
    url(r'^question/delete/(?P<survey_slug>[-\w]+)/(?P<object_id>\d+)/$', object_delete, {'object_type': 'question', }, name='question-delete'),


    url(r'^choice/add/(?P<question_id>\d+)/$', choice_add,   name='choice-add'),
    url(r'^choice/update/(?P<question_id>\d+)/(?P<choice_id>\d+)/$', choice_update,   name='choice-update'),
    url(r'^choice/delete/(?P<survey_slug>[-\w]+)/(?P<object_id>\d+)/$', object_delete, {'object_type': 'choice', }, name='choice-delete'),

    url(r'^delete_image/(?P<model_string>[-\w]+)/(?P<object_id>\d+)/$', delete_image, name='delete-image'),
    )
