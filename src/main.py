import tkinter as tk
from tkinter import ttk, scrolledtext
from tkcalendar import DateEntry
from domain.facturas import insertar_encabezado_fc
from utils.cnxapi import facturas_eds
from db.querys import insertar_sales, view_invoice_data_head,clean_data
import logging


class TextHandler(logging.Handler):
    """Manejador de logs que escribe en un widget Text de Tkinter."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.yview(tk.END)  # autoscroll al final


def configurar_logger(text_area):
    """Configura el logger global con el TextHandler personalizado."""
    text_handler = TextHandler(text_area)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    text_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(text_handler)
    return logger


def limpiar_text_area():
    text_area.configure(state='normal')
    text_area.delete('1.0', tk.END)
    text_area.configure(state='disabled')


def procesa_fac(logger):
    invoice_data = view_invoice_data_head("C")
    if not invoice_data:
        logger.warning("No hay facturas para procesar.")
        return
    for row in invoice_data:
        insertar_encabezado_fc(row, 'E')


def impdata_api(Fec_ini, Fec_fin, logger):
    clean_data(0)
    branch_ids = [2156, 2157]

    for branch_id in branch_ids:
        try:
            response_json_eds = facturas_eds(Fec_ini, Fec_fin, branch_id)
            if not response_json_eds or "data" not in response_json_eds:
                logger.warning(f"No se pudo obtener datos de ventas para la estación {branch_id}.")
                continue

            _data = response_json_eds.get("data", {}).get("fe_sales", [])
            if not _data:
                logger.warning(f"No hay datos de ventas para la estación {branch_id}.")
                continue

            for fe_sales in _data:
                customer = fe_sales.get("customer", [])
                sales = fe_sales.get("sales", [])
                insertar_sales(fe_sales, customer, sales)

            logger.info(f"Procesamiento de ventas completado para la estación {branch_id}.")

        except KeyError as e:
            logger.error(f"Error al acceder a los datos de ventas: Clave faltante {e}.", exc_info=True)
        except Exception as e:
            logger.error(f"Error inesperado al procesar ventas en la estación {branch_id}: {e}.", exc_info=True)

def reprocesos(logger):
    clean_data(0)
    procesa_fac(logger) 

def ventana_fechas(logger):
    def on_submit():
        fecha_inicio = date_entry_inicio.get()
        fecha_final = date_entry_final.get()
        top.destroy()
        limpiar_text_area()
        impdata_api(fecha_inicio, fecha_final, logger)
        procesa_fac(logger)

    top = tk.Toplevel()
    top.title("Seleccionar Fechas")
    
    ancho_ventana = 300
    alto_ventana = 180
    ancho_pantalla = top.winfo_screenwidth()
    alto_pantalla = top.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)
    top.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")
    
    ttk.Label(top, text="Fecha de inicio:").pack(pady=(10, 0))
    date_entry_inicio = DateEntry(top, date_pattern='yyyy-mm-dd')
    date_entry_inicio.pack()

    ttk.Label(top, text="Fecha final:").pack(pady=(10, 0))
    date_entry_final = DateEntry(top, date_pattern='yyyy-mm-dd')
    date_entry_final.pack()

    ttk.Button(top, text="Generar Factura", command=on_submit).pack(pady=15)


def crear_ventana_principal():
    global text_area
    ventana = tk.Tk()
    ventana.title('Cuentas por pagar a crédito EDS CB&S')

    ancho_ventana = 600
    alto_ventana = 400
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()
    x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    y = (alto_pantalla // 2) - (alto_ventana // 2)
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{x}+{y}")

    text_area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, state='disabled')
    text_area.pack(expand=True, fill='both', padx=10, pady=10)

    return ventana, text_area


def main():
    ventana, text_area = crear_ventana_principal()
    logger = configurar_logger(text_area)

    # Crear menú
    barra_menu = tk.Menu(ventana)
    menu_procesos = tk.Menu(barra_menu, tearoff=0)
    menu_procesos.add_command(label='Procesar Facturas', command=lambda: ventana_fechas(logger))
    menu_procesos.add_command(label='Reprocesar Novedades', command=lambda: reprocesos(logger))
    menu_procesos.add_command(label='Excluir Documentos ', command=lambda: reprocesos(logger))
    barra_menu.add_cascade(label="Procesar Facturas", menu=menu_procesos)
   
    ventana.config(menu=barra_menu)

    logger.info("Aplicación iniciada correctamente.")
    ventana.mainloop()


if __name__ == "__main__":
    main()

    
        
