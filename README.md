# risingstar-backend
backend for rising stars

# to redeploy
1. gcloud config set project rising-stars-backend
2. gcloud run deploy

# to redeploy cloud functions
1. gcloud functions deploy "<FUNCTION NAME HERE>" --runtime python39 --trigger-http    

# How Do I Run This Backend Locally?
3 easy steps to run:
1. flask --app server.py run

# To update requirements.txt
1. pip3 install pipreqs
2. python3 -m pipreqs.pipreqs .# gerpainter-backend
