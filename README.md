# Bias Blocker Backend

## Docker Deployment
docker image prune -a
docker build -t bias_blocker:latest .
docker run -p 8080:8080 -it $(docker build -q .)
docker run -v $(pwd)/prompts:/app/prompts -p 80:8080 --env-file .env bias_blocker:latest