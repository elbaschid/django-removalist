CREATE OR REPLACE FUNCTION {{ old_db_table_name }}_to_{{ new_db_table_name }}_insert()
RETURNS TRIGGER AS
$BODY$
BEGIN
    INSERT INTO {{ new_db_table_name }} ({% for column_name in new_column_names %}
        {{ column_name }}{% if not forloop.last %},{% endif %}{% endfor %}
    )
    VALUES ({% for column_name in new_column_names %}
        NEW.{{ column_name }}{% if not forloop.last %},{% endif %}{% endfor %}
    );

    RETURN NEW;
END;
$BODY$
LANGUAGE plpgsql;


CREATE TRIGGER {{ old_db_table_name }}_to_{{ new_db_table_name }}_insert_trigger
  AFTER INSERT
  ON {{ old_db_table_name }}
  FOR EACH ROW
  EXECUTE PROCEDURE {{ old_db_table_name }}_to_{{ new_db_table_name }}_insert();
