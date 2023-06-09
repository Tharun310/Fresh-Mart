from DbConnection import get_sql_connection

def get_all_products(connection):
    cursor = connection.cursor()
    query = ("select products.product_id, products.product, products.unit_id, products.price_per_unit, units.unit_name from products inner join units on products.unit_id=units.unit_id")
    cursor.execute(query)
    response = []
    for (product_id, product, unit_id, price_per_unit, unit_name) in cursor:
        response.append({
            'product_id': product_id,
            'product': product,
            'unit_id': unit_id,
            'price_per_unit': price_per_unit,
            'unit_name': unit_name
        })
    return response

def insert_new_product(connection, product):
    cursor = connection.cursor()
    query = ("INSERT INTO products "
             "(product, unit_id, price_per_unit)"
             "VALUES (%s, %s, %s)")
    data = (product['product'], product['unit_id'], product['price_per_unit'])

    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid



def delete_product(connection, product_id):
    cursor = connection.cursor()
    query = ("DELETE FROM products where product_id=" + str(product_id))
    cursor.execute(query)
    connection.commit()

    return cursor.lastrowid



if __name__ == '__main__':
    connection = get_sql_connection()