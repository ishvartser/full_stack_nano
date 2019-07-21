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


def print_top_three_articles(cursor):
    """Execute a query that produces results on the most popular articles."""
    cursor.execute(
        """select title, count(*) from log
        join articles on log.path like '/article/' || articles.slug || ''
        where method='GET' group by title, slug order by count desc limit 3;"""
    )
    results = cursor.fetchall()

    print '\nThe three most popular articles are:'
    for row in results:
        print '"{}" - {} views'.format(row[0], row[1])


def print_most_popular_authors(cursor):
    """Execute a query that produces results on the most popular authors."""
    cursor.execute(
        """select name, count(*) from log join articles on
        log.path = '/article/' || articles.slug
        join authors on articles.author=authors.id
        where method='GET' group by name order by count desc;"""
    )
    results = cursor.fetchall()

    print '\nThe most popular authors are:'
    for row in results:
        print '{} - {} views'.format(row[0], row[1])


def print_error_rates_by_day(cursor):
    """Execute a query that produces results on days with the
    most request error rates."""
    cursor.execute(
        """
        select time, (100.0 * cast(fail_count as decimal) / total)
        as error_rate from
        (
            select time::timestamp::date, count(*) as total,
            sum(case when status like '200%' then 1 else 0 end) success_count,
            sum(case when status like '404%' then 1 else 0 end) fail_count
            from log
            group by time::timestamp::date order by time desc
        ) as subq order by error_rate desc;
        """
    )
    error_results = cursor.fetchall()

    print '\nThe days with the most errors are:'
    for row in error_results:
        if row[1] > 1.0:
            print '{:%b %d, %Y} - {:.2f}% errors'.format(row[0], row[1])


if __name__ == '__main__':
    db = psycopg2.connect(database=DBNAME)
    cursor = db.cursor()
    print_top_three_articles(cursor)
    print_most_popular_authors(cursor)
    print_error_rates_by_day(cursor)
    db.close()
