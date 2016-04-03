import datetime
import difflib
import os
import psycopg2
import pytz

def diff(after, before=None):
    if not before:
        return None

    diff = difflib.context_diff(before[1].splitlines(True),
                                after[1].splitlines(True),
                                str(before[0]),
                                str(after[0]))
    return list(diff)

def scrape(body, timestamp=None, database_url=None):
    assert timestamp
    path = os.path.join(os.path.dirname(__file__), 'query.sql')
    with open(path) as f:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(f.read(), (body, timestamp))
                results = cur.fetchall()
                return diff(*results)

def main():
    database_url  = os.environ['DATABASE_URL']
    sender        = os.environ['FROM']
    sendgrid_pass = os.environ['SENDGRID_PASSWORD']
    sendgrid_user = os.environ['SENDGRID_USERNAME']
    timezone      = pytz.timezone(os.environ['TZ'])

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--recipients', required=True)
    parser.add_argument('--subject', required=True)
    args = parser.parse_args()

    import sys
    body = sys.stdin.read()

    timestamp = datetime.datetime.now(timezone)
    diff = scrape(body, database_url=database_url, timestamp=timestamp)

    if not diff:
        return

    import sendgrid
    sg = sendgrid.SendGridClient(sendgrid_user, sendgrid_pass)
    message = sendgrid.Mail(to=args.recipients,
                            subject=args.subject,
                            text=''.join(diff),
                            from_email=sender)
    status, msg = sg.send(message)
    if status is not 200:
        sys.exit(1)

if __name__ == "__main__":
    main()
