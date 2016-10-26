CREATE OR REPLACE FUNCTION {{ old_db_table_name }}_to_{{ new_db_table_name }}_update()
RETURNS TRIGGER AS
$BODY$
BEGIN
    UPDATE {{ new_db_table_name }}
    SET{% for column_name in new_column_names %}{% if column_name not in new_unique_column_names %}
        {{ column_name }} = NEW.{{ column_name }}{% if not forloop.last %},{% endif %}{% endif %}{% endfor %}
    WHERE {{ pk_name }} = NEW.{{ pk_name }};

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;


CREATE TRIGGER {{ old_db_table_name }}_to_{{ new_db_table_name }}_update_trigger
    AFTER UPDATE
    ON {{ old_db_table_name }}
    FOR EACH ROW
    EXECUTE PROCEDURE {{ old_db_table_name }}_to_{{ new_db_table_name }}_update();
