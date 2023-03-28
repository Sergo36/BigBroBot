import psycopg2
from data.entity.user import User
from data.entity.node import Node

def create_conn():
    return psycopg2.connect(dbname="bla_bla_nodes", user="postgres", password="postgres", host="127.0.0.1", port="5432")


# with conn:
#   with conn.cursor() as cursor:
#      cursor.execute("SELECT * FROM users WHERE telegram_id = %(tid)s", {'tid': 502691086})
#     (id, ) = cursor.fetchone()
#    print(id)


# conn.close()

def get_user(tid):
    res = User()
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE telegram_id = %(tid)s", {'tid': tid})
            temp = cursor.fetchone()
            res.id = temp[0]
            res.telegram_id = temp[1]
            res.telegram_name = temp[2]
    conn.close()
    return res


def getNodes(user_id):
    res = []
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, owner, type, payment_date
                FROM public.nodes
                WHERE owner = %(owner)s"""
            cursor.execute(sql, {'owner': user_id})

            sql_res = cursor.fetchall()
            for row in sql_res:
                temp_node = Node()
                temp_node.id = row[0]
                temp_node.owner = row[1]
                temp_node.type = row[2]
                temp_node.payment_date = row[3]
                res.append(temp_node)
    conn.close()
    return res


def get_nodes_info(node_type, user_id):
    res = []
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT id, owner, type, payment_date
                FROM public.nodes
                WHERE type = %(type)s AND owner = %(owner)s"""
            cursor.execute(sql, {'type': node_type, 'owner': user_id})

            sql_res = cursor.fetchall()
            for row in sql_res:
                temp_node = Node()
                temp_node.id = row[0]
                temp_node.owner = row[1]
                temp_node.type = row[2]
                temp_node.payment_date = row[3]
                res.append(temp_node)
    conn.close()
    return res
