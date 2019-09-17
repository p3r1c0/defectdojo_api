#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright 2019
#
# Authors: Pedro Galindo
# @p3r1c0
from defectdojo_api import defectdojo
import os, traceback
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

# setup DefectDojo connection information
global api
defectdojo_url = os.getenv('DEFECTDOJO_URL')
defectdojo_api_key = os.getenv('DD_API_KEY')
defectdojo_user = os.getenv('DEFECTDOJO_USER')

# instantiate the DefectDojo api wrapper
api = defectdojo.DefectDojoAPI(defectdojo_url, defectdojo_api_key, defectdojo_user, debug=False)

# method to get the connection directly with dd bbdd
def get_connection_defect():
    conn = None
    try:
        conn = psycopg2.connect(dbname=os.getenv('DEFECT_BBDD_NAME'), user=os.getenv('DEFECT_BBDD_USER'),
                                password=os.getenv('DEFECT_PASS'), host=os.getenv('DEFECT_BBDD_HOST'), port=os.getenv('DEFECT_BBDD_PORT'), sslmode='require')

        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

# method to get product_type dict via bbdd
def get_product_type_bbdd_dojo():
    conn = None
    try:
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_product_type")
        prod_type_dict = [dict((cur.description[i][0], value)
                                  for i, value in enumerate(row)) for row in cur.fetchall()]
        prod_type_dict_f = {}
        for prod_type in prod_type_dict:
            prod_type_dict_f[prod_type['id']] = prod_type['name']
        return prod_type_dict_f
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()

# method to get test_types dict via bbdd
def get_test_type_bbdd_dojo():
    conn = None
    try:
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_test_type")
        test_type_dict = [dict((cur.description[i][0], value)
                                  for i, value in enumerate(row)) for row in cur.fetchall()]
        test_type_dict_f = {}
        for test_type in test_type_dict:
            test_type_dict_f[test_type['id']] = test_type['name']
        return test_type_dict_f
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()

# method to get all products via bbdd
def get_products_bbdd_dojo():
    conn = None
    try:
        prod_type = get_product_type_bbdd_dojo()
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_product")
        products_list = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]
        for product in products_list:
            product['prod_type_name'] = prod_type[product['prod_type_id']]
            if product['name'] == 'Misc' or product['name'] == 'VULN SCANNING':
                product['name'] = product['name'] + ' - ' + product['prod_type_name']

        return products_list
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()

# method to get a product if exists via bbdd
def get_product_bbdd_dojo(product_name, product_type_id):
    conn = None
    try:
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_product WHERE name = '%s' AND prod_type_id = '%s' " % (product_name, product_type_id))
        product = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]

        return product[0]
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()

# method to get all products via bbdd
def get_engagements_bbdd_dojo():
    conn = None
    try:
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_engagement")
        engagements_list = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]

        return engagements_list
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()

# method to get findings of specific test depending severity via bbdd
def get_findings_bbdd_dojo_severity(test_id, severity):
    conn = None
    try:
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_finding WHERE test_id = '%s' and severity = '%s'" % (test_id, severity))
        findings_list = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]

        return len(findings_list)
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()

# method to get a product if exists via bbdd
def get_engagement_bbdd_dojo(product_id, engagement_name):
    conn = None
    try:
        conn = get_connection_defect()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM dojo_engagement WHERE name = '%s' AND product_id = '%s'" % (engagement_name, product_id))
        engagemet = [dict((cur.description[i][0], value)
                            for i, value in enumerate(row)) for row in cur.fetchall()]

        return engagemet[0]
    except:
        print('Error type: %s\n\n' % traceback.format_exc())
    finally:
        if conn is not None:
            conn.close()
            
#List Products via API
def listProducts():
    try:
        products = api.list_products(limit=None)
        if products.success:
            print(products.data_json(pretty=True))  # Decoded JSON object
            return products
        else:
            print(products.message)
            return None
    except:
        print('Error type: %s\n\n' % traceback.format_exc())

# method to get product_type id from product type value
def getIdProductType(product_type_dicc, product_type_value):
    try:
        for key in product_type_dicc:
            if product_type_dicc[key] == product_type_value:
                return key
        return None
    except:
        print('Error type: %s\n\n' % traceback.format_exc())

## method to check if already exists an product (DP-ID)
# def selectedExistingProduct(products, product_type, product_name):
#     try:
#         for product in products.data["objects"]:
#             if product_type == product['prod_type'] and product_name == product['name']: #s'hauria de fer mappetj de prod_type 1-Research and Development, 2-ZAP Scans..
#             ##if product_name == product['name']:
#                 return product
#         return None
#     except:
#         print('Error type: %s\n\n' % traceback.format_exc())

# method to get product id depending if this product already or not exists
def getProductId(selectedProduct, product_name, product_type_id):
    try:
        if selectedProduct and selectedProduct is not None: ##si existe el producto
            print("This DP-ID already exists: "+ selectedProduct['name']) 
            print(selectedProduct)  
            return selectedProduct['id']
        else:
            ## create the product
            newProduct = api.create_product(product_name, product_name + " - Product", product_type_id)
            if newProduct.success:
                # Get the product id
                print("Product successfully created." )
                return newProduct.id()
            else:
                print("Error creating product: " + str(newProduct.success))
                return None
    except:
        print('Error type: %s\n\n' % traceback.format_exc())

# method to list engagements via API
def listEngagements():
    try:
        engagements = api.list_engagements()
        if engagements.success:
            print(engagements.data_json(pretty=True))  # Decoded JSON object
            return engagements
        else:
            print(engagements.message)
            return None
    except:
        print('Error type: %s\n\n' % traceback.format_exc())

# method to select existing engagement if already exists
# def selectedExistingEngagement(engagements, product_id, engagement_name):
#     try:
#         for engagement in engagements.data["objects"]:
#             print(str(product_id) +" "+ str(engagement['product_id']) +" "+ engagement_name +" "+ engagement['name'])
#             if product_id == engagement['product_id'] and engagement_name == engagement['name']:
#                 return engagement
#         return None
#     except:
#         print('Error type: %s\n\n' % traceback.format_exc())

# method to get engagement_id of specific engagement
def getEngagementId(selectedEngagement, product_id, engagement_name):
    try:
        if selectedEngagement:       
            print("This Engagement already exists: "+ selectedEngagement['name'])   
            return selectedEngagement['id']  
        else:
            ## TODO: change status, target start, target end?
            timeEngDelta = datetime.now() + timedelta(days=180)
            newEngagement = api.create_engagement(name=engagement_name, product_id=product_id, lead_id=1, status="In Progress", target_start=datetime.now().strftime('%Y-%m-%d'), target_end=timeEngDelta.strftime('%Y-%m-%d'))
            if newEngagement.success:
                print("Engagement successfully created with an id: " + str(newEngagement))
                return newEngagement.id()
            else:
                print(newEngagement)
                return None
    except:
        print('Error type: %s\n\n' % traceback.format_exc())

# method to upload scan to defectdojo
def uploadScan(engagement_id, file, scan_type, active="True", scan_date=datetime.now().strftime('%Y-%m-%d'), severity='Medium'):
    try:
        severities = ['Low', 'Info', 'Medium', 'High', 'Critical']
        if severity in severities:
            test_type_dict = get_test_type_bbdd_dojo()
            if scan_type in test_type_dict.values():
                upload_file = api.upload_scan(engagement_id=engagement_id, file=file, active=active, scan_date=scan_date, scan_type=scan_type, minimum_severity=severity)
                return upload_file
            else:
                print("ERROR... this test type doesn't exist")
        else:
            print("ERROR... this severity: " + severity + " doesn't exist")
    except:
        print('Error type: %s\n\n' % traceback.format_exc())