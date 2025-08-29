import os

client_id = "1KFFYcePjAU8wjEfwNYSMJ5cp"
client_secret = "SbWjFqQ512c3tYHa3HTcVMGiUMKGeFAy0tbx87qt"
scope = "dominus"

DB_SERVER = os.getenv("DB_SERVER", "172.18.200.14\pruebas") # 172.18.200.14\pruebas172.18.200.14:1433
DB_USER = os.getenv("DB_USER", "seven")
DB_PASSWORD = os.getenv("DB_PASSWORD", "seven") # "Gav:[Z3A@X7"
DB_NAME = os.getenv("DB_NAME", "seven_qa") # seven_pruebas

ULTIMOS_DATOS =[]

wsdl_fac = 'http://172.18.200.26/Seven/Webservicesoap/UFaFactu/SFaFactu.asmx?wsdl'
wsdl_ews = 'http://172.18.200.26/SEVEN/WEBSERVICESOPHELIA/SIeWssec.asmx?wsdl'
wsdl_rec = 'http://172.18.200.26/SEVEN/WEBSERVICESOPHELIA/WTsRecaj.asmx?wsdl'
wsdl_acc = 'http://172.18.200.26/SEVEN/WEBSERVICESOPHELIA/SCnMcont.asmx?wsdl'
wsdl_inv = 'http://172.18.200.26/SEVEN/WEBSERVICESOPHELIA/SInMinve.asmx?wsdl'