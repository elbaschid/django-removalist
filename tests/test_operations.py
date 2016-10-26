from unittest import mock

from removalist.operations import (CreateTableDuplication,
                                   ReleaseTableDuplication)


def test_create_table_duplicate_initalization():
    op = CreateTableDuplication('testapp.OldModel', 'testapp.NewModel')

    assert op.old_model_name == 'testapp.OldModel'
    assert op.new_model_name == 'testapp.NewModel'

    assert op.state_forwards('testapp', mock.Mock()) is None

    assert op.describe() == ("Create triggers for transitional model renaming: "
                             "testapp.OldModel -> testapp.NewModel")


def test_create_table_duplicate_forward_migration():
    state = mock.Mock()
    schema_editor = mock.Mock()

    op = CreateTableDuplication('testapp.OldModel', 'testapp.NewModel')

    with mock.patch('removalist.operations.builder') as builder:
        op.database_forwards('testapp', schema_editor, state, mock.Mock())

        assert state.apps.get_model.call_count == 2

        assert builder.copy_model_data.call_count == 1
        assert builder.create_insert_trigger.call_count == 1
        assert builder.create_update_trigger.call_count == 1
        assert builder.create_delete_trigger.call_count == 1


def test_create_table_duplicate_backward_migration():
    state = mock.Mock()
    schema_editor = mock.Mock()

    op = CreateTableDuplication('testapp.OldModel', 'testapp.NewModel')

    with mock.patch('removalist.operations.builder') as builder:
        op.database_backwards('testapp', schema_editor, state, mock.Mock())

        assert state.apps.get_model.call_count == 2

        assert builder.drop_insert_trigger.call_count == 1
        assert builder.drop_update_trigger.call_count == 1
        assert builder.drop_delete_trigger.call_count == 1


def test_release_table_duplicate_initalization():
    op = ReleaseTableDuplication('testapp.OldModel', 'testapp.NewModel')

    assert op.old_model_name == 'testapp.OldModel'
    assert op.new_model_name == 'testapp.NewModel'

    assert op.state_forwards('testapp', mock.Mock()) is None

    assert op.describe() == ("Drop triggers for transitional model renaming: "
                             "testapp.OldModel -> testapp.NewModel")


def test_release_table_duplicate_forward_migration():
    state = mock.Mock()
    schema_editor = mock.Mock()

    op = ReleaseTableDuplication('testapp.OldModel', 'testapp.NewModel')

    with mock.patch('removalist.operations.builder') as builder:
        op.database_forwards('testapp', schema_editor, state, mock.Mock())

        assert state.apps.get_model.call_count == 2

        assert builder.drop_insert_trigger.call_count == 1
        assert builder.drop_update_trigger.call_count == 1
        assert builder.drop_delete_trigger.call_count == 1


def test_release_table_duplicate_backward_migration():
    state = mock.Mock()
    schema_editor = mock.Mock()

    op = ReleaseTableDuplication('testapp.OldModel', 'testapp.NewModel')

    with mock.patch('removalist.operations.builder') as builder:
        op.database_backwards('testapp', schema_editor, state, mock.Mock())

        assert state.apps.get_model.call_count == 2

        assert builder.copy_model_data.call_count == 1
        assert builder.create_insert_trigger.call_count == 1
        assert builder.create_update_trigger.call_count == 1
        assert builder.create_delete_trigger.call_count == 1
