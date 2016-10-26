import structlog

from django.template.loader import get_template

log = structlog.get_logger(__name__)


def get_context_from_model(model, prefix, ignore_unique=False):
    column_names = []
    unique_column_names = []

    for field in model._meta.fields:
        name = field.get_attname_column()[0]

        if field.unique:
            unique_column_names.append(name)

        column_names.append(name)

    return {
        '{}_db_table_name'.format(prefix): model._meta.db_table,
        '{}_column_names'.format(prefix): column_names,
        '{}_unique_column_names'.format(prefix): unique_column_names,
        'pk_name': model._meta.pk.attname
    }


def drop_trigger(event, old_model, new_model):
    event = event.lower()

    template = get_template('removalist/drop_{}_trigger.sql'.format(event))

    context = get_context_from_model(new_model, 'new')
    context.update(get_context_from_model(old_model, 'old'))

    statement = template.render(context)
    log.debug('drop {} trigger statement'.format(event),
              sql_statement=statement)

    return statement


def create_trigger(event, old_model, new_model):
    event = event.lower()

    old_column_names = [f.get_attname_column()[0]
                        for f in old_model._meta.fields]
    new_column_names = [f.get_attname_column()[0]
                        for f in new_model._meta.fields]

    assert sorted(old_column_names) == sorted(new_column_names), \
        "{} <=> {}".format(old_column_names, new_column_names)

    template = get_template('removalist/create_{}_trigger.sql'.format(event))

    ignore_unique = bool(event == 'update')

    context = get_context_from_model(new_model, 'new', ignore_unique)
    context.update(get_context_from_model(old_model, 'old', ignore_unique))

    statement = template.render(context)
    log.debug('create {} trigger statement'.format(event),
              sql_statement=statement)

    return statement


def create_insert_trigger(old_model, new_model):
    return create_trigger('insert', old_model, new_model)


def create_update_trigger(old_model, new_model):
    return create_trigger('update', old_model, new_model)


def create_delete_trigger(old_model, new_model):
    return create_trigger('delete', old_model, new_model)


def drop_insert_trigger(old_model, new_model):
    return drop_trigger('insert', old_model, new_model)


def drop_update_trigger(old_model, new_model):
    return drop_trigger('update', old_model, new_model)


def drop_delete_trigger(old_model, new_model):
    return drop_trigger('delete', old_model, new_model)


def copy_model_data(old_model, new_model):
    old_column_names = [f.get_attname_column()[0]
                        for f in old_model._meta.fields]
    new_column_names = [f.get_attname_column()[0]
                        for f in new_model._meta.fields]

    assert sorted(old_column_names) == sorted(new_column_names), \
        "{} <=> {}".format(old_column_names, new_column_names)

    template = get_template('removalist/copy_table.sql')

    context = get_context_from_model(new_model, 'new')
    context.update(get_context_from_model(old_model, 'old'))

    statement = template.render(context)
    log.debug('copy {} -> {} statement'.format(old_model, new_model),
              sql_statement=statement)

    return statement
