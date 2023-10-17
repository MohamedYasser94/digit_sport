from itertools import chain

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction, IntegrityError
from django.utils.crypto import get_random_string
from slugify import slugify

from core.models.people import Employee
from helper.modelHelper import Active_Status, Absent_Type, Absent_Status

User = get_user_model()


class EmployeeOperationLevel(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='employee_operation_level_sender', blank=True, null=True,
                                     on_delete=models.CASCADE)
    sender_id = models.PositiveIntegerField(blank=True, null=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='employee_operation_level_receiver', blank=True,
                                       null=True, on_delete=models.CASCADE)
    receiver_id = models.PositiveIntegerField(blank=True, null=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='employee_operation_level_owner', blank=True, null=True,
                                    on_delete=models.CASCADE)
    owner_id = models.PositiveIntegerField(blank=True, null=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_operation_level')
    level = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def get_self_name(self):
        if self.node_type == self.NodeType.PEOPLE:
            return f'{self.user.username}'
        else:
            return f'{self.org_unit.name}'

    def __str__(self):
        try:
            if self.node_type == self.NodeType.PEOPLE:
                return f'ID {self.id} | {self.parent.get_self_name()} - {self.user.username}'
            else:
                return f'ID {self.id} | {self.parent.get_self_name()} - {self.name}'
        except AttributeError:
            if self.node_type == self.NodeType.PEOPLE:
                return f'ID {self.id} | {self.user.username}'
            else:
                return f'ID {self.id} | {self.name}'

    @staticmethod
    def get_descendants(node):
        queryset = EmployeeOperationLevel.objects.filter(parent=node)
        results = chain(queryset)
        for child in queryset:
            results = chain(results, node.get_descendants(child))
        return results

    @staticmethod
    def get_ancestors(node):
        if node.parent:
            return chain([node.parent], node.get_ancestors(node.parent))
        return chain()

    @staticmethod
    def get_all_tree_origins():
        return EmployeeOperationLevel.objects.filter(parent=None)

    @staticmethod
    def get_child_nodes(node):
        return EmployeeOperationLevel.objects.filter(parent=node)

    @staticmethod
    def bind_child_nodes_to_parent(node):
        try:
            EmployeeOperationLevel.objects.filter(parent=node).update(parent=node.parent)
        except IntegrityError:
            raise IntegrityError('Failed to update node instance\'s child nodes')

    @staticmethod
    def delete_node(node):
        with transaction.atomic():
            EmployeeOperationLevel.bind_child_nodes_to_parent(node)
            node.delete()


class Attendance(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='attendance_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='attendance_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='attendance_owner', on_delete=models.CASCADE, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_attendance')
    date = models.DateField(blank=True, null=True)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date',)
        verbose_name = 'attendance'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['date']

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Attendance-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Attendance, self).save(*args, **kwargs)


class AttendanceCheck(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='attendance_check_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='attendance_check_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='attendance_check_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_attendance_check')
    date = models.DateField(blank=True, null=True)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date',)
        verbose_name = 'attendance check'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['date']

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AttendanceCheck-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AttendanceCheck, self).save(*args, **kwargs)


class AttendanceHistory(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='attendance_history_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='attendance_history_receiver',
                                       on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='attendance_history_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_attendance_history')
    date = models.DateField(blank=True, null=True)
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date',)
        verbose_name = 'attendance history'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['date']

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AttendanceHistory-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AttendanceHistory, self).save(*args, **kwargs)


class Absent(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='absent_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='absent_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='absent_owner', on_delete=models.CASCADE, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_absent')
    category = models.CharField(max_length=50, choices=Absent_Type, null=True, blank=True)
    approved = models.CharField(max_length=50, choices=Absent_Status, null=True, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date',)
        verbose_name = 'absent'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['date']

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Absent-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Absent, self).save(*args, **kwargs)


class Payroll(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='payroll_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='payroll_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='payroll_owner', on_delete=models.CASCADE, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_payroll')
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    punish = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    absent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    month = models.CharField(max_length=50, null=True, blank=True)
    year = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('employee',)
        verbose_name = 'payroll'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['employee']

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Payroll-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Payroll, self).save(*args, **kwargs)


class PayrollHistory(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='payroll_history_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='payroll_history_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='payroll_history_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_payroll_history')
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    punish = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    absent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    month = models.CharField(max_length=50, null=True, blank=True)
    year = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('employee',)
        verbose_name = 'payroll history'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['employee']

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'PayrollHistory-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(PayrollHistory, self).save(*args, **kwargs)


class Survey(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='survey_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='survey_receiver', on_delete=models.CASCADE, null=True,
                                       blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='survey_owner', on_delete=models.CASCADE, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_survey', null=True,
                                 blank=True)

    title = models.CharField(max_length=50, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    show_count = models.IntegerField(default=0, null=True, blank=True)
    answer_count = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('employee',)
        verbose_name = 'survey'  # verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ['employee']

    def __str__(self):
        return self.employee

    def answer_avg(self):
        return self.answer_count / self.show_count

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Survey-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Survey, self).save(*args, **kwargs)


class SurveyQuestion(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='survey_question_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='survey_question_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='survey_question_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='survey_question', null=True, blank=True)
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('survey',)
        verbose_name = 'survey question'

    def __str__(self):
        return self.survey

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'SurveyQuestion-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SurveyQuestion, self).save(*args, **kwargs)


class SurveyAnswer(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='survey_answer_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='survey_answer_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='survey_answer_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='survey_answer', null=True, blank=True)
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE, related_name='survey_answer_question',
                                 null=True, blank=True)
    answer = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('survey',)
        verbose_name = 'survey answer'

    def __str__(self):
        return self.survey

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'SurveyAnswer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(SurveyAnswer, self).save(*args, **kwargs)


class Appraisal(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='appraisal_sender', on_delete=models.CASCADE, null=True,
                                     blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='appraisal_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='appraisal_owner', on_delete=models.CASCADE, null=True,
                                    blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_appraisal', null=True,
                                 blank=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    reason = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    show_count = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('employee',)
        verbose_name = 'appraisal'

    def __str__(self):
        return self.employee

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'Appraisal-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(Appraisal, self).save(*args, **kwargs)


class AppraisalQuestion(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='appraisal_question_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='appraisal_question_receiver',
                                       on_delete=models.CASCADE, null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='appraisal_question_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name='appraisal_question', null=True,
                                  blank=True)
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    score = models.IntegerField(default=0, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('appraisal',)
        verbose_name = 'appraisal question'

    def __str__(self):
        return self.appraisal

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AppraisalQuestion-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AppraisalQuestion, self).save(*args, **kwargs)


class AppraisalAnswer(models.Model):
    sender_model = models.ForeignKey(ContentType, related_name='appraisal_answer_sender', on_delete=models.CASCADE,
                                     null=True, blank=True)
    sender_id = models.PositiveIntegerField(null=True, blank=True)
    sender = GenericForeignKey('sender_model', 'sender_id')
    receiver_model = models.ForeignKey(ContentType, related_name='appraisal_answer_receiver', on_delete=models.CASCADE,
                                       null=True, blank=True)
    receiver_id = models.PositiveIntegerField(null=True, blank=True)
    receiver = GenericForeignKey('receiver_model', 'receiver_id')
    owner_model = models.ForeignKey(ContentType, related_name='appraisal_answer_owner', on_delete=models.CASCADE,
                                    null=True, blank=True)
    owner_id = models.PositiveIntegerField(null=True, blank=True)
    owner = GenericForeignKey('owner_model', 'owner_id')
    appraisal = models.ForeignKey(Appraisal, on_delete=models.CASCADE, related_name='appraisal_answer', null=True,
                                  blank=True)
    question = models.ForeignKey(AppraisalQuestion, on_delete=models.CASCADE, related_name='appraisal_answer_question',
                                 null=True, blank=True)
    answer = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, null=True, blank=True)
    score = models.IntegerField(default=0, null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Active_Status, default='Active', null=True, blank=True)
    code = models.CharField(max_length=50, null=True, blank=True)
    slug = models.SlugField(null=True, blank=True, max_length=128, unique=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('appraisal',)
        verbose_name = 'appraisal answer'

    def __str__(self):
        return self.appraisal

    def save(self, *args, **kwargs):
        if not self.code and not self.slug:
            code = f'AppraisalAnswer-{get_random_string(5).upper()}'
            self.code = code
            self.slug = slugify(code)
        super(AppraisalAnswer, self).save(*args, **kwargs)


