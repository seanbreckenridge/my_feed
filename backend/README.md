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
