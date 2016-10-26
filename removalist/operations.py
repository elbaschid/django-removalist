import structlog

from django.db.migrations.operations.base import Operation

from . import builder

log = structlog.get_logger('removalist.operations')


def execute_create_triggers(schema_editor, old_model, new_model):
    """
    Execute all the SQL statements required to copy data between the tables
    underlying the *old_model* and *new_model*. This will create a new
    transaction and imposes a write lock on the entire table for the duration
    of the data sync and setup of the triggers.
    """
    schema_editor.execute('BEGIN ISOLATION LEVEL REPEATABLE READ;')

    # We want to acquire an exclusive lock on the old table while we are copying
    # the data over to the new table, avoiding entries being added before the
    # new triggers are being setup.
    schema_editor.execute(
        'LOCK TABLE {} IN EXCLUSIVE MODE;'.format(old_model._meta.db_table))

    schema_editor.execute(builder.copy_model_data(old_model, new_model))

    schema_editor.execute(builder.create_insert_trigger(old_model, new_model))
    schema_editor.execute(builder.create_update_trigger(old_model, new_model))
    schema_editor.execute(builder.create_delete_trigger(old_model, new_model))

    schema_editor.execute('COMMIT;')


def execute_drop_triggers(schema_editor, old_model, new_model):
    """
    Execute all the SQL statements required to drop the triggers setup for the
    table sync in `execute_create_triggers`. The statements will be executed
    in a transaction and will only be committed if the can all be applied
    successfully.
    """
    schema_editor.execute('BEGIN ISOLATION LEVEL REPEATABLE READ;')

    schema_editor.execute(builder.drop_insert_trigger(old_model, new_model))
    schema_editor.execute(builder.drop_update_trigger(old_model, new_model))
    schema_editor.execute(builder.drop_delete_trigger(old_model, new_model))

    schema_editor.execute('COMMIT;')


class CreateTableDuplication(Operation):
    """
    Copy model data from old table to new table and create triggers.

    Allow moving a Django model from one app to another requires slightly more
    effort than Django's migrations allow. This custom operation allows us to
    setup duplicate tables for two models (the old one and the new one) and then
    have data inserted, updated or deleted in the old table, being replicated
    in the new table. This will allow the old and the new code to run in
    on the same setup during the transition.

    .. warning::

        This only works in one direction, regarding the data sync between
        tables. After switching to the new code version only using the new
        model/table will result in potential data loss if a switch to the old
        code version is required.
    """
    reversible = True

    def __init__(self, old_model_name, new_model_name):
        self.old_model_name = old_model_name
        self.new_model_name = new_model_name

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        try:
            old_model = from_state.apps.get_model(self.old_model_name)
        except LookupError:
            log.warning("old model no longer available, we assume it's because "
                        "you are removing the model. If not, there's an issue "
                        "and you should check it out.",
                        old_model=self.old_model_name,
                        new_model=self.new_model_name)
            return

        new_model = from_state.apps.get_model(self.new_model_name)

        execute_create_triggers(schema_editor, old_model, new_model)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        try:
            old_model = from_state.apps.get_model(self.old_model_name)
        except LookupError:
            log.warning("old model no longer available, we assume it's because "
                        "you are removing the model. If not, there's an issue "
                        "and you should check it out.",
                        old_model=self.old_model_name,
                        new_model=self.new_model_name)
            return

        new_model = from_state.apps.get_model(self.new_model_name)

        execute_drop_triggers(schema_editor, old_model, new_model)

    def state_forwards(self, app_label, state):
        """ Overriding this method is required. """
        pass

    def describe(self):
        return "Create triggers for transitional model renaming: {} -> {}".format(
            self.old_model_name,
            self.new_model_name)


class ReleaseTableDuplication(Operation):
    """
    Release the triggers setup in the CreateTableDuplication operation.
    """
    reversible = True

    def __init__(self, old_model_name, new_model_name):
        self.old_model_name = old_model_name
        self.new_model_name = new_model_name

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        try:
            old_model = from_state.apps.get_model(self.old_model_name)
        except LookupError:
            log.warning("old model no longer available, we assume it's because "
                        "you are removing the model. If not, there's an issue "
                        "and you should check it out.",
                        old_model=self.old_model_name,
                        new_model=self.new_model_name)
            return

        new_model = from_state.apps.get_model(self.new_model_name)

        execute_drop_triggers(schema_editor, old_model, new_model)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        try:
            old_model = from_state.apps.get_model(self.old_model_name)
        except LookupError:
            log.warning("old model no longer available, we assume it's because "
                        "you are removing the model. If not, there's an issue "
                        "and you should check it out.",
                        old_model=self.old_model_name,
                        new_model=self.new_model_name)
            return

        new_model = from_state.apps.get_model(self.new_model_name)

        execute_create_triggers(schema_editor, old_model, new_model)

    def state_forwards(self, app_label, state):
        """ Overriding this method is required. """
        pass

    def describe(self):
        return "Drop triggers for transitional model renaming: {} -> {}".format(
            self.old_model_name,
            self.new_model_name)
