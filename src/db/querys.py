import pymssql
import logging
from config import DB_SERVER,DB_USER,DB_PASSWORD,DB_NAME
from db.connection import execute_query
# Configuración del logging
logger = logging.getLogger(__name__)


def insertar_sales(factura,cliente,ventas):
    cli_doc = cliente.get('document', '')
    if cliente.get('id_type', '') == '31':
        Cli = cli_doc[:9]  # Remueve el último carácter si aplica
    else:    
        Cli =  cli_doc
    Eds = factura.get('branch_id', '')
    Fac = factura.get('bill_number', '')
    Pfr = factura.get('bill_prefix', '')
    Fec = factura.get('billing_date','')
    Clf = cliente.get("first_name",'') 
    Cll = cliente.get("last_name",'') 
    Cla = cliente.get("address",'') 
    Clp = cliente.get("phone",'') 
    Eml = cliente.get('email','') 
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
                    p_tot=payment_.get("value", ""),
                    p_des=payment_.get("name", ""),
                    p_apb=payment_.get("code", ""),
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
        2156,          # id_origen
        '211010006',   # pro_codi (valor fijo)
        'Crdto CB&S',      # dfa_desc (puede ajustarse)
        p_clf,         # cli_name
        p_cll,         # cli_lasn
        p_cla,         # cli_addr
        p_clp,         # cli_phon
        p_fec,         # fac_feta
        'F',           # fac_tipo
        p_fec,         # fac_feci
        p_fec,         # fac_fecf
        p_eds,         # fac_cref
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


def view_invoice_data_head(tipo,branch_id = 0,numero=0,surtidor=''):
    query = "exec usp_ViewInvoiceData @Proceso=%s, @BranchID=%s, @FacNume=%s, @distrib=%s"
    params = (tipo, branch_id, numero,surtidor)
    return execute_query(query,params)    


def  consultapagos(pid):
    query = 'select * from int_PagosEds  where sale_id = %s'
    params = (pid)
    result = execute_query(query,params)
    if not result:
        return None
    else: 
        return result     
    
def find_pettycash(empresa,operacion):
    query = 'select caj_codi from int_pareds where id_proyecto = %s and operacion = %s'
    params = (empresa,operacion)
    result = execute_query(query,params)
    if not result:
        return None
    else: 
        return result[0]['caj_codi']     # type: ignore
    
    

def  updated_status(proceso,estado,factura, empresa):
   sentenc = """update int_dataeds set Est_proc = %s where fac_nume = %s and emp_codi = %s"""
   params = (estado,factura, empresa)
   if proceso == 'T':        
        return execute_query(sentenc.replace("int_dataeds", "int_datatickets"),params,fetch=False)
   else:
        return execute_query(sentenc,params,fetch=False)       
    
def clean_data(proceso):
        sentenc = """DELETE FROM int_dataeds where est_proc = %s"""
        params = (proceso,)
        # Ejecutar la consulta
        result = execute_query(sentenc, params, fetch=False)
        return result      