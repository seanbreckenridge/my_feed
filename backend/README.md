## python

To use the python backend server:

```
cd backend
pipenv install
pipenv run prod
```

See .env.example for environment variables, save as .env

Update the feedtypes.json if needed

That hosts the backend server on port 5100. To allow the frontend to communicate to this, you need to host both publicly. With nginx I do:

```nginx
rewrite ^/feed$ /feed/ permanent;

location /feed/ {
  proxy_pass http://127.0.0.1:4500/feed;
}

location /feed/_next/ {
  # required since the above proxy pass doesnt end with '/'
  proxy_pass http://127.0.0.1:4500/feed/_next/;
}

location /feed_api/ {
  proxy_pass http://127.0.0.1:5100/;
}
```

## golang

You could of course use the python server all the time, but the golang server uses much less memory (20 times less), and is faster.

The golang server serves the information from the database the same way the python server does. It does not create or update the database at all. To accomplish that it runs a python subprocess using the `main.py` file here, by running:

- `pipenv run cli update-db` to update the database whenever pinged to do so (hit `/check` with the `token` header set
- `pipenv run cli update-db --delete-db` to delete the database and create a new one (the equivalent of FEED_REINDEX=1 from the [`index`](../index) script) (hit `/recheck` with the `Authorization` header set)

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
