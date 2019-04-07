import psycopg2
from faker import Faker
from uuid import uuid4
from datetime import datetime, timedelta

# - psql -f db_work/create_dbs.sql -U postgres
# - psql -f db_work/create_hotel_table.sql -U postgres -d db_hotel
# - psql -f db_work/create_fly_table.sql -U postgres -d db_fly
# - psql -f db_work/create_amount_table.sql -U postgres -d db_amount
# - psql -f db_work/drop_dbs.sql -U postgres

# - psql -c "SELECT * FROM amounts" -U postgres -d db_amount
# - psql -c "SELECT * FROM hotel_booking" -U postgres -d db_hotel
# - psql -c "SELECT * FROM fly_booking" -U postgres -d db_fly

def add_values(cur_hotel, cur_fly, values_to_insert):
    hotel_transaction_id = uuid4()
    fly_transaction_id = uuid4()
    transactions = []

    cur_hotel.execute("BEGIN;")
    cur_hotel.execute("INSERT INTO hotel_booking (client_name, hotel_name, arrival_date, departure_date) \
                      VALUES (%s, %s, %s, %s)",
                      (values_to_insert["client_name"],
                       values_to_insert["hotel_name"],
                       values_to_insert["book_date"],
                       values_to_insert["departure_date"]))
    print("Prepare hotel booking transaction", hotel_transaction_id)
    cur_hotel.execute('PREPARE TRANSACTION \'%s\';'%hotel_transaction_id)
    transaction = cur_hotel, hotel_transaction_id
    transactions.append(transaction)

    cur_fly.execute("BEGIN;")
    cur_fly.execute("INSERT INTO fly_booking (client_name, fly_number, fly_from, fly_to, book_date) \
                    VALUES (%s, %s, %s, %s, %s)",
                    (values_to_insert["client_name"],
                     values_to_insert["fly_number"],
                     values_to_insert["fly_from"],
                     values_to_insert["fly_to"],
                     values_to_insert["book_date"]))
    print("Prepare fly booking transaction", fly_transaction_id)
    cur_fly.execute('PREPARE TRANSACTION \'%s\';'%fly_transaction_id)
    transaction = cur_fly, fly_transaction_id
    transactions.append(transaction)

    return transactions

def substract_from_amount(cur_amount, transactions):
    amount_transaction_id = uuid4()
    cur_amount.execute("BEGIN;")
    cur_amount.execute("UPDATE amounts SET amount = amount - 2 WHERE amount_id = 1")
    print("Prepare amount substracting transaction", amount_transaction_id)
    cur_amount.execute('PREPARE TRANSACTION \'%s\';'%amount_transaction_id)
    transaction = cur_amount, amount_transaction_id
    transactions.append(transaction)
    return transactions

def two_pc(cur_hotel, cur_fly, cur_amount):
    faker = Faker()

    values_to_insert = {
        'client_name' : faker.name().replace('\'', '\'\''),
        'fly_number' : faker.sha1(),
        'fly_from' : faker.country_code(),
        'fly_to' : faker.country_code(),
        'book_date' : str(faker.date_time_this_month()),
        'hotel_name' : faker.address().replace('\'', '\'\'').replace('\n', '; '),
        'departure_date' : str(datetime.now() + timedelta(days=faker.random_digit()))
    }

    transactions = []
    try:
        transactions = add_values(cur_hotel, cur_fly, values_to_insert)
        transactions = substract_from_amount(cur_amount, transactions)
    except (psycopg2.InternalError, psycopg2.IntegrityError) as e:
        for cursor, transaction_id in transactions:
            print("Rollback transaction", transaction_id)
            cursor.execute('ROLLBACK PREPARED \'%s\';'%transaction_id)
        transactions = []
        raise e

    for cursor, transaction_id in transactions:
        print("Commit transaction", transaction_id)
        cursor.execute('COMMIT PREPARED \'%s\';'%transaction_id)

def delete_data(cur_hotel, cur_fly, cur_amount):
    cur_hotel.execute('DELETE FROM hotel_booking;')
    cur_fly.execute('DELETE FROM fly_booking;')
    cur_amount.execute('DELETE FROM amounts;')


if __name__ == '__main__':
    conn_hotel = psycopg2.connect(dbname="db_hotel", user='postgres')
    conn_fly = psycopg2.connect(dbname="db_fly", user='postgres')
    conn_amount = psycopg2.connect(dbname="db_amount", user='postgres')
    cur_hotel = conn_hotel.cursor()
    cur_fly = conn_fly.cursor()
    cur_amount = conn_amount.cursor()
    try:
        two_pc(cur_hotel, cur_fly, cur_amount)
    except (psycopg2.InternalError, psycopg2.IntegrityError) as e:
        print("Cannot add entries, because", e)

    cur_hotel.close()
    cur_fly.close()
    conn_hotel.close()
    conn_fly.close()
