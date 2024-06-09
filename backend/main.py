from fastapi import FastAPI
from model_processor import ModelProcessor
import uvicorn

app = FastAPI()

def main():
    ModelProcessor.process_image()



if __name__ == "__main__":
    main()
    # uvicorn.run(app, host="0.0.0.0", port=8000)
