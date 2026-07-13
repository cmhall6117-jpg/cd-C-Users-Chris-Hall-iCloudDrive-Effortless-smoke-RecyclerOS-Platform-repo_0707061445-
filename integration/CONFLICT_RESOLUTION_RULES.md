# Conflict Resolution Rules

1. Prefer newest vertical slice file when it expands a feature-specific folder.
2. Do not overwrite shared domain models without comparing fields.
3. Consolidate route imports into one FastAPI main file.
4. Consolidate Flutter routes into one GoRouter configuration.
5. Keep all SQL migrations, preserving numeric order.
6. If duplicate enum names exist, move them into shared domain package and export once.
7. Never delete generated documentation; move superseded docs into archive.
