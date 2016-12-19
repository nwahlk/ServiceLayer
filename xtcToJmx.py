# -*- coding: utf-8 -*-
from xml.dom import minidom
import simplejson as json
import os

#precheck for xtc if meet requirements
def pre_check(element):
	# If xtc not contain OBJECT, no need to parse it
	if(len(element.getElementsByTagName('OBJECT')) <= 1):
		return 0
	# Not support method such as cancel.
	for object in element.getElementsByTagName('action'):
		method = object.getAttribute('Method')
		if method not in ('add','Add','update','Update','remove','Remove'):
			return 0
    # Not support parameter contain "!"
		if '!' in str(object.getAttribute('Code')):
			return 0
		# not support service type now
		elif 'Service' in str(object.getAttribute('Type')):
			return 0
	return 1

#parse xtc to dict_data
def parse_element(element):
	totalnum_action = 0
	dict_data = dict()
	for child in element.getElementsByTagName('action'):
		dict_data[totalnum_action] = dict()
		method = child.getAttribute('Method')
		title = child.getAttribute('Title')
		dict_data[totalnum_action][0] = method
		dict_data[totalnum_action][1] = title

		if(child.getElementsByTagName('OBJECT') and child.getElementsByTagName('OBJECT')[0].hasAttribute('Code')):
			code = child.getElementsByTagName('OBJECT')[0].getAttribute('Code')
			dict_data[totalnum_action][2] = code
		if (child.getElementsByTagName('OBJECT') and child.getElementsByTagName('OBJECT')[0].hasAttribute('Type')):
			type = child.getElementsByTagName('OBJECT')[0].getAttribute('Type')
			dict_data[totalnum_action][3] = type

		# Get main object under action
		if (len(child.getElementsByTagName("OBJECT")) >= 1):
			mainObject = child.getElementsByTagName('OBJECT')[0]
			if(len(mainObject.getElementsByTagName("sub")) >= 1):
				subOject = mainObject.getElementsByTagName("sub")[0]

		if method == 'add' or method == 'Add' or method == 'update' or method == 'Update':
			for att in mainObject.getElementsByTagName('put')[0].attributes.items():
				if att[0] == "CardType":
					if att[1] == "0":
						cardType = "cCustomer"
					elif att[1] == "1":
						cardType = "cSupplier"
					elif att[1] == "2":
						cardType = "cLid"
					else:
						cardType = att[1]
					dict_data[totalnum_action][att[0]] = cardType
				elif att[1] != "":
					dict_data[totalnum_action][att[0]] = att[1]
			if (len(mainObject.getElementsByTagName("sub")) >= 1):
				for object in subOject.getElementsByTagName("OBJECT"):
					objectName = object.getAttribute('Type')
					if(objectName[-1] == "s"):
						objectName = objectName[:-1]
					dict_data[totalnum_action][objectName] = {}
					for att in object.getElementsByTagName('put')[0].attributes.items():
						if att[0] == "CardType":
							if att[1] == "0":
								cardType = "cCustomer"
							elif att[1] == "1":
								cardType = "cSupplier"
							elif att[1] == "2":
								cardType = "cLid"
							else:
								cardType = att[1]
							dict_data[totalnum_action][objectName][att[0]] = cardType
						elif att[1] != "":
							dict_data[totalnum_action][objectName][att[0]] = att[1]
					if(dict_data[totalnum_action][objectName] == {}):
						del dict_data[totalnum_action][objectName]
		elif method == 'compare' or method == 'Compare':
			for child in child.getElementsByTagName('get'):
				for item in child.attributes.items():
					if item[1] != "":
						dict_data[totalnum_action][item[0]] = item[1]
		totalnum_action = totalnum_action + 1
	return dict_data

type_list = {
	1:"ChartOfAccounts",
	2:"BusinessPartners",
	4:"Items",
	5:"VatGroups",
	6:"PriceLists",
	7:"SpecialPrices",
	12:"Users",
	13:"Invoices",
	14:"CreditNotes",
	15:"DeliveryNotes",
	16:"Returns",
	17:"Orders",
	18:"PurchaseInvoices",
	19:"PurchaseCreditNotes",
	20:"PurchaseDeliveryNotes",
	21:"PurchaseReturns",
	23:"Quotations",
	22:"PurchaseOrders",
	24:"IncomingPayments",
	28:"JournalVouchersService",
	30:"JournalEntries",
	31:"StockTaking",
	33:"Contacts",
	40:"PaymentTermsTypes",
	42:"BankPages",
	43:"Manufacturers",
	46:"VendorPayments",
	49:"ShippingTypes",
	52:"ItemGroups",
	53:"SalesPersons",
	56:"CustomsGroups",
	57:"ChecksforPayment",
	59:"InventoryGenEntries",
	60:"InventoryGenExits",
	64:"Warehouses",
	65:"CommissionGroups",
	66:"ProductTrees",
	67:"StockTransfers",
	73:"AlternateCatNum",
	77:"Budgets",
	78:"BudgetDistributions",
	81:"Messages",
	91:"BudgetScenarios",
	97:"SalesOpportunities",
	103:"ActivityTypes",
	104:"ActivityLocations",
	112:"Drafts",
	125:"AdditionalExpenses",
	134:"QueryCategories",
	138:"FactoringIndicators",
	146:"InventoryCycles",
	150:"BPPriorities",
	151:"DunningLetters",
	152:"UserFieldsMD",
	153:"UserTablesMD",
	170:"ContractTemplates",
	171:"EmployeesInfo",
	176:"CustomerEquipmentCards",
	189:"KnowledgeBaseSolutions",
	190:"ServiceContracts",
	191:"ServiceCalls",
	194:"Queue",
	198:"SalesForecast",
	200:"Territories",
	201:"Industries",
	205:"PackagesTypes",
	211:"Teams",
	212:"Relationships",
	217:"ActivityStatuses",
	140:"UnKnown",
}
# add json to jmx, generate jmeter file
def add_jmx_template(dom, dict_data,file_name):
	# print dict_data
	for i in dict_data:
		# use title as name
		name = file_name + " - " + dict_data[i][1]
		method = dict_data[i][0]
		type = ""

		if(dict_data[i].has_key(2)):
			entryCode = dict_data[i][2]
			del dict_data[i][2]
		if (dict_data[i].has_key(3)):
			actionType = dict_data[i][3]
			del dict_data[i][3]
			# print actionType
			if (actionType.isdigit()):
				type = type_list[int(actionType)]
			else:
				type = actionType

		if (method == 'update' or method == 'Update' or method == 'remove' or method == 'Remove'):
			if(entryCode.isdigit()):
				type = type + "(" + entryCode + ")"
			else:
				type = type + "(\'" + entryCode + "\')"

		del dict_data[i][0]
		del dict_data[i][1]

		enter_node = dom.createTextNode('\n')
		Proxy_node = dom.createElement('HTTPSamplerProxy')
		Proxy_node.setAttribute("guiclass", "HttpTestSampleGui")
		Proxy_node.setAttribute("testclass", "HTTPSamplerProxy")
		Proxy_node.setAttribute("testname", name)
		Proxy_node.setAttribute("enabled", "true")
		boolProp_node = dom.createElement('boolProp')
		boolProp_node.setAttribute("name", "HTTPSampler.postBodyRaw")
		text = dom.createTextNode('true')
		boolProp_node.appendChild(text)
		Proxy_node.appendChild(enter_node)
		Proxy_node.appendChild(boolProp_node)
		Proxy_node.appendChild(enter_node)

		elementProp_node = dom.createElement('elementProp')
		elementProp_node.setAttribute("elementType", "Arguments")
		elementProp_node.setAttribute("name", "HTTPsampler.Arguments")

		collectionProp_node = dom.createElement('collectionProp')
		collectionProp_node.setAttribute("name", "Arguments.arguments")

		elementProp_node2 = dom.createElement('elementProp')
		elementProp_node2.setAttribute("elementType", "HTTPArgument")
		elementProp_node2.setAttribute("name", "")

		boolProp_node2 = dom.createElement('boolProp')
		boolProp_node2.setAttribute("name", "HTTPArgument.always_encode")
		text = dom.createTextNode('false')
		boolProp_node2.appendChild(text)
		elementProp_node2.appendChild(boolProp_node2)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "Argument.value")
		json_node = dom.createElement('')
		text = dom.createTextNode(json.dumps(dict_data[i], sort_keys=True, indent=4))
		stringProp_node.appendChild(text)
		elementProp_node2.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "Argument.metadata")
		json_node = dom.createElement('')
		text = dom.createTextNode('=')
		stringProp_node.appendChild(text)
		elementProp_node2.appendChild(stringProp_node)

		collectionProp_node.appendChild(elementProp_node2)

		elementProp_node.appendChild(collectionProp_node)

		Proxy_node.appendChild(elementProp_node)
		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.domain")
		Proxy_node.appendChild(stringProp_node)
		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.port")
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.connect_timeout")
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.response_timeout")
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.protocol")
		text = dom.createTextNode('https')
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.contentEncoding")
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.path")
		text = dom.createTextNode('/b1s/v1/' + type)
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.method")
		if(method == 'add' or method == 'Add'):
			text = dom.createTextNode('POST')
		elif(method == 'update' or method == 'Update'):
			text = dom.createTextNode('PATCH')
		elif(method == 'remove' or method == 'Remove'):
			text = dom.createTextNode('DELETE')
		else:
			text = dom.createTextNode(method)
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.follow_redirects")
		text = dom.createTextNode('true')
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.auto_redirects")
		text = dom.createTextNode('false')
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.use_keepalive")
		text = dom.createTextNode('true')
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.DO_MULTIPART_POST")
		text = dom.createTextNode('false')
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.monitor")
		text = dom.createTextNode('false')
		stringProp_node.appendChild(text)
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "HTTPSampler.embedded_url_re")
		Proxy_node.appendChild(stringProp_node)

		stringProp_node = dom.createElement('stringProp')
		stringProp_node.setAttribute("name", "TestPlan.comments")
		Proxy_node.appendChild(stringProp_node)

		item = dom.getElementsByTagName('ThreadGroup')[0]
		item.nextSibling.nextSibling.appendChild(Proxy_node)

		hasTree_node = dom.createElement('hashTree')
		item.nextSibling.nextSibling.appendChild(hasTree_node)
		item.nextSibling.nextSibling.appendChild(enter_node)
	# print item.nextSibling.nextSibling
	return dom

# add all xtc to one jmx
def addXtcToOneJmx(xtcFile,jmxTemplate,file_name):
	dom = minidom.parse(xtcFile)
	# if pre_check(dom) == 0:
	# 	# print xtcFile
	# 	return
	dict_data = parse_element(dom)
	with open(jmxTemplate, 'r+') as jmxfile:
		jmx_dom = minidom.parse(jmxfile)
		jmxfile.seek(0)
		add_jmx_template(jmx_dom, dict_data,file_name).writexml(jmxfile)
		jmxfile.truncate()
	# print jmxfile
	return jmxfile

# Add one xtc to one jmx
def addXtcToJmx(xtcFile,jmxTemplate,file_name):
	dom = minidom.parse(xtcFile)
	dict_data = parse_element(dom)
	# print dict_data
	jmxFileName = xtcFile.replace('.xtc', '.jmx')
	jmxFile = open(jmxFileName, 'w')
	jmx_dom = minidom.parse(jmxTemplate)
	add_jmx_template(jmx_dom, dict_data, file_name).writexml(jmxFile)
	jmxFile.close()
	return jmxFile

def batchConvertXTCtoJMX(xtcFolder,jmxTemplate):
	for root, dirs, files in os.walk(xtcFolder):
		for name in files:
			if name.endswith(".xtc"):
				xtcFile = os.path.join(root, name)
				file_name = name.split(".")[0]
				addXtcToJmx(xtcFile,jmxTemplate,file_name)
				# addXtcToJmx(xtcFile, jmxTemplate, file_name)

if __name__ == '__main__':
	xtcFolder = r'D:\MyBox\Work\SAP\QA\TestCase\ServiceLayerTools\test\XTC\test'
	jmxTemplate = r"D:\MyBox\Work\SAP\QA\TestCase\ServiceLayerTools\SLTemplate.jmx"
	batchConvertXTCtoJMX(xtcFolder,jmxTemplate)
