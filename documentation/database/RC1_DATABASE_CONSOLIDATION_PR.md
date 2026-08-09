# Draft Pull Request: RC1 Database Consolidation

## Title

Consolidate RC1 database tenant schema

## Base

`codex/rc1-repository-integration`

## Head

`codex/rc1-database-consolidation`

## Summary

This PR consolidates the RC1 database layer after the first reproducible build state.

## Scope

- Adds `025_rc1_database_consolidation.sql` for PostgreSQL and SQLite.
- Seeds `org-local` and `workspace-local`.
- Adds PostgreSQL `sync_queue` parity with SQLite.
- Adds tenant indexes across tenant-owned tables.
- Adds database-level tenant/workspace validation triggers.
- Strengthens the SQLite migration check to verify tenant columns and reject mismatched tenant/workspace inserts.
- Updates migration and smoke-test documentation.

## Local Evidence

- SQLite clean initialization passed through migration `025`.
- Tenant columns present check passed.
- Tenant mismatch rejection check passed.
