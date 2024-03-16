import uvicorn

# import logguru
from loguru import logger
logger.add("./logs/file_{time}.log")

def main():
    # logger.info("Running movie-service")

    uvicorn.run("main:app", host="0.0.0.0", port=6677, reload=True, workers=4)
    logger.info("Running chatLLM-service")

if __name__ == "__main__":
    main()