# Strava Deck? 

This is a Django web app that renames Strava activities.

That's it! It's free so check it out at 

https://activitytitle.com/

## Development Notes

Python 3.11

```
Python 3.11
Django 5.0.7
whitenoise  6.7.0
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
2. Check what privedges were given in the OAuth flow
3. Security 