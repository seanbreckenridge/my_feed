## python

To use the python backend server:

```
cd backend
pipenv install
pipenv run prod

See .env.example for environment variables, save as .env
```

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

You could of course use the python server all the time, but the golang server uses much less memory and is faster.

All the golang server does is serve the information from the database the exact same way the python server does. It does not create or update the database at all. To accomplish that it runs a python subprocess using the `main.py` file here, by running:

- `pipenv run cli update-db` to update the database whenever pinged to do so
- `pipenv run cli update-db --delete-db` to delete the database and create a new one (the equivalent of FEED_REINDEX=1 from the [`index`](../index) script)

TODO: actually write the golang server
