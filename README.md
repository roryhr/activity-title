# Activity Title

This is a Django web app that renames Strava activities.
You create them here, they're saved to a database, and then they'll get applied one-by-one automatically within minutes once a Strava activity is created.

That's it! It's free so check it out at 

https://activitytitle.com/

# Development

I'm using Python 3.11 and Django.

```
conda create -n py311 python=3.11
conda activate py311
pip install -r requirements.txt 

python manage.py runserver 
```

Code formatting is handled by `black .` 

Static files are handled by whitenoise. 


Deployed to http://strava-deck.fly.dev/

```
fly deploy
```

## Tests

Run the tests 

```
python manage.py collectstatic
python manage.py test
```


# TODOS

1. User management panel where you can delete your account. Log out.
2. Check what privileges were given in the OAuth flow
3. Security 