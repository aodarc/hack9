start_app:
	uvicorn api:app

start_dev:
	uvicorn api:app  --reload


start_tests:
	py.test
