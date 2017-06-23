import ast
import threading

from django.apps import apps
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState

local_data = threading.local()


class ModelNodeVisitor(ast.NodeVisitor):
    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr == 'Model' and base.value.id == 'models':
                    local_data.collected_models.append(node)
                    local_data.collected_model_names.append(node.name)


def find_model(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Call):
        return find_model(node.func)
    elif isinstance(node, ast.Attribute):
        return find_model(node.value)


def find_models_from_binop(node):
    rv = []

    if isinstance(node.left, ast.Call):
        rv += [find_model(node.left)]
    elif isinstance(node.left, ast.BinOp):
        rv += find_models_from_binop(node.left)

    if isinstance(node.right, ast.Call):
        rv += [find_model(node.right)]
    elif isinstance(node.right, ast.BinOp):
        rv += find_models_from_binop(node.right)

    return rv


def extract_safe_orm_ast(model_def):
    tree = ast.parse(model_def, mode='exec')
    ModelNodeVisitor().visit(tree)
    new_tree = ast.Module([ast.ImportFrom('django.db', [ast.alias(name='models', asname=None)], 0)] + local_data.collected_models)
    return ast.fix_missing_locations(new_tree)


def extract_safe_orm_query_ast(query):
    tree = ast.parse(query, mode='eval')

    if isinstance(tree.body, ast.BinOp):
        model_names = find_models_from_binop(tree.body)
        if set(local_data.collected_model_names).issuperset(set(model_names)):
            return tree

    elif isinstance(tree.body, ast.Call):
        model_name = find_model(tree.body)
        if model_name in local_data.collected_model_names:
            return tree

    raise Exception('No query to work with')


def run_query(model_def, query):
    local_data.collected_models = []
    local_data.collected_qs_expression = None
    local_data.collected_model_names = []
    exec(compile(extract_safe_orm_ast(model_def), filename='<ast>', mode='exec'))

# these migrations may not be needed afterall
#
#    loader = MigrationLoader(None, ignore_no_migrations=True)
#    to_state = ProjectState.from_apps(apps)
#
#    autodetector = MigrationAutodetector(
#        from_state=loader.project_state(),
#        to_state=to_state,
#        questioner=NonInteractiveMigrationQuestioner('playground'),
#    )
#    changes = autodetector.changes(
#        graph=loader.graph,
#        trim_to_apps={'playground'},
#        convert_apps={'playground'},
#    )
#
#    connection = connections[DEFAULT_DB_ALIAS]
#    migration = changes['playground'][0]
#
#    with connection.schema_editor(atomic=migration.atomic) as schema_editor:
#        migration.apply(project_state=to_state, schema_editor=schema_editor)

    return eval(compile(extract_safe_orm_query_ast(query), filename='<ast>', mode='eval'))
