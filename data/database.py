import psycopg2
from datetime import datetime
from data.entity.user import User
from data.entity.node import Node
from data.entity.transaction import Transaction
from data.entity.payment import Payment
from data.entity.payment_type import PaymentType


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


def get_user_by_tn(tn) -> User:
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE telegram_name = %(tn)s", {'tn': tn})
            sql_res = cursor.fetchone()
    conn.close()

    if sql_res is None:
        return
    else:
        return User(sql_res)


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


def get_node(node_id):
    res = Node()
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                    SELECT id, owner, type, payment_date, cost
                    FROM public.nodes
                    WHERE id = %(node_id)s"""
            cursor.execute(sql, {'node_id': node_id})

            sql_res = cursor.fetchone()
            res.id = sql_res[0]
            res.owner = sql_res[1]
            res.type = sql_res[2]
            res.payment_date = sql_res[3]
            res.cost = sql_res[4]
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


def get_transactions(user_id):
    res = []
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT transaction_hash, block_hash, block_number, transaction_from, transaction_to, status, owner, value, payments_id
	            FROM public.transaction
                WHERE owner = %(owner)s"""
            cursor.execute(sql, {'owner': user_id})

            sql_res = cursor.fetchall()
            for row in sql_res:
                temp_transaction = Transaction()
                temp_transaction.transaction_hash = row[0]
                temp_transaction.block_hash = row[1]
                temp_transaction.block_number = row[2]
                temp_transaction.transaction_from = row[3]
                temp_transaction.transaction_to = row[3]
                temp_transaction.status = row[4]
                res.append(temp_transaction)
    conn.close()
    return res


def get_payment_data():
    res = ""
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                SELECT wallet_adress
	            FROM public.payment_data
	            WHERE active = true
	            """

            cursor.execute(sql)
            sql_res = cursor.fetchone()
            res = sql_res[0]

    conn.close()
    return res


def get_last_not_paid_payment(user_id, node_id) -> Payment:
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
            SELECT id, node_id, user_id, status, date
	        FROM public.payments
	        WHERE user_id = %(user_id)s AND node_id = %(node_id)s AND Status <> %(status)s
	        ORDER BY date DESC
	        LIMIT 1"""

            cursor.execute(sql, {'user_id': user_id, "node_id": node_id, "status": PaymentType.Paid.value})
            sql_res = cursor.fetchone()

    conn.close()

    if sql_res is None:
        return
    else:
        return Payment(sql_res)


def create_new_payment(user_id, node_id) -> Payment:
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO public.payments(
	            node_id, user_id, status, date)
	            VALUES (%(node_id)s, %(user_id)s, %(status)s, %(date)s)"""

            cursor.execute(sql, {
                'user_id': user_id,
                "node_id": node_id,
                "status": PaymentType.NotPaid.value,
                "date": datetime.now()})
    conn.close()
    return get_last_not_paid_payment(user_id, node_id)

def set_transaction(trn: Transaction, user: User, payment: Payment):
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                    INSERT INTO public.transaction(
	                    transaction_hash, 
	                    block_hash, 
	                    block_number, 
	                    transaction_from, 
	                    transaction_to, 
	                    status, 
	                    owner, 
	                    value, 
	                    payment_id)
	                VALUES (
	                    %(t_hash)s, 
	                    %(b_hash)s,
	                    %(b_number)s, 
	                    %(t_from)s, 
	                    %(t_to)s, 
	                    %(status)s, 
	                    %(owner)s, 
	                    %(value)s, 
	                    %(payment)s);"""

            cursor.execute(sql, {
                't_hash': trn.transaction_hash,
                "b_hash": trn.block_hash,
                "b_number": trn.block_number,
                "t_from": trn.transaction_from,
                't_to': trn.transaction_to,
                'status': True, # to do add request status
                'owner': user.id,
                'value': trn.value,
                'payment': payment.id})
    conn.close()


def get_server_ip(owner: int, node_type: int):
    res = Node()
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                        SELECT id, owner, type, payment_date, cost, server_ip
                        FROM public.nodes
                        WHERE owner = %(owner)s AND type = %(node_type)s"""
            cursor.execute(sql, {'owner' : owner, 'node_type': node_type})

            sql_res = cursor.fetchone()
            res.id = sql_res[0]
            res.owner = sql_res[1]
            res.type = sql_res[2]
            res.payment_date = sql_res[3]
            res.cost = sql_res[4]
            res.server_ip = sql_res[5]
    conn.close()
    return res
