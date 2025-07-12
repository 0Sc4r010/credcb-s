import sys
from utilidades import truncar_con_regla_especial,extraer_fac_cont
from requests import Session
from config import wsdl_fac
from db.querys import  consultapagos, find_pettycash, updated_status, view_invoice_data_head
from soap_client import get_soap_client
import logging

# Clase para instanciar la clase 
client = get_soap_client(wsdl_fac)  # o wsdl_inv

logger = logging.getLogger(__name__)


'''metodo para getionar el valor a pagar'''
def create_vfopa(detalle,row):
    total_pagar = 0  # Inicializa la variable antes del bucle
    valor = 0
    TSFaDfopa = []  # Inicializa una lista vacía para almacenar los registros
    pagos = consultapagos(row['id'])
    if not pagos:
        cls_pago = 0 if row['fpd_codi'] in (101,311) else 105
        for vcadic in detalle:
            valor = vcadic['dfa_cant'] * ( vcadic['dfa_valo'] + vcadic['dfa_impt'])
            valor_truncado = truncar_con_regla_especial(valor,0,'T')   #   round(valor,3)
            total_pagar += valor_truncado   
            Cod_aprob = ''.join(c for c in str(row['apb_code']) if c.isdigit())    
            
        TSFaDfopa.append(
            {        
                    'Fop_codi' : row['fpd_codi'],
                    'Tac_codi' : cls_pago,
                    'Dfo_nume' : row['apb_code'],
                    'Dfo_valo' : total_pagar ,
                    'Dfo_fech' : detalle[0]['fac_fech'],
                    'Dfo_comp' : 'S',
                    'Caj_codi' : find_pettycash(detalle[0]['id_proyecto'], detalle[0]['operacion']),  
                    'Dfo_desc' : 'Recaudo automatico',
                    'Ban_codi' : 0,
                    'Dfo_chec' : Cod_aprob if Cod_aprob else 0
            })
    else:
        for pago_det in pagos:
            Cod_aprob = ''.join(c for c in str(pago_det.get('approval_code')) if c.isdigit()) 
            TSFaDfopa.append({
                'Fop_codi': pago_det.get('code'),
                'Tac_codi':  0 if pago_det.get('code') in (101,311) else 105,  # 105  pero es necesario denir uno 
                'Dfo_nume': pago_det.get('approval_code'),
                'Dfo_valo': pago_det.get('value'),
                'Dfo_fech': detalle[0].get('fac_fech'),
                'Dfo_comp': 'S',
                'Caj_codi': find_pettycash(detalle[0].get('id_proyecto'), detalle[0].get('operacion')),
                'Dfo_desc': 'Recaudo automático',
                'Ban_codi': 0,
                'Dfo_chec': Cod_aprob if Cod_aprob else 0
            
            })
 
    return {'TSFaDfopa': TSFaDfopa}  # Retorna la lista con todos los registros insertados      
  

def calcula_factura_no_tasa(detalle):
    try:
        total_brutofac = 0  # Inicializa la variable antes del bucle 
        for vbrfac in detalle:
            total_brutofac += vbrfac['dfa_cant'] * vbrfac['dfa_valo']
        return total_brutofac
        
    except Exception as e:
        logger.error(f"Error processing invoice: {e}", exc_info=True)   
    
    
    

def create_vDistribA(detalle):
    try:
        return {
            'TSFaDdisp': [
                {'Tar_codi': 1, 'Arb_codi': detalle[0]['area'], 'Ddi_tipo': 'P', 'Ddi_valo': 0, 'Ddi_porc': 100},
                {'Tar_codi': 4, 'Arb_codi': detalle[0]['proyecto'], 'Ddi_tipo': 'P', 'Ddi_valo': 0, 'Ddi_porc': 100},
                {'Tar_codi': 2, 'Arb_codi': detalle[0]['sucursal'], 'Ddi_tipo': 'P', 'Ddi_valo': 0, 'Ddi_porc': 100},
                {'Tar_codi': 3, 'Arb_codi': detalle[0]['ctro_Costo'], 'Ddi_tipo': 'P', 'Ddi_valo': 0, 'Ddi_porc': 100}
            ]
        }
    except Exception as e:
        logger.error(f"Error processing invoice: {e}", exc_info=True)   



def insertar_detalles(detalles, vDistribA):
    return {
        'TSFaDfact': [
            {
                'Bod_codi': detalle['bod_codi'],
                'Pro_codi': detalle['pro_codi'],
                'Uni_codi': detalle['uni_codi'],
                'Dfa_cant': detalle['dfa_cant'],
                'Dfa_valo': detalle['dfa_valo'],
                'Dfa_tide': detalle['dfa_tide'],
                'Dfa_pvde': round(detalle['dfa_pvde'], 2),
                'Dfa_desc': detalle['dfa_desc'],
                'Dfa_dest': detalle['destino'],
                'Ctr_cont': 0,
                'Tip_codi': 0,
                'Cli_coda': detalle['cli_coda'],
                'Dcl_codd': 1,
                'Lot_fven': '2029-12-30',
                'vDistribA': vDistribA
            } for detalle in detalles
        ]
    }

def insertar_encabezado_fc(row,proceso_global):
        detalles_cursor = view_invoice_data_head('I',  row['id_origen'], row['doc_nume'], row['nom_disp'])
        if isinstance( detalles_cursor, list) and  detalles_cursor:
            vDistribA = create_vDistribA(detalles_cursor)
            vDetalle = insertar_detalles(detalles_cursor, vDistribA)
            vFopa = create_vfopa(detalles_cursor,row)
            # vCAdic =  create_vcadic(detalles_cursor) 
            factura = {
                'Emp_codi': row['id_proyecto'],
                'Top_codi': row['operacion'],
                'Fac_nume': 0,
                'Fac_fech': row['fac_fech'],
                'Fac_desc': row['des_hfac'] + '-' + str(row['fac_nume']),
                'Arb_csuc': row['sucursal'],
                'Tip_codi': 0,
                'Cli_coda': row['cli_coda'],
                'Dcl_codd': row['Dcl_codd'],
                'Mon_codi': row['Mon_codi'],
                'Fac_tdis': 'A',
                'Fac_tipo': row['fac_tipo'],
                'Fac_feta': row['fac_fech'],
                'Fac_feci': row['fac_fech'],
                'Fac_fecf': row['fac_fech'],
                'Fac_cref': row['fac_cref'],
                'Fac_fepo': row['fac_fech'],
                'Fac_fepe': row['fac_fech'],
                'Fac_fext': row['fac_fech'],
                'Mco_cont': 0,
                'Fac_tido': row['fac_tipo'],
                'Fac_pepe': 0,
                'Fac_pext': 0,
                'Fac_peri': 0,
                'Fac_esth': 0,
                'Fac_esta': 'A',
                'Fac_fepf': row['fac_fech'],
                'vDetalle': vDetalle,
                'vFopa' : vFopa
            }

            try:
                resultado_insercion = client.service.InsertarFactura(pFactura=factura)
                retorno = extraer_fac_cont('.//RETORNO', resultado_insercion) 
                if retorno!= 0:
                    logger.error(f"Error al insertar factura: {resultado_insercion}", exc_info=True)
                updated_status(proceso_global, extraer_fac_cont('.//RETORNO', resultado_insercion), row['fac_nume'] if proceso_global == 'T' else row['doc_nume'], row['id_proyecto'])
                    
            except Exception as e:
                logger.error(f"Error crítico: la operación no pudo completarse. Comuníquese con soporte técnico.: {e}")
        else:
            logger.info(f"Error crítico: Factura No procesada: {row['doc_nume']}", exc_info=True)       



if __name__ == "__main__":
    result = view_invoice_data_head()
    if isinstance(result, list) and result:
        insertar_encabezado_fc(result, branch_id=0)


