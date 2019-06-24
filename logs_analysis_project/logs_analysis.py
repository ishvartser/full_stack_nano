#!/usr/bin/env python2
"""
This module provides analysis on the "news" database.
It answers the following questions:

    1.  What are the most popular three articles of all time?
        (i.e. which articles have been accessed the most?) 
    2.  Who are the most popular article authors of all time? 
        That is, when you sum up all of the articles each author has written, 
        which authors get the most page views? Present this as a sorted 
        list with the most popular author at the top.
    3.  On which days did more than 1% of requests lead to errors?

Author: Igor Shvartser <i.shvartser@gmail.com>
"""

from datetime import datetime
import psycopg2

DBNAME = 'news'


def get_top_three_articles(cursor):
    """Executes a query that produces results on the most popular articles."""
    cursor.execute(
        """select title, count(*) from log 
        join articles on log.path like '/article/' || articles.slug || '' 
        where method='GET' group by title, slug order by count desc limit 3;"""
    )
    results = cursor.fetchall()
    
    print '\nThe three most popular articles are:'
    for row in results:
        print '"{}" - {} views'.format(row[0], row[1])

def get_most_popular_authors(cursor):
    """Executes a query that produces results on the most popular authors."""
    cursor.execute(
        """select name, count(*) from log join articles on log.path 
        like '/article/' || articles.slug || '' 
        join authors on articles.author=authors.id 
        where method='GET' group by name order by count desc;"""
    )
    results = cursor.fetchall()
    
    print '\nThe most popular authors are:'
    for row in results:
        print '{} - {} views'.format(row[0], row[1])

def get_error_rates_by_day(cursor):
    """Executes a query that produces results on days with the most request error rates."""
    cursor.execute(
        """select time::timestamp::date, count(*) from log 
        group by time::timestamp::date order by time desc;"""
    )
    all_results = cursor.fetchall()

    cursor.execute(
        """select time::timestamp::date, count(*) from log 
        where status like '404%' group by time::timestamp::date 
        order by time desc;"""
    )
    error_results = cursor.fetchall()

    error_rates = {}
    for count, row in enumerate(all_results):
        error_rates[error_results[count][0]] =\
            float(error_results[count][1]) * 100.0 / float(row[1])

    print '\nThe days with the most errors are:'
    for k, v in error_rates.iteritems():
        if v > 1.0:
            print '{} - {}% errors'.format(k.strftime("%b %d %Y"), round(v, 2))


if __name__ == '__main__':
    db = psycopg2.connect(database=DBNAME)
    cursor = db.cursor()
    get_top_three_articles(cursor)
    get_most_popular_authors(cursor)
    get_error_rates_by_day(cursor)
    db.close()
