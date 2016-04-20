# UPSERT scraper

Accompanying article: http://p.epij.nl/postgresql/heroku/2016/04/20/sidestepping-heroku-limits-with-postgresql-upsert/

## Addons

```
$ heroku addons

Add-on                                         Plan       Price
─────────────────────────────────────────────  ─────────  ─────
heroku-postgresql (postgresql-graceful-65275)  hobby-dev  free
 └─ as DATABASE

scheduler (scheduler-trapezoidal-14878)        standard   free
 └─ as SCHEDULER

sendgrid (sendgrid-horizontal-56807)           starter    free
 └─ as SENDGRID
 ```
 
### Heroku scheduler settings

Every 10 minutes:

    curl -s "http://example.com" | python scraper.py --recipients you@example.com,friend@example.com --subject "Website changed"
