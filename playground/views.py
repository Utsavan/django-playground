# from io import StringIO
# from traceback import print_tb
from django import forms
from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState
from django.db.models.query import QuerySet
from django.shortcuts import render


class PlaygroundForm(forms.Form):
    model_def = forms.CharField(widget=forms.Textarea)
    query = forms.CharField(widget=forms.Textarea)


def run_query(model_def, query):
    exec(model_def)

    loader = MigrationLoader(None, ignore_no_migrations=True)
    to_state = ProjectState.from_apps(apps)

    autodetector = MigrationAutodetector(
        from_state=loader.project_state(),
        to_state=to_state,
        questioner=NonInteractiveMigrationQuestioner('playground'),
    )
    changes = autodetector.changes(
        graph=loader.graph,
        trim_to_apps={'playground'},
        convert_apps={'playground'},
    )

    connection = connections[DEFAULT_DB_ALIAS]
    migration = changes['playground'][0]

    with connection.schema_editor(atomic=migration.atomic) as schema_editor:
        migration.apply(project_state=to_state, schema_editor=schema_editor)

    return eval(query)


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
