from models import QTYPE_CHOICES, Answer, Survey, Question, Choice
from django.conf import settings
from django.forms import BaseForm, Form, ValidationError
from django.forms import CharField, ChoiceField, SplitDateTimeField,\
                            CheckboxInput, BooleanField,FileInput,\
                            FileField, ImageField
from django.forms import Textarea, TextInput, Select, RadioSelect,\
                            CheckboxSelectMultiple, MultipleChoiceField,\
                            SplitDateTimeWidget,MultiWidget, MultiValueField
from django.forms.forms import BoundField
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.template import Context, loader
from django.template.defaultfilters import slugify

from itertools import chain
import uuid


class BaseAnswerForm(Form):
    def __init__(self, question, user, interview_uuid, session_key, edit_existing=False, *args, **kwdargs):
        self.question = question
        self.session_key = session_key.lower()
        self.user = user
        self.interview_uuid = interview_uuid
        self.answer = None
        initial = None
        if edit_existing:
            if not user.is_authenticated():
                query = question.answers.filter(session_key=session_key)
            else:
                query = question.answers.filter(user=user)
            if query.count():
                self.answer = query[0]
                initial = self.answer.text
                if 'initial' not in kwdargs:
                    kwdargs['initial'] = {}
                if 'answer' not in kwdargs['initial']:
                    kwdargs['initial']['answer'] = self.answer.text
        super(BaseAnswerForm, self).__init__(*args, **kwdargs)
        answer = self.fields['answer']
        answer.required = question.required
        answer.label = question.text
        if not question.required:
            answer.help_text = unicode(_('this question is optional'))
        if initial is not None and initial != answer.initial:
            if kwdargs['initial']['answer'] != answer.initial:
                ## rats.. we are a choice list style and need to map to id.
                answer.initial = initial

    def as_template(self):
        "Helper function for fieldsting fields data from form."
        bound_fields = [BoundField(self, field, name) for name, field in self.fields.items()]
        c = Context(dict(form = self, bound_fields = bound_fields))
        # TODO: check for template ... if template does not exist
        # we could just get_template_from_string to some default
        # or we could pass in the template name ... whatever we want
        # import pdb; pdb.set_trace()
        t = loader.get_template('forms/form.html')
        return t.render(c)

    def save(self, commit=True):
        if not self.cleaned_data['answer']:
            if self.fields['answer'].required:
                raise ValidationError, _('This field is required.')
            return
        ans = self.answer
        if ans is None:
            ans = Answer()
        ans.question = self.question
        ans.session_key = self.session_key
        if self.user.is_authenticated():
            ans.user = self.user
        else:
            ans.user = None
        ans.interview_uuid = self.interview_uuid
        ans.text = self.cleaned_data['answer']
        if commit: ans.save()
        return ans

class TextInputAnswer(BaseAnswerForm):
    answer = CharField()

class TextAreaAnswer(BaseAnswerForm):
    answer = CharField(widget=Textarea)

class NullSelect(Select):
    def __init__(self, attrs=None, choices=(), empty_label=u"---------"):
        self.empty_label = empty_label
        super(NullSelect, self).__init__(attrs, choices)

    def render(self, name, value, attrs=None, choices=(), **kwdargs):
        empty_choice = ()
        # kwdargs is needed because it is the only way to determine if an
        # override is provided or not.
        if 'empty_label' in kwdargs:
            if kwdargs['empty_label'] is not None:
                empty_choice = ((u'', kwdargs['empty_label']),)
        elif self.empty_label is not None:
            empty_choice = ((u'', self.empty_label),)
        base_choices = self.choices
        self.choices = chain(empty_choice, base_choices)
        result = super(NullSelect, self).render(name, value, attrs, choices)
        self.choices = base_choices
        return result

class ChoiceAnswer(BaseAnswerForm):
    answer = ChoiceField(widget=NullSelect)

    def __init__(self, *args, **kwdargs):
        super(ChoiceAnswer, self).__init__(*args, **kwdargs)
        choices = []
        choices_dict = {}
        self.initial_answer = None
        for opt in self.question.choices.all().order_by("order"):
            if opt.image and opt.image.url:
                text = mark_safe(opt.text + '<br/><img src="%s"/>'%opt.image.url)
            else:
                text = opt.text
            if self.answer is not None and self.answer.text == opt.text:
                self.initial_answer = str(opt.id)
            choices.append((str(opt.id),text))
            choices_dict[str(opt.id)] = opt.text
        self.choices = choices
        self.choices_dict = choices_dict
        self.fields['answer'].choices = choices
        self.fields['answer'].initial = self.initial_answer
        if self.initial_answer is not None:
            self.initial['answer'] = self.initial_answer
    def clean_answer(self):
        key = self.cleaned_data['answer']
        if not key and self.fields['answer'].required:
            raise ValidationError, _('This field is required.')
        return self.choices_dict.get(key, key)

class ChoiceRadio(ChoiceAnswer):
    def __init__(self, *args, **kwdargs):
        super(ChoiceRadio, self).__init__(*args, **kwdargs)
        self.fields['answer'].widget = RadioSelect(choices=self.choices)

class ChoiceImage(ChoiceAnswer):
    def __init__(self, *args, **kwdargs):
        super(ChoiceImage, self).__init__(*args, **kwdargs)
        #import pdb; pdb.set_trace()
        self.choices = [ (k,mark_safe(v)) for k,v in self.choices ]
        self.fields['answer'].widget = RadioSelect(choices=self.choices)

class ChoiceCheckbox(BaseAnswerForm):
    answer = MultipleChoiceField(widget=CheckboxSelectMultiple)

    def __init__(self, *args, **kwdargs):
        super(ChoiceCheckbox, self).__init__(*args, **kwdargs)
        choices = []
        choices_dict = {}
        self.initial_answer = None
        for opt in self.question.choices.all().order_by("order"):
            text = opt.text
            if opt.image and opt.image.url:
                text = mark_safe(opt.text + '<br />' + opt.image.url)
            choices.append((str(opt.id),text))
            choices_dict[str(opt.id)] = opt.text
            if self.answer is not None and self.answer.text == opt.text:
                self.initial_answer = str(opt.id)

        self.choices = choices
        self.choices_dict = choices_dict
        self.fields['answer'].choices = choices
        self.fields['answer'].initial = self.initial_answer
        if self.initial_answer is not None:
            self.initial['answer'] = self.initial_answer
    def clean_answer(self):

        keys = self.cleaned_data['answer']
        if not keys and self.fields['answer'].required:
            raise ValidationError, _('This field is required.')
        for key in keys:
            if not key and self.fields['answer'].required:
                raise ValidationError, _('Invalid Choice.')
        return [self.choices_dict.get(key, key) for key in keys]
    def save(self, commit=True):
        if not self.cleaned_data['answer']:
            if self.fields['answer'].required:
                raise ValidationError, _('This field is required.')
            return
        ans_list = []
        for text in self.cleaned_data['answer']:
            ans = Answer()
            ans.question = self.question
            ans.session_key = self.session_key
            if self.user.is_authenticated():
                ans.user = self.user
            else:
                ans.user = None
            ans.interview_uuid = self.interview_uuid
            ans.text = text
            if commit: ans.save()
            ans_list.append(ans)
        return ans_list

## each question gets a form with one element, determined by the type
## for the answer.
QTYPE_FORM = {
    'T': TextInputAnswer,
    'A': TextAreaAnswer,
    'S': ChoiceAnswer,
    'R': ChoiceRadio,
    'I': ChoiceImage,
    'C': ChoiceCheckbox,
}

def forms_for_survey(survey, request, edit_existing=False):
    ## add session validation to base page.
    sp = str(survey.id) + '_'
    session_key = request.session.session_key.lower()
    login_user = request.user
    random_uuid = uuid.uuid4().hex
    if request.POST: # bug in forms
        post = request.POST
    else:
        post = None
    # If there's a question with no answers, it raises a KeyError
    # Let's just pretend there's no question if that happens.
    try:
        return [QTYPE_FORM[q.qtype](q, login_user, random_uuid, session_key, prefix=sp+str(q.id), data=post, edit_existing=edit_existing)
            for q in survey.questions.all().order_by("order") ]
    except KeyError:
        return None

class CustomDateWidget(TextInput):
    class Media:
        js = ('/admin/jsi18n/',
              settings.ADMIN_MEDIA_PREFIX + 'js/core.js',
              settings.ADMIN_MEDIA_PREFIX + "js/calendar.js",
              settings.ADMIN_MEDIA_PREFIX + "js/admin/DateTimeShortcuts.js",
              )

    def __init__(self, attrs={}):
        super(CustomDateWidget, self).__init__(attrs={'class': 'vDateField', 'size': '10'})

class CustomTimeWidget(TextInput):
    class Media:
        js = ('/admin/jsi18n/',
              settings.ADMIN_MEDIA_PREFIX + 'js/core.js',
              settings.ADMIN_MEDIA_PREFIX + "js/calendar.js",
              settings.ADMIN_MEDIA_PREFIX + "js/admin/DateTimeShortcuts.js",
              )


    def __init__(self, attrs={}):
        super(CustomTimeWidget, self).__init__(attrs={'class': 'vTimeField', 'size': '8'})

class CustomSplitDateTime(SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """
    def __init__(self, attrs=None):
        widgets = [CustomDateWidget, CustomTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(u'<p class="datetime">%s %s<br />%s %s</p>' % \
            (_('Date:'), rendered_widgets[0], _('Time:'), rendered_widgets[1]))

class SurveyForm(ModelForm):
    opens = SplitDateTimeField(widget=CustomSplitDateTime(),
                               label=Survey._meta.get_field("opens").verbose_name)
    closes = SplitDateTimeField(widget=CustomSplitDateTime(),
                               label=Survey._meta.get_field("closes").verbose_name)
    class Meta:
        model = Survey
        exclude = ("created_by","editable_by","slug","recipient_type","recipient_id")
    def clean(self):
        title_slug = slugify(self.cleaned_data.get("title"))
        if not hasattr(self,"instance"):
            if not len(Survey.objects.filter(slug=title_slug))==0:
                raise ValidationError, _('The title of the survey must be unique.')
        elif self.instance.title != self.cleaned_data.get("title"):
            if not len(Survey.objects.filter(slug=title_slug))==0:
                raise ValidationError, _('The title of the survey must be unique.')

        return self.cleaned_data

class QuestionForm(ModelForm):
    class Meta:
        model= Question
        exclude = ("survey")

class ChoiceForm(ModelForm):
    class Meta:
        model = Choice
        exclude = ("question")
