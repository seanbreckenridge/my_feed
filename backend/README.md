To build, this requires `go` (I set minimum version to `v1.18`, but you can change the `go.mod` file and try with something lower as well).

To build `sqlite3-go`, you also need `gcc`.

```
cd ./go_server
./build
```

This will create a `./go_server/main` executable, which has the `backend` folder embedded in it for configuration. Hence, additional flags to configure should not be needed, but you can always customize if needed:

```
Usage of ./main:
  -db-path string
    	Path to sqlite database file (default "/home/sean/Repos/my_feed/backend/feeddata.sqlite")
  -db-uri string
    	Database URI (overrides db-path)
  -echo
    	Echo SQL queries
  -ftypes-file string
    	Path to feedtypes.json file (default "/home/sean/Repos/my_feed/backend/feedtypes.json")
  -log-requests
    	Log info from HTTP requests to stderr
  -port int
    	Port to listen on (default 5100)
  -root-dir string
    	Root dir for backend (where Pipfile lives) (default "/home/sean/Repos/my_feed/backend")
```
