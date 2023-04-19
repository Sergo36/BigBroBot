import psycopg2
from datetime import datetime
from data.entity.user import User
from data.entity.node import Node
from data.entity.transaction import Transaction
from  data.entity.node_type import NodeTypeClass


def create_conn():
    return psycopg2.connect(dbname="bla_bla_nodes", user="postgres", password="postgres", host="127.0.0.1", port="5432")


# with conn:
#   with conn.cursor() as cursor:
#      cursor.execute("SELECT * FROM users WHERE telegram_id = %(tid)s", {'tid': 502691086})
#     (id, ) = cursor.fetchone()
#    print(id)


# conn.close()

def get_user(tid):
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE telegram_id = %(tid)s", {'tid': tid})
            sql_res = cursor.fetchone()
    conn.close()
    if sql_res is None:
        return
    else:
        return User(sql_res)


def get_user_by_tn(tn) -> User:
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE lower(telegram_name) = LOWER(%(tn)s)", {'tn': tn})
            sql_res = cursor.fetchone()
    conn.close()

    if sql_res is None:
        return
    else:
        return User(sql_res)

def set_user(t_id, t_username) -> User:
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO public.users(
	            telegram_id, telegram_name)
	            VALUES (%(t_id)s, %(t_username)s)"""
            cursor.execute(sql, {'t_id': t_id, 't_username': t_username})
    conn.close()
    return get_user(t_id)



def get_nodes(user_id):
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
    res: Node
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                    SELECT id, owner, type, payment_date, cost, server_ip
                    FROM public.nodes
                    WHERE id = %(node_id)s"""
            cursor.execute(sql, {'node_id': node_id})

            sql_res = cursor.fetchone()
            res = Node().initialisation_sql(sql_res)
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
            sql = Transaction.get_sql() + """WHERE owner = %(owner)s"""

            # sql = """
            #     SELECT transaction_hash, block_hash, block_number, transaction_from, transaction_to, status, decimals, owner, value, node_id
	        #     FROM public.transaction
            #     WHERE owner = %(owner)s"""
            cursor.execute(sql, {'owner': user_id})

            sql_res = cursor.fetchall()
            for row in sql_res:
                temp_transaction = Transaction().initialisation_sql(row)
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


def set_transaction(trn: Transaction, user: User, node: Node):
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
	                    node_id, 
	                    decimals)
	                VALUES (
	                    %(t_hash)s, 
	                    %(b_hash)s,
	                    %(b_number)s, 
	                    %(t_from)s, 
	                    %(t_to)s, 
	                    %(status)s, 
	                    %(owner)s, 
	                    %(value)s, 
	                    %(node)s,
	                    %(decimals)s);"""

            cursor.execute(sql, {
                't_hash': trn.transaction_hash,
                "b_hash": trn.block_hash,
                "b_number": trn.block_number,
                "t_from": trn.transaction_from,
                't_to': trn.transaction_to,
                'status': trn.status,
                'decimals': trn.decimals,
                'owner': user.id,
                'value': trn.value,
                'node': node.id})
    conn.close()


def get_transaction_for_node(node: Node) -> []:
    res = []
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = Transaction.get_sql() + """WHERE transaction.node_id = %(node_id)s"""
            # sql = """
            #     SELECT transaction_hash, block_hash, block_number, transaction_from, transaction_to, status, decimals, owner, value, node_id
            #     FROM public.transaction
            #     WHERE transaction.node_id = %(node_id)s
            # """
            cursor.execute(sql, {'node_id': node.id})
            sql_res = cursor.fetchall()
            for row in sql_res:
                temp_transaction = Transaction().initialisation_sql(row)
                res.append(temp_transaction)
    conn.close()
    return res


def get_server_ip(owner: int, node_type: int):
    res = Node()
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                        SELECT id, owner, type, payment_date, cost, server_ip
                        FROM public.nodes
                        WHERE owner = %(owner)s AND type = %(node_type)s"""
            cursor.execute(sql, {'owner': owner, 'node_type': node_type})

            sql_res = cursor.fetchone()
            res.id = sql_res[0]
            res.owner = sql_res[1]
            res.type = sql_res[2]
            res.payment_date = sql_res[3]
            res.cost = sql_res[4]
            res.server_ip = sql_res[5]
    conn.close()
    return res


def get_nodes_type() -> []:
    res = []
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                        SELECT id, name, discription, cost
	                    FROM public.node_types"""
            cursor.execute(sql)
            sql_res = cursor.fetchall()
            for row in sql_res:
                temp_node_type = NodeTypeClass.initialisation_sql (row)
                res.append(temp_node_type)
    conn.close()
    return res

def get_node_type(type_name: str) -> NodeTypeClass:
    res: NodeTypeClass
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                        SELECT id, name, discription, cost
	                    FROM public.node_types	                    
	                    WHERE lower(name) = LOWER(%(name)s)"""
            cursor.execute(sql, {'name': type_name})
            sql_res = cursor.fetchone()
            res = NodeTypeClass().initialisation_sql(sql_res)
    conn.close()
    return res


def set_node(node_type: NodeTypeClass, owner: User):
    conn = create_conn()
    with conn:
        with conn.cursor() as cursor:
            sql = """
                        INSERT INTO public.nodes(
	                    owner, type, payment_date, cost, server_ip)
	                    VALUES (%(owner_id)s, %(type_id)s, %(payment_date)s, %(cost)s, %(server_ip)s);"""

            cursor.execute(sql, {
                'owner_id': owner.id,
                "type_id": node_type.id,
                "payment_date": datetime.now(),
                "cost": node_type.cost,
                'server_ip': ""})
    conn.close()