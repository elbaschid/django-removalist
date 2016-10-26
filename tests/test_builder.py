import pytest

from django.db import models

from removalist import builder


class NewModel(models.Model):
    text = models.TextField()
    number = models.IntegerField()
    group = models.ForeignKey('auth.Group')

    class Meta:
        db_table = 'testapp_newmodel'


class OldModel(models.Model):
    text = models.TextField()
    number = models.IntegerField()
    group = models.ForeignKey('auth.Group')

    class Meta:
        db_table = 'testapp_oldmodel'


def test_create_context_for_new_model():
    context = builder.get_context_from_model(NewModel, 'new')

    assert sorted(['new_db_table_name',
                   'new_column_names',
                   'pk_name',
                   'new_unique_column_names']) == sorted(context.keys())

    assert context['pk_name'] == 'id'
    assert context['new_unique_column_names'] == ['id']
    assert context['new_db_table_name'] == 'testapp_newmodel'
    assert sorted(context['new_column_names']) == sorted(['id',
                                                          'text',
                                                          'number',
                                                          'group_id'])


@pytest.mark.parametrize('event', ('insert', 'update', 'delete'))
def test_create_trigger_statement_generation(event):
    statement = builder.create_trigger(event, OldModel, NewModel)
    assert statement == globals()['CREATE_{}_TRIGGERS'.format(event.upper())]

    shortcut_function = getattr(builder, 'create_{}_trigger'.format(event))
    statement = shortcut_function(OldModel, NewModel)
    assert statement == globals()['CREATE_{}_TRIGGERS'.format(event.upper())]


@pytest.mark.parametrize('event', ('insert', 'update', 'delete'))
def test_drop_trigger_statement_generation(event):
    statement = builder.drop_trigger(event, OldModel, NewModel)
    assert statement == globals()['DROP_{}_TRIGGERS'.format(event.upper())]

    shortcut_function = getattr(builder, 'drop_{}_trigger'.format(event))
    statement = shortcut_function(OldModel, NewModel)
    assert statement == globals()['DROP_{}_TRIGGERS'.format(event.upper())]


def test_copy_table_statement():
    statement = builder.copy_model_data(OldModel, NewModel)
    assert statement == globals()['COPY_TABLE']


CREATE_INSERT_TRIGGERS = """CREATE OR REPLACE FUNCTION testapp_oldmodel_to_testapp_newmodel_insert()
RETURNS TRIGGER AS
$BODY$
BEGIN
    INSERT INTO testapp_newmodel (
        id,
        text,
        number,
        group_id
    )
    VALUES (
        NEW.id,
        NEW.text,
        NEW.number,
        NEW.group_id
    );

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;


CREATE TRIGGER testapp_oldmodel_to_testapp_newmodel_insert_trigger
  AFTER INSERT
  ON testapp_oldmodel
  FOR EACH ROW
  EXECUTE PROCEDURE testapp_oldmodel_to_testapp_newmodel_insert();
"""

DROP_INSERT_TRIGGERS = """DROP TRIGGER IF EXISTS testapp_oldmodel_to_testapp_newmodel_insert_trigger
     ON testapp_oldmodel;

DROP FUNCTION IF EXISTS testapp_oldmodel_to_testapp_newmodel_insert();
"""


CREATE_UPDATE_TRIGGERS = """CREATE OR REPLACE FUNCTION testapp_oldmodel_to_testapp_newmodel_update()
RETURNS TRIGGER AS
$BODY$
BEGIN
    UPDATE testapp_newmodel
    SET
        text = NEW.text,
        number = NEW.number,
        group_id = NEW.group_id
    WHERE id = NEW.id;

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;


CREATE TRIGGER testapp_oldmodel_to_testapp_newmodel_update_trigger
    AFTER UPDATE
    ON testapp_oldmodel
    FOR EACH ROW
    EXECUTE PROCEDURE testapp_oldmodel_to_testapp_newmodel_update();
"""

DROP_UPDATE_TRIGGERS = """DROP TRIGGER IF EXISTS testapp_oldmodel_to_testapp_newmodel_update_trigger
     ON testapp_oldmodel;

DROP FUNCTION IF EXISTS testapp_oldmodel_to_testapp_newmodel_update();
"""

CREATE_DELETE_TRIGGERS = """CREATE OR REPLACE FUNCTION testapp_oldmodel_to_testapp_newmodel_delete()
RETURNS TRIGGER AS
$BODY$
BEGIN
    DELETE FROM testapp_newmodel
    WHERE OLD.id = id;

    RETURN OLD;
END;
$BODY$
LANGUAGE plpgsql;


CREATE TRIGGER testapp_oldmodel_to_testapp_newmodel_delete_trigger
    AFTER DELETE
    ON testapp_oldmodel
    FOR EACH ROW
    EXECUTE PROCEDURE testapp_oldmodel_to_testapp_newmodel_delete();
"""

DROP_DELETE_TRIGGERS = """DROP TRIGGER IF EXISTS testapp_oldmodel_to_testapp_newmodel_delete_trigger
     ON testapp_oldmodel;

DROP FUNCTION IF EXISTS testapp_oldmodel_to_testapp_newmodel_delete();
"""

COPY_TABLE = """INSERT INTO testapp_newmodel (
    SELECT
        id,
        text,
        number,
        group_id
    FROM testapp_oldmodel)
ON CONFLICT (id) DO
    UPDATE
        SET
            text = EXCLUDED.text,
            number = EXCLUDED.number,
            group_id = EXCLUDED.group_id;
"""
