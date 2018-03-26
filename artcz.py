#!/usr/bin/env python3

"""
This is djamix based static website code powering artcz.pl
"""

from datetime import datetime

import djamix
from markdown import markdown
from django.template import Template, Context
from django.urls import reverse
from django.test import Client  # RequestFactory


class Article(djamix.DjamixModel):

    class Meta:
        data_file = 'articles.yaml'

    def get_absolute_url(self):
        return reverse('article', kwargs={'slug': self.slug})

    def get_content(self):
        return markdown(self.content or self.render_content_file_as_template())

    def get_content_from_file(self):
        with open(self.content_file, 'r') as file:
            return file.read()

    def render_content_file_as_template(self):
        return Template(self.get_content_from_file()).render(Context())

    def get_output_filename(self):
        """For static gen only"""
        return "articles/%s.html" % self.slug


def get_all_articles():
    return Article.objects.all().order_by('-pub_date')


def get_article(slug):
    return Article.objects.get(slug=slug)


def _response_from_the_url(url):
    """
    Here set up request factory and test client(?)
    """
    return Client().get(url).content.decode()


@djamix.register_command
def build():
    start = datetime.now()

    OUTPUT = {
        # "about.html": "/about/",
        "index.html": "/",
        "articles/index.html": "/articles/",
    }

    def build_filename(filename):
        BUILD_PREFIX = "./_build/"
        return BUILD_PREFIX + filename

    # then add all the other articles
    for article in Article.objects.all():
        OUTPUT[article.get_output_filename()] = article.get_absolute_url()

    for filename, url in OUTPUT.items():
        f = build_filename(filename)
        print("Building %s from %s" % (f, url))
        with open(f, 'w') as a_file:
            a_file.write(_response_from_the_url(url))

    print("==================")
    print("Build completed in %s" % (datetime.now() - start))


urls = [
    {'name': 'homepage',
     'path': '/',
     'template_name': 'index.html',
     'description': "Showe homepage"},

    {'name': 'articles',
     'path': '/articles/',
     'template_name': 'articles/list.html',
     'description': "Show all the articles"},

    {'name': 'article',
     'path': '/articles/<slug>/',
     'template_name': 'articles/detail.html',
     'description': 'Show single article'},
]


djamix.start(urls, locals())
