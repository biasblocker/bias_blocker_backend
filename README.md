# Bias Blocker Backend

This code contains an API to request Llama2 or ChatGPT with the prompts that we developed for BiasBlocker.

## Docker Deployment - API

Copy the code from a local host to server can be done via scp:

```bash
scp -i [SHH_KEY] -r ../bias_blocker_backend/app/ [SERVER_USR]@[SERVER_HOST]:[SERVER_PATH]/bias_blocker_backend
```

The below command builds a docker image, and run it at port 80 by using the external environment:
```bash
docker image prune -a
docker build -t bias_blocker:latest .
docker run -v $(pwd)/prompts:/app/prompts -p 80:8080 --env-file .env bias_blocker:latest
```

## Running with Virtual Environment

if you would like to use Python venv instead of Docker, you can create a virtual environment and then install the
requirements via `pip install -r requirements.txt`.

## Seting up .env file

The API needs an .env file. Your environment settings in .env should be as follows:

```text
ACTIVE=chatgpt-chain
CHAIN_PROMPT_FILE=prompts/chain_prompts
# if you don't want to use chain-prompt use the below settings
PROMPT_FILE=prompts/debias_ar_with_examples_ar_prompts_v2.txt
# setup for the model if you want to use HF
MODEL_NAME=meta-llama/Llama-2-70b-chat
MODEL_TOKEN=HF_API_TOKEN
MAX_NEW_TOKENS=1000
# setup if you want to use OpenAI
OPENAI_API_KEY=OPEN_KEY_API
OPENAI_TEMPERATURE=0.7
CHATGPT_MODEL=gpt-3.5-turbo-1106
PROMPT_LANGUAGE=english % choose english/arabic which are currently supported languages
```

You can check the API documentation {ENDPOINT}/docs.

## Demo of the API

If you don't want to use FastAPI docs for experimenting, you can run the demo folder.
Enter the [demo](/demo) folder, to read the instructions on how you can run the demo UI.

**Note:** Chain-prompt is developed by [@isspek](https://github.com/isspek) after the fellowship. This method is based
on sentence-level bias detection, it is optimized and produces less parsing errors. Currently it only supports ChatGPT.

We are open for contributions and suggestions, please open an issue for discussion.

If you find this repository useful, don't forget to give credits :)