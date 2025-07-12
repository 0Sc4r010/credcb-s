from zeep import Client
from zeep.transports import Transport
from requests import Session

def get_soap_client(wsdl_url: str) -> Client:
    session = Session()
    session.verify = False  
    transport = Transport(session=session)
    return Client(wsdl=wsdl_url, transport=transport)
