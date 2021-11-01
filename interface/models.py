# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
# class Topic(models.Model):
#     name = models.CharField(max_length=100, blank=False, default="Unknown topic")
#     keywords = models.ManyToManyField(Keyword)
#     message = models.TextField(blank = True)
#
#
# class Keyword(models.Model):
#     name = models.CharField(max_length=100, blank=False, default="Unknown keyword")
#
#
# class Document(models.Model):
#     title = models.CharField(max_length=200, blank=False, default="Unknown title")
#     body = models.TextField(blank = True)
#     topics = models.ManyToManyField(Topic)
#     keywords = models.ManyToManyField(Keyword)
#     #relevance = models.
#     message = models.TextField(blank = True)
