from p0sx.celery import app


@app.task
def test():
    print("Hello world!")