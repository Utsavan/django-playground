# from io import StringIO
# from traceback import print_tb

import sqlparse
from django import forms
from django.shortcuts import render

from .run_query import run_query


class PlaygroundForm(forms.Form):
    model_def = forms.CharField(widget=forms.Textarea)
    query = forms.CharField(widget=forms.Textarea)


def index(request):
    if 'model_def' in request.GET:
        form = PlaygroundForm(request.GET)
        if form.is_valid():
            try:
                qs = run_query(form.cleaned_data.get('model_def'), form.cleaned_data.get('query'))
                context = {
                    'form': form,
                    'sql': sqlparse.format(str(qs.query), reindent=True),
                }
            except Exception as e:
                # output = StringIO()
                # print_tb(e.__traceback__, file=output)
                context = {
                    'form': form,
                    # 'error': output.getvalue(),
                    'error': str(e),
                }
    else:
        context = {
            'form': PlaygroundForm(),
        }

    return render(request, template_name='playground/playground.html', context=context)
