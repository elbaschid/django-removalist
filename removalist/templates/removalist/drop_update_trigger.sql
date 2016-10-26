DROP TRIGGER IF EXISTS {{ old_db_table_name }}_to_{{ new_db_table_name }}_update_trigger
     ON {{ old_db_table_name }};

DROP FUNCTION IF EXISTS {{ old_db_table_name }}_to_{{ new_db_table_name }}_update();
