# Snowball

discord bot to save our syno day.

## Deploy

```sh
docker run -d --name snowball --mount type=bind,src=$(pwd)/conf,dst=/app/conf --mount type=bind,src=$(pwd)/data,dst=/app/data snowball-local
```
