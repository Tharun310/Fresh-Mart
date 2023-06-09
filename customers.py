from DbConnection import get_sql_connection

def get_all_customers(connection):
    cursor = connection.cursor()
    query = ("select * from customer_details")
    cursor.execute(query)
    response = []
    for (cid, firstname, lastname, email, password, address, city, state, zipcode, country, phone) in cursor:
        response.append({
            'cid': cid,
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': password,
            'address' : address,
            'city' : city,
            'state' : state,
            'zipcode' : zipcode,
            'country' : country,
            'phone' : phone
        })
    return response

def insert_new_customer(connection, cust):
    cursor = connection.cursor()
    query = ("INSERT INTO customer_details "
             "(firstname, lastname, email, password, address, city, state, zipcode, country, phone)"
             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data = (cust['firstname'], cust['lastname'], cust['email'], cust['password'], cust['address'], cust['city'], cust['state'], cust['zipcode'], cust['country'], cust['phone'])

    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid


if __name__ == '__main__':
    connection = get_sql_connection()