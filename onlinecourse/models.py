import sys
from django.utils.timezone import now
from datetime import datetime
from datetime import date
from django.utils.translation import gettext_lazy as _

try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings
import uuid
from model_utils import FieldTracker
from django.utils.timezone import now as djnow

Account = settings.AUTH_USER_MODEL


# Instructor model
class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)
    tracker = FieldTracker()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    STUDENT = 'student'
    DEVELOPER = 'developer'
    DATA_SCIENTIST = 'data_scientist'
    DATABASE_ADMIN = 'dba'
    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)
    tracker = FieldTracker()

    def __str__(self):
        return self.user.username + "," + \
               self.occupation


# Course model
class Course(models.Model):
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)
    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Enrollment')
    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False
    grade = models.IntegerField(default=80,
                                null=True,
                                blank=True)
    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)

    tracker = FieldTracker()

    def __str__(self):
        return "Name: " + self.name + "," + \
               "Description: " + self.description

    def all_questions(self):
        return Question.objects.filter(course=self)


# Lesson model
class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(Account,
                                   on_delete=models.SET_DEFAULT,
                                   default=None,
                                   null=True,
                                   blank=True,
                                   related_name='%(app_label)s_%(class)s_created_by')
    updated_by = models.ForeignKey(Account,
                                   on_delete=models.SET_DEFAULT,
                                   default=None,
                                   null=True,
                                   blank=True,
                                   related_name='%(app_label)s_%(class)s_modified_by')
    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)
    tracker = FieldTracker()

    def __str__(self):
        return self.title


# Enrollment model
# <HINT> Once a user enrolled a class, an enrollment entry should be created between the user and course
# And we could use the enrollment to track information such as exam submissions
class Enrollment(models.Model):
    AUDIT = 'audit'
    HONOR = 'honor'
    BETA = 'BETA'
    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)

    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)
    tracker = FieldTracker()

    def __str__(self):
        return str(f"[{self.user.username}] - {self.course.name}")

    def questions(self):
        return self.course.all_questions()


class Question(models.Model):
    question_text = models.TextField(null=False,
                                     default="",
                                     blank=True)
    lesson = models.ForeignKey(Lesson,
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    course = models.ForeignKey(Course,
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    # choice_set = models.ManyToManyField(Choice,
    #                                     blank=True)
    # grade = models.CharField(default="0",
    #                          max_length=2048,
    #                          null=True,
    #                          blank=True)
    grade = models.IntegerField(default=1,
                                null=True,
                                blank=True)
    created_by = models.ForeignKey(Account,
                                   on_delete=models.SET_DEFAULT,
                                   default=None,
                                   null=True,
                                   blank=True,
                                   related_name='%(app_label)s_%(class)s_created_by')
    updated_by = models.ForeignKey(Account,
                                   on_delete=models.SET_DEFAULT,
                                   default=None,
                                   null=True,
                                   blank=True,
                                   related_name='%(app_label)s_%(class)s_modified_by')
    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)
    choices = []
    tracker = FieldTracker()

    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers == selected_correct:
            return True
        else:
            return False

    def all_choices(self):
        return Choice.objects.filter(question=self)

    def correct_choices(self):
        return Choice.objects.filter(question=self, is_correct=True)

    # <HINT> A sample model method to calculate if learner get the score of the question
    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers == selected_correct:
            return True
        else:
            return False


class Choice(models.Model):
    choice_text = models.TextField(null=True,
                                   blank=True)
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE,
                                 null=True)


# <HINT> Create a Question Model with:
# Used to persist question content for a course
# Has a One-To-Many (or Many-To-Many if you want to reuse questions) relationship with course
# Has a grade point for each question
# Has question content
# Other fields and methods you would like to design
# class Question(models.Model):
# Foreign key to lesson
# question text
# question grade/mark


#  <HINT> Create a Choice Model with:
# Used to persist choice content for a question
# One-To-Many (or Many-To-Many if you want to reuse choices) relationship with Question
# Choice content
# Indicate if this choice of the question is a correct one or not
# Other fields and methods you would like to design
class ChoiceAnswer(models.Model):
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return str(f"[{self.question.question_text}] [{self.choices}]")

    def correct_choices(self):
        return self.choices.filter(is_correct=True)

    def all_correct_choices(self):
        return self.question.correct_choices()

    def all_choices(self):
        return self.choices.all()

    def get_mark(self):
        mark = len(self.correct_choices()) / len(self.all_correct_choices())
        print(f"[{self.question.question_text}] mark = {mark}")
        return mark

# <HINT> The submission model
# One enrollment could have multiple submission
# One submission could have multiple choices
# One choice could belong to multiple submissions
class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
    choices_answer = models.ManyToManyField(ChoiceAnswer)
    updated_by = models.ForeignKey(Account,
                                   on_delete=models.SET_DEFAULT,
                                   default=None,
                                   null=True,
                                   blank=True,
                                   related_name='%(app_label)s_%(class)s_modified_by')
    created_date = models.DateField(default=date.today,
                                    help_text=_('Ngày chỉnh sửa gần nhất'),
                                    )

    updated_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ chỉnh sửa gần nhất'),
                                      )
    created_at = models.DateTimeField(default=djnow,
                                      help_text=_('Ngày giờ được tạo, không thể sửa đổi'),
                                      editable=False)
    tracker = FieldTracker()

    def __str__(self):
        return str(f"[Submission] {self.enrollment}")

    def get_mark(self):
        mark = 0
        for choice_answer in self.choices_answer.all():
            mark += choice_answer.get_mark()

        print(f"[get_mark] mark = {mark}")
        return mark

    def get_grade(self):
        return self.get_mark() / self.count_questions()

    def count_questions(self):
        return len(self.enrollment.questions())

    #
    # def correct_answers(self):
    #     results = []
    #     for c in self.choices.all():
    #         results.append(c.choice_text)
    #     return results

    def answers(self):
        results = []
        for c in self.choices_answer.all():
            results.append(c.choice_text)
        return results

    def questions(self):
        results = self.enrollment.questions()
        return results

    def choices_answers(self):
        results = self.choices_answer.all()
        return results