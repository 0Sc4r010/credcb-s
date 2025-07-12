import pymssql
import logging
from config import DB_SERVER,DB_USER,DB_PASSWORD,DB_NAME
from conexion import execute_query
# Configuración del logging
logger = logging.getLogger(__name__)


def insertar_sales(factura,cliente,ventas):
    Eds = factura.get('branch_id', '')
    Fac = factura.get('bill_number', '')
    Pfr = factura.get('bill_prefix', '')
    Fec = factura.get('billing_date','')
    Cli = cliente.get('document','') 
    Clf = cliente.get("first_name",'') 
    Cll = cliente.get("last_name",'') 
    Cla = cliente.get("address",'') 
    Clp = cliente.get("phone",'') 
    Eml = cliente.get('email','') 
    Tot = factura.get('total', '')
    Id  = factura.get('id', '')
    
    for payment in ventas:
        _payment =  payment.get("payment", [])
        for payment_ in _payment:
            if payment_.get("desc",'') == 'Credito':
               insertar_tabla(
                    p_eds=Eds,
                    p_fac=Fac,
                    p_pfr=Pfr,
                    p_fec=Fec,
                    p_cli=Cli,
                    p_clf=Clf,
                    p_cll=Cll,
                    p_cla=Cla,
                    p_clp=Clp,
                    p_eml=Eml,
                    p_tot=Tot,
                    p_des=payment.get("name", ""),
                    p_apb=payment.get("code", ""),
                    p_id=Id) 


def insertar_tabla(p_eds, p_fac, p_pfr, p_fec, p_cli, p_clf, p_cll, p_cla, p_clp, p_eml, p_tot, p_des, p_apb, p_id):
    query = """
        EXEC sp_GetDataEDS
            @emp_codi = %s, @pre_fixd = %s, @fac_nume = %s, @fac_fech = %s, 
            @cli_coda = %s, @id_origen = %s, @pro_codi = %s, @dfa_desc = %s, 
            @cli_name = %s, @cli_lasn = %s, @cli_addr = %s, @cli_phon = %s, 
            @fac_feta = %s, @fac_tipo = %s, @fac_feci = %s, @fac_fecf = %s, 
            @fac_cref = %s, @dfa_cant = %s, @dfa_valo = %s, @dfa_pvde = %s, 
            @eml_clte = %s, @arb_codi = %s, @payment = %s, @fpd_codi = %s,
            @dfa_impt = %s, @apb_code = %s, @id = %s
    """

    params = (
        3,             # emp_codi
        None,          # pre_fixd
        p_fac,         # fac_nume
        p_fec,         # fac_fech
        p_cli,         # cli_coda
        p_eds,         # id_origen
        0,             # pro_codi (valor fijo)
        'prueba',      # dfa_desc (puede ajustarse)
        p_clf,         # cli_name
        p_cll,         # cli_lasn
        p_cla,         # cli_addr
        p_clp,         # cli_phon
        p_fac,         # fac_feta
        'F',           # fac_tipo
        p_fec,         # fac_feci
        p_fec,         # fac_fecf
        'prueba',      # fac_cref
        1,             # dfa_cant
        p_tot,         # dfa_valo
        0,             # dfa_pvde
        p_eml,         # eml_clte
        '10810001',    # arb_codi
        p_des,         # payment (nombre)
        p_apb,         # fpd_codi (código)
        0,             # dfa_impt
        0,             # apb_code
        p_id           # id
    )
    
    return execute_query(query, params, fetch=False)