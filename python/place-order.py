#!/usr/bin/python
import requests, json, time

base_rest_url = "https://test.cofacecentraleurope.com/api/bi/v1/"

headers = {'accept': 'application/json','content-type': 'application/json', 'charset' : 'UTF-8'}

api_key = '8842ace2-e377-48d9-b129-f952950ea535'


def search_for_company(params):
    print ""
    print "searching for company..."
    parameters = {'api_key': api_key}
    response = requests.get(base_rest_url + "companies?" + params, params=parameters, headers=headers)
    if (response.status_code == 200):
        return response.json()
    else:
        raise ValueError("server returned http status %d (%s)" % (response.status_code, response.text))  

def get_order_details(id):
    print ""
    print "fetching order details..."
    parameters = {'api_key': api_key}
    response = requests.get(base_rest_url + "order/" + id, params=parameters, headers=headers)
    if (response.status_code == 200):
        return response.json()
    else:
        raise ValueError("server returned http status %d (%s)" % (response.status_code, response.text))  

def list_order_documents(id):
    print ""
    print "fetching list of order documents..."
    parameters = {'api_key': api_key}
    response = requests.get(base_rest_url + "order/" + id + "/documents", params=parameters, headers=headers)
    if (response.status_code == 200):
        return response.json()
    else:
        raise ValueError("server returned http status %d (%s)" % (response.status_code, response.text))  

def get_order_document(id, file_name):
    print ""
    print "fetching order document..."
    parameters = {'api_key': api_key}
    response = requests.get(base_rest_url + "order/" + id + "/document/" + file_name, params=parameters, headers=headers)
    if (response.status_code == 200):
        return response.content
    else:
        raise ValueError("server returned http status %d (%s)" % (response.status_code, response.text))  

def place_order_immediate(product, company_id, format):
    print ""
    print "placing immediate order..."
    data = json.dumps(
        {
            "customer_reference": "testref-313",
            "company_id": company_id,
            "product_details": {
                "product_code": product,
                'language': 'EN',
                'format': format,
            },
            "credit_report_details": {
                'research_instructions': 'immediate_no_research'
            },
        })
    parameters = {'api_key': api_key}
    response = requests.post(base_rest_url + "orders/creditreport", params=parameters, headers=headers, data=data)
    if (response.status_code == 202):
        return response.json()
    else:
        raise ValueError("server returned http status %d (%s)" % (response.status_code, response.text))  


def section(title):
    print ""
    print ""
    print "===== " + title + " ====="
    print ""



section("Company search")

companies = search_for_company("country_iso_code=PL&company_name=Hydrobudowa&limit=5")
print "Company search result list:"
for company in companies:
    print "  {0}: {1}".format(company['company_id'], company['company_name'])
company_id = companies[0]['company_id']
print ""
print "Found {0} companies with name Hydrobudowa in PL; first one has company_id {1}".format(len(companies), company_id)


section("Placing an order")

immediate_order_response = place_order_immediate(200, company_id, 'html')
immediate_order_guid = immediate_order_response['id']
print ""
print "Immediate order placed; order ID is " + immediate_order_guid


section("Waiting for the order to finish")

finished = False
while not finished:
    print "Order not finished yet, waiting..."
    time.sleep(1)
    order_details = get_order_details(immediate_order_guid)
    finished = (order_details['order_status'] == 'finished' or order_details['order_status'] == 'cancelled')

print "Immediate order finished"


section("Retrieving report document")

documents = list_order_documents(immediate_order_guid)
print ""
print "Order documents list:"
for document in documents:
    print "  {0}".format(document['file_name'])

report = get_order_document(immediate_order_guid, documents[0]['file_name'])
print ""
print "Downloaded report has a length of {0} characters, showing first 500:".format(len(report))
print report[:500]
print "..."

