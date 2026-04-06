# Quizzle

This is an application to create interactive quizzes built with Django + Channels + JS.

This has started as a final Project for the  [CS50 Web development course](https://cs50.harvard.edu/web/) and is still a work in progress.

Beyond the final project, the longterm goal is to host the app and offer a simple and free service to created quizzes and other digital interaction tools for educaion and non-profits. 

### Shortterm Todos:

- Better UI experience
- Better access control to quizzes
-  [x] ~~Add QR code for interactive quizzes~~
- Allow to calculate scores based on speed
- Allow embedding images
- Better control over timelimits and guided quizzes

### Longterm Todos:

- Add other interactive tools
- Choose a nice open source license :)


## Setup environment variables

Copy `example.env` to `.env` and change values

## Run with Docker (not for production)

```bash
docker compose up --build
```

Open http://localhost:8000

## Stop

```bash
docker compose down
```

To also delete the database:

```bash
docker compose down -v
```

## Run locally (SQLite)

```bash
uv run manage.py migrate
uv run manage.py runserver
```
