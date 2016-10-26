INSERT INTO {{ new_db_table_name }} (
    SELECT{% for column_name in new_column_names %}
        {{ column_name }}{% if not forloop.last %},{% endif %}{% endfor %}
    FROM {{ old_db_table_name }})
ON CONFLICT ({{ pk_name }}) DO
    UPDATE
        SET{% for column_name in new_column_names %}{% if column_name not in new_unique_column_names %}
            {{ column_name }} = EXCLUDED.{{ column_name }}{% if not forloop.last %},{% endif %}{% endif %}{% endfor %};
