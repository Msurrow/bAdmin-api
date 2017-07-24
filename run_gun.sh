echo "Setting up ENV"
#export DATABASE_URL='sqlite:///test.db'
export DATABASE_URL='postgresql://localhost'
export TOKEN_GEN_SECRET_KEY='SuperSecretKey'
echo "Running.."
#python badmin_api.py 5000
gunicorn -k sync -w 1 -b 127.0.0.1:5000 badmin_api:app
