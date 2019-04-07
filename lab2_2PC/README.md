# Work with distributed (two-phase) transactions

To work with distributed (two-phase) PostgreSQL was used
(http://www.postgresql.org/download/).

To perform a distributed transaction,
Distributed Transaction Manager (Coordinator, TM) was  implement.
TM sends the SQL commands with the help of which the distributed transaction is managed,
based on the biphasic fix protocol
(https://en.wikipedia.org/wiki/Two-phase_commit_protocol).

TM is a simple executable application (that was implemented on Python),
in which you need to run a set of SQL queries (or call some methods)
to PostgreSQL.

To imitate a distributed system,
three separate databased were created in PostgreSQL.
One database holds the data (table) for booking airline tickets,
the second database is for hotel booking,
and the third one containg one numeric field that can be interpreted as amount of money left in the account.

Functionality for inserting information about booking of airline ticket and hotel for a specific client was implemented in TM using the biphasic fix protocol.

Here are examples of SQL-queries for performing two-phase transaction:
1. Here's the sequence that two-phase commits:
```
BEGIN;
update mytable set a_col='something' where red_id=1000;
PREPARE TRANSACTION 'foobar';
COMMIT PREPARED 'foobar';
```
2. Here's the sequence that rolls back, leaving the table unchanged:
```
BEGIN;
update mytable set a_col='something' where red_id=1000;
PREPARE TRANSACTION 'foobar';
ROLLBACK PREPARED 'foobar';
```

Both cases were modelled in the application.

#### Additional information:
1. Brief instructions for installing and configuring PostgreSQL: https://github.com/jboss-developer/jboss-developer-shared-resources/blob/master/guides/CONFIGURE_POSTGRESQL.md
2. PostgreSQL commands information for performing a two-phase transaction: https://www.postgresql.org/docs/current/static/sql-prepare-transaction.html
3. In case of blocking due to unsuccessful transaction (`COMMIT PREPARED` or `ROLLBACK PREPARED` commands were not executed), they can be seen by running a SQL query:
`select * from pg_prepared_xacts;`
To unlock, you need to execute a SQL query
`ROLLBACK PREPARED '<gid>';`
or
`COMMIT PREPARED '<gid>';`
4. In the case of a message like
`XAException occurred. XAException contents and details are: The cause is org.postgresql.util.PSQLException: ERROR: Transacted transactions are disabled Error code is: XAER_RMERR (-3). Exception is: Error preparing transaction
Hint: Set max_prepared_transactions to a nonzero value.`
modify the `postgresql.conf` file by setting the option for performing two-phase transactions:
`max_prepared_transactions = 5`
