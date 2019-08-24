import operator
from functools import reduce
from django.http import Http404
from django.shortcuts import render
from django.core.paginator import Paginator, Page, EmptyPage, PageNotAnInteger
from crispy_forms import helper
from elasticsearch import TransportError
from elasticsearch_dsl.query import Q

from blog.models import Post, User
from .documents import PostDocument
from .helpers import DateInput, SearchResults
from .forms import SearchForm


def post_list(request):
    paginate_by = 20

    search = PostDocument.search()

    form = SearchForm(data=request.GET)
    form.helper = helper.FormHelper()
    form.helper.form_tag = False
    form.helper.disable_csrf = True

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            search = search.query(
                Q('match', title=query) |
                Q('nested', path='author', query=Q('match', author__username=query)) |
                Q('nested', path='author', query=Q('match', author__first_name=query)) |
                Q('nested', path='author', query=Q('match', author__last_name=query))
            )
        title = form.cleaned_data['title']
        if title:
            search = search.query('match_phrase', title=title)
        body = form.cleaned_data['body']
        if body:
            search = search.query('match', body=body)
        users = form.cleaned_data['users']
        if users:
            users_queries = []
            for user in users:
                users_queries.append(
                    Q('nested', path='author', query=Q('match', author__pk=user.pk))
                )
            search = search.query(reduce(operator.ior, users_queries))
        created_from = form.cleaned_data['created_from']
        if created_from:
            search = search.filter('range', created={'gte': created_from})

        created_till = form.cleaned_data['created_till']
        if created_till:
            search = search.filter('range', created={'lte': created_till})

    search = search.highlight('title')
    search_results = SearchResults(search)

    paginator = Paginator(search_results, paginate_by)
    page_number = request.GET.get('page')
    try:
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page parameter is not an integer, show first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page parameter is out of range, show last existing page.
            page = paginator.page(paginator.num_pages)
    except TransportError:
        raise Http404('Index does not exist. Run `python manage.py search_index --rebuild` to create it.')

    context = {
        'object_list': page,
        'form': form
    }

    return render(request, 'search/post_list.html', context)
