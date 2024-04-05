# Simple Demo based on Streamlit
The unofficial UI of Bias Blocker for demonstrating the API capabilities, if you don't prefer FastAPI. You can run the demo along with the api locally.

## Installation
Initially, you need to copy the environment file `.env` from the app and add its API endpoint on the file:
```text
% contents from the api's .env
API_ENDPOINT=http://bias_blocker:8080/debias
```

### Run Dockerized Demo
To dockerize the demo, run the following command. You can adjust the settings in the second command based on your preferences.
```shell
docker build -t streamlit .
```


### Virtual Environment
If you don't prefer using Docker, you can create a virtual Python environment. Next you need to install the required libraries via `pip install -r requirements.txt`.

Finally, run the following command:
```shell
streamlit run app.py
```

This demo UI is developed by [isspek](https://github.com/isspek) after the fellowship. 
