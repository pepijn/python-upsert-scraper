import datetime
import difflib
import os
import psycopg2
import pytz
import re
from bs4 import BeautifulSoup

def diff(after, before=None):
    if not before:
        return None

    diff = difflib.context_diff(before[1].splitlines(True),
                                after[1].splitlines(True),
                                str(before[0]),
                                str(after[0]))
    return list(diff)

def scrape(body, timestamp, database_url=None):
    query_path = os.path.join(os.path.dirname(__file__), 'query.sql')
    select_path = os.path.join(os.path.dirname(__file__), 'select.sql')

    with open(query_path) as q:
        with open(select_path) as s:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor() as cur:
                    query = re.sub('([^:]):\w+', '\\1%s', q.read())
                    cur.execute(query + s.read(), (body, timestamp))
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
    parser.add_argument('--link', required=True)
    args = parser.parse_args()

    import sys
    body = BeautifulSoup(sys.stdin.read(), 'html.parser')

    timestamp = datetime.datetime.now(timezone)
    diff = scrape(body.prettify(), timestamp, database_url=database_url)

    if not diff:
        return

    import sendgrid
    sg = sendgrid.SendGridClient(sendgrid_user, sendgrid_pass)
    message = sendgrid.Mail(subject=args.subject,
                            text=''.join(args.link).join(diff),
                            from_email=sender)
    for to in args.recipients.split(','):
        message.add_to(to)
    status, msg = sg.send(message)
    print(msg)
    if status is not 200:
        sys.exit(1)

if __name__ == "__main__":
    main()
