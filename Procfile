web: gunicorn -k sync -w 4 --log-level=DEBUG -b 0.0.0.0:$PORT badmin_api:app
#web: python badmin_api.py $PORT