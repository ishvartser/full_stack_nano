# logs_analysis.py

## Design

This module provides three methods for analysis on the `news` database, a collection of articles, authors, and logs related to a news organization.

Running the module is easy! Assuming you've [downloaded the data](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) and have `PostgreSQL` installed and configured, simply run the following: 

```bash
python logs_analysis.py
```
**Note:** the `logs_analysis` module is compatible with `python-2.7.12` at this time only.

The output you'll see will have answers to three questions, namely:

1.  What are the most popular three articles of all time? (i.e. which articles have been accessed the most?) 

2.  Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views? Present this as a sorted list with the most popular author at the top.

3.  On which days did more than 1% of requests lead to errors?

## Sample Output

A successful execution of the module will give results similar to:

```bash
The three most popular articles are:
"Candidate is jerk, alleges rival" - 338647 views
"Bears love berries, alleges bear" - 253801 views
"Bad things gone, say good people" - 170098 views

The most popular authors are:
Ursula La Multa - 507594 views
Rudolf von Treppenwitz - 423457 views
Anonymous Contributor - 170098 views
Markoff Chaney - 84557 views

The days with the most errors are:
Jul 17 2016 - 2.26% errors
```

## Database

The `news` database includes the following tables:

* The `authors` table includes information about the authors of articles.
* The `articles` table includes the articles themselves.
* The `log` table includes one entry for each time a user has accessed the site.
