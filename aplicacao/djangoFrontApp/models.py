from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    nome = models.CharField(db_column='name', max_length=100, blank=False)
    descricao = models.CharField(db_column='desc', max_length=500, blank=False)
    user = models.ManyToManyField(User)


class Origin(models.Model):
    nome = models.CharField(db_column='name', max_length=100, blank=False)
    descricao = models.CharField(db_column='desc', max_length=500, blank=False)
    tecnologia = models.CharField(db_column='technology', max_length=100, blank=False)
    endpoint = models.CharField(db_column='endpoint', max_length=500, blank=False)
    responsavel = models.CharField(db_column='emailresp', max_length=100, blank=False)


class Metrics(models.Model):
    nome = models.CharField(db_column='name', max_length=100, blank=False)
    projeto = models.ForeignKey(Project, db_column='project', on_delete=models.CASCADE, blank=False)
    origin = models.ForeignKey(Origin, db_column='origin', on_delete=models.CASCADE, blank=False)


class MetricsValues(models.Model):

    metrica = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    valor = models.IntegerField(db_column='value', blank=False)
    tempo = models.IntegerField(db_column='time', blank=False)
    decisao = models.IntegerField(db_column='decision', blank=False)
    cadastrado_por = models.CharField(db_column='add_by', max_length=100, blank=False, default='')


class Ratings(models.Model):
    comment = models.CharField(db_column='comment', max_length=500, blank=False, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')


class Train(models.Model):
    accuracy = models.CharField(db_column='accuracy', max_length=50, blank=False, default='')
    date = models.DateField(db_column='date')
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Prediction(models.Model):
    value_informed = models.IntegerField(db_column='value_informed', blank=False)
    time_informed = models.IntegerField(db_column='time_informed', blank=False)
    result = models.IntegerField(db_column='result', blank=False)
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)


class PasswordChanges(models.Model):
    new_pwd = models.CharField(db_column='new_pwd', max_length=15, blank=False, default='')
    date = models.DateField(db_column='date')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
