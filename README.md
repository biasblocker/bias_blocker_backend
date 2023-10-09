# Bias Blocker Backend

## Docker Deployment

Copy the code from a local host to server can be done via scp:

```bash
scp -i [SHH_KEY] -r ../bias_blocker_backend/app/ [SERVER_USR]@[SERVER_HOST]:[SERVER_PATH]/bias_blocker_backend
```

```bash
docker image prune -a
docker build -t bias_blocker:latest .
docker run -v $(pwd)/prompts:/app/prompts -p 80:8080 --env-file .env bias_blocker:latest
```
