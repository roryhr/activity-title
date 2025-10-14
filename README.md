# Activity Title

This is a Django web app to help me rename my Strava activities.

That's it!

## Development Notes

I use conda; it gets the job done. 
```
conda create -n py311 python=3.11
conda activate py311
pip install -r requirements.txt
```

Static files are handled by whitenoise. 


Deployed to http://strava-deck.fly.dev/

## Tests

```
python manage.py collectstatic
python manage.py test
```


# TODOS

1. User management panel where you can delete your account. Log out.
2. Check what privileges were given in the OAuth flow
3. Security 