# from io import StringIO
# from traceback import print_tb

from django import forms
from django.shortcuts import render

from .run_query import run_query


class PlaygroundForm(forms.Form):
    model_def = forms.CharField(widget=forms.Textarea)
    query = forms.CharField(widget=forms.Textarea)


def index(request):
    if request.method == 'POST':
        form = PlaygroundForm(request.POST)
        if form.is_valid():
            try:
                qs = run_query(form.cleaned_data.get('model_def'), form.cleaned_data.get('query'))
                context = {
                    'form': form,
                    'sql': qs.query,
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
