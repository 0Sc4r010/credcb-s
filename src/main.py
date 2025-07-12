import tkinter as tk
import tkinter as ttk
from tkinter import simpledialog
from tkcalendar import DateEntry
from utils.cnxapi import facturas_eds
import logging

from db import insertar_sales
# import requests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("Credcbys.log")]
)
logger = logging.getLogger(__name__)

# funcion para actualizar clientes 
def genera_fac(Fec_ini, Fec_fin):
    branch_ids = [2156,2157] 
   
    for  branch_id in branch_ids:  
        try:
            response_json_eds = facturas_eds(Fec_ini,Fec_fin,branch_id)
            if not response_json_eds or "data" not in response_json_eds:
                logger.warning(f"No se pudo obtener datos de ventas para la Estacion {branch_id}.")
                continue
            
            _data = response_json_eds.get("data", {}).get("fe_sales", [])
            if not _data:
                logger.warning(f"No hay datos de ventas para la Estación {branch_id}.")
                continue
        
            for fe_sales in _data:
                customer  = fe_sales.get("customer", [])
                sales =  fe_sales.get("sales", [])
                insertar_sales(fe_sales,customer,sales)
                    
                print(fe_sales.get("bill_number"))   #insert_data_int(client, branch_id)
                
            logger.info(f"Procesamiento de ventas completado para la sucursal {branch_id}.")

        except KeyError as e:
            logger.error(f"Error al acceder a los datos de ventas: Clave faltante {e}.", exc_info=True)
        except Exception as e:
            logger.error(f"Error inesperado al procesar ventas en la sucursal {branch_id}: {e}.", exc_info=True)
      


def ventana_fechas():
    def on_submit():
        fecha_inicio = date_entry_inicio.get()
        fecha_final = date_entry_final.get()
        top.destroy()
        genera_fac(fecha_inicio, fecha_final)

    top = tk.Toplevel()
    top.title("Seleccionar Fechas")
    top.geometry("300x180")

    ttk.Label(top, text="Fecha de inicio:").pack(pady=(10, 0))
    date_entry_inicio = DateEntry(top, date_pattern='yyyy-mm-dd')
    date_entry_inicio.pack()

    ttk.Label(top, text="Fecha final:").pack(pady=(10, 0))
    date_entry_final = DateEntry(top, date_pattern='yyyy-mm-dd')
    date_entry_final.pack()

    ttk.Button(top, text="Generar Factura", command=on_submit).pack(pady=15)


# crear la ventana principal
ventana = tk.Tk()
ventana.title('Cuentas por pagar a credito EDS CB&S') 
ventana.geometry("400x300")
# crea la barra del menu
barra_menu = tk.Menu(ventana)
# menu de procesos 
menu_procesos = tk.Menu(barra_menu,tearoff=0)
menu_procesos.add_command(label='Generar Factura', command=ventana_fechas )
barra_menu.add_cascade(label="Procesos", menu=menu_procesos)
# Asigna el menu a la ventana 
ventana.config(menu=barra_menu)
ventana.mainloop()
