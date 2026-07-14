# RecyclerOS Pro Mobile

The RC1 Flutter baseline implements the local operational path from sign-in
through inventory intake.

## Run

```text
flutter pub get
flutter run
```

## Validate

```text
flutter analyze
flutter test
```

## RC1 State Boundary

The app currently uses Riverpod process-local state and the shared
`recycleros_domain` package. Live authentication and API transport are deferred;
the typed routes and workflow controller provide the boundary for those later
integrations.
