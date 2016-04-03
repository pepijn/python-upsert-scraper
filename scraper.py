def diff(after, before=None):
    if not before:
        return None

    from difflib import context_diff
    diff = context_diff(before[1].splitlines(True),
                        after[1].splitlines(True),
                        str(before[0]),
                        str(after[0]))
    return list(diff)

def query(query, params=(), database_url=None):
    from psycopg2 import connect
    with connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

def scrape(body, timestamp=None, database_url=None):
    if not timestamp:
        from datetime import datetime
        timestamp = datetime.now()

    with open('query.sql') as f:
        result = query(f.read(),
                       params=(body, timestamp),
                       database_url=database_url)
        return diff(*result)

def message(body):
    import sendgrid
    message = sendgrid.Mail()
    message.add_to('John Doe ')
    message.set_subject('Example')
    message.set_text(body)
    message.set_from('Doe John ')

    return message
