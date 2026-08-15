# Google Reviews System

This project stores Google Business rating data and the latest Google reviews in the database. The homepage only reads from MySQL/PostgreSQL/SQLite and never calls Google during a page request.

## Environment Variables

Add these to `.env` in development and to your Render/cPanel environment variables in production:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
GOOGLE_PLACE_ID=your_google_place_id
```

The API key is used only by server-side Django code.

## Install And Migrate

```bash
pip install -r requirements.txt
python manage.py makemigrations main
python manage.py migrate
python manage.py collectstatic --noinput
```

## Manual Sync

```bash
python manage.py sync_google_reviews
```

You can also sync from Django Admin:

1. Go to Admin.
2. Open Google Business.
3. Click Sync Now.

## Automatic Sync

The existing scheduler command now runs Google reviews daily at 2:00 AM:

```bash
python manage.py start_scheduler
```

On Render, run this as a background worker. On cPanel, either keep the scheduler process running if supported or add a cron job:

```bash
python /path/to/manage.py sync_google_reviews --quiet
```

## Homepage

The homepage renders `templates/components/google_reviews.html` using saved database records only. If Google is down, the site continues to show the last saved reviews.

## SEO

When reviews exist, the homepage outputs JSON-LD for:

- Dentist/Organization
- AggregateRating
- Review
