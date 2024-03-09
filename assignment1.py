import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import s3Connect
import boto3

def init_db_connection():
    conn = sqlite3.connect('/tmp/edcury-de.db')
    return conn


def read_olddata(conn):
    query = """select yearMonth,ProductID as ProductId,salesAmount,percentage_change,yearMonth as Yearmonth_join
                from ProductSalesAmountByMonth
                order by yearMonth desc"""
    df_olddata = pd.read_sql_query(query, conn)
    # print(df_olddata)
    return df_olddata

def read_data(conn):
    df_old = read_olddata(conn)
    query = """
                    SELECT strftime('%Y-%m',a.OrderDate) as yearMonth,c.ProductId as ProductId,c.ProductName,sum(b.UnitPrice * Quantity) as salesAmount
                    FROM `Orders` as a
                    inner join `Order Details` as b
                    on a.OrderID = b.OrderID
                    inner join Products as c
                    on b.ProductID = c.ProductID
                    group by strftime('%Y-%m',a.OrderDate),c.ProductId,c.ProductName
                    order by c.ProductId,strftime('%Y-%m',a.OrderDate)
                """
    
    df = pd.read_sql_query(query, conn)
    df['SalesAmount_PreviousYear'] = df['salesAmount'].shift(1)
    df['percentage_change'] = ((df['salesAmount'] - df['SalesAmount_PreviousYear']) / df['SalesAmount_PreviousYear']) * 100
    
    df_join = pd.merge(df,df_old,how='left',on=['yearMonth','ProductId'])

    df_insert = df_join[df_join["Yearmonth_join"].isnull()]
    df_update = df_join.loc[(df_join["Yearmonth_join"].notnull()) & ((df_join["salesAmount_x"] != df_join["salesAmount_y"]) | (df_join["percentage_change_x"] != df_join["percentage_change_y"]))]
    print(df_update)
    df_col = ["yearMonth","ProductID","ProductName","salesAmount","percentage_change"]

    df_insert = df_insert[["yearMonth","ProductId","ProductName","salesAmount_x","percentage_change_x"]]
    df_insert.columns = df_col
    df_update = df_update[["yearMonth","ProductId","ProductName","salesAmount_y","percentage_change_y"]]
    df_update.columns = df_col
    

    json_data_insert = df_insert.to_json(orient='records')
    json_data_update = df_update.to_json(orient='records')

    json_data_insert = json.loads(json_data_insert)
    json_data_update = json.loads(json_data_update)
    # # df.to_csv("Products.csv",header=True,index=False)
    return json_data_insert,json_data_update

def insertData(conn):
    cursor = conn.cursor()
    data_insert,data_update = read_data(conn)
    for data in data_insert:
        # print(data)
        sql_insert = f"""INSERT INTO ProductSalesAmountByMonth (yearMonth,ProductID,ProductName,salesAmount,percentage_change)
        VALUES (?,?,?,?,?);"""
        # print(sql_upsert)
        cursor.execute(sql_insert,(data['yearMonth'], data['ProductID'], data['ProductName'], data['salesAmount'], data['percentage_change']))
    conn.commit()
    

    for data_upd in data_update:
        sql_update = f"""update ProductSalesAmountByMonth
                            set salesAmount = ?
                            ,percentage_change = ?
                            where yearMonth = ? and ProductID = ?;"""
        # print(sql_upsert)
        cursor.execute(sql_update,(data_upd['salesAmount'],data_upd['yearMonth'], data_upd['percentage_change'],data_upd['ProductID']))
    conn.commit()


def lambda_handler(event, context):
    s3Connect.download_file_from_s3()
    conn = init_db_connection()
    insertData(conn)
    s3Connect.upload_file_to_s3()

    return {
        'statusCode': 200,
        'body': json.dumps('Data processing and updates successfully completed')
    }

