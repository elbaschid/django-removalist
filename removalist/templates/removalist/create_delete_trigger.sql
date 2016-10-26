CREATE OR REPLACE FUNCTION {{ old_db_table_name }}_to_{{ new_db_table_name }}_delete()
RETURNS TRIGGER AS
$BODY$
BEGIN
    DELETE FROM {{ new_db_table_name }}
    WHERE OLD.{{ pk_name }} = {{ pk_name }};

    RETURN OLD;
END;
$BODY$
LANGUAGE plpgsql;


CREATE TRIGGER {{ old_db_table_name }}_to_{{ new_db_table_name }}_delete_trigger
    AFTER DELETE
    ON {{ old_db_table_name }}
    FOR EACH ROW
    EXECUTE PROCEDURE {{ old_db_table_name }}_to_{{ new_db_table_name }}_delete();
