import reflex as rx
from rxconfig import config

# Constantes para cálculos
PORCENTAJE_TSS = 0.0304  # 3.04% del sueldo bruto

# Definición de rangos para el ISR (anual)
RANGO_EXENTO_ANUAL = 416220  # Hasta RD$416,220 (exento)
RANGO_MEDIO1_ANUAL = 624329  # Hasta RD$624,329 (15% del excedente)
RANGO_MEDIO2_ANUAL = 867123  # Hasta RD$867,123 (20% del excedente + monto fijo)

# Montos IRS
MONTO_FIJO_RANGO_MEDIO2 = 31216  # RD$31,216
MONTO_FIJO_RANGO_ALTO = 79776  # RD$79,776

PORCENTAJE_BONIFICACION = 0.0833


def calcular_isr(sueldo_mensual):
    """Calcula el ISR mensual basado en el sueldo anual"""
    # Convertir el sueldo mensual a anual para calcular el ISR
    sueldo_anual = sueldo_mensual * 12
    
    # Determinar el ISR según el rango de ingresos
    if sueldo_anual <= RANGO_EXENTO_ANUAL:
        # Exento de ISR
        isr_anual = 0
    elif sueldo_anual <= RANGO_MEDIO1_ANUAL:
        # 15% del excedente sobre RD$416,220
        excedente = sueldo_anual - RANGO_EXENTO_ANUAL
        isr_anual = excedente * 0.15
    elif sueldo_anual <= RANGO_MEDIO2_ANUAL:
        # RD$31,216 + 20% del excedente sobre RD$624,329
        excedente = sueldo_anual - RANGO_MEDIO1_ANUAL
        isr_anual = MONTO_FIJO_RANGO_MEDIO2 + (excedente * 0.20)
    else:
        # RD$79,776 + 25% del excedente sobre RD$867,123
        excedente = sueldo_anual - RANGO_MEDIO2_ANUAL
        isr_anual = MONTO_FIJO_RANGO_ALTO + (excedente * 0.25)
    
    # Dividir el ISR anual entre 12 para obtener la retención mensual
    isr_mensual = isr_anual / 12
    return isr_mensual


class State(rx.State):
    """Estado de la aplicación"""
    
    # Inputs
    sueldo_bruto: str = ""
    otros_descuentos: str = ""
    
    # Resultados calculados
    descuento_tss: float = 0.0
    retencion_isr: float = 0.0
    bonificacion: float = 0.0
    sueldo_neto: float = 0.0
    total_descuentos: float = 0.0
    sueldo_bruto_num: float = 0.0
    otros_descuentos_num: float = 0.0
    
    # Estado de validación y resultados
    mostrar_resultados: bool = False
    error_message: str = ""
    
    def calcular_sueldo(self):
        """Realiza todos los cálculos del sueldo neto"""
        try:
            # Validar entradas
            if not self.sueldo_bruto or not self.sueldo_bruto.strip():
                self.error_message = "Por favor ingrese el sueldo bruto"
                self.mostrar_resultados = False
                return
            
            self.sueldo_bruto_num = float(self.sueldo_bruto)
            if self.sueldo_bruto_num <= 0:
                self.error_message = "El sueldo bruto debe ser un valor positivo"
                self.mostrar_resultados = False
                return
            
            self.otros_descuentos_num = 0.0
            if self.otros_descuentos and self.otros_descuentos.strip():
                self.otros_descuentos_num = float(self.otros_descuentos)
                if self.otros_descuentos_num < 0:
                    self.error_message = "Los descuentos no pueden ser negativos"
                    self.mostrar_resultados = False
                    return
            
            # Realizar cálculos
            self.descuento_tss = self.sueldo_bruto_num * PORCENTAJE_TSS
            self.retencion_isr = calcular_isr(self.sueldo_bruto_num)
            self.bonificacion = self.sueldo_bruto_num * PORCENTAJE_BONIFICACION
            self.total_descuentos = self.descuento_tss + self.retencion_isr + self.otros_descuentos_num
            self.sueldo_neto = self.sueldo_bruto_num - self.total_descuentos + self.bonificacion
            
            # Limpiar errores y mostrar resultados
            self.error_message = ""
            self.mostrar_resultados = True
            
        except ValueError:
            self.error_message = "Por favor ingrese valores numéricos válidos"
            self.mostrar_resultados = False
    
    def limpiar_formulario(self):
        """Limpia todos los campos y resultados"""
        self.sueldo_bruto = ""
        self.otros_descuentos = ""
        self.mostrar_resultados = False
        self.error_message = ""
        self.descuento_tss = 0.0
        self.retencion_isr = 0.0
        self.bonificacion = 0.0
        self.sueldo_neto = 0.0
        self.total_descuentos = 0.0
        self.sueldo_bruto_num = 0.0
        self.otros_descuentos_num = 0.0


def formato_dinero(cantidad: float) -> str:
    """Formatea una cantidad como dinero dominicano"""
    return f"RD$ {cantidad:,.2f}"


def input_section() -> rx.Component:
    """Sección de inputs del formulario"""
    return rx.vstack(
        rx.heading("Calculadora de Sueldo Neto", size="8", color="blue.600"),
        rx.text("República Dominicana", size="4", color="gray.600"),
        
        rx.vstack(
            rx.text("Sueldo Bruto Mensual", weight="bold", size="3"),
            rx.input(
                placeholder="Ej: 50000",
                value=State.sueldo_bruto,
                on_change=State.set_sueldo_bruto,
                type="number",
                min="0",
                step="0.01",
                width="100%",
                size="3"
            ),
            width="100%",
            spacing="2"
        ),
        
        rx.vstack(
            rx.text("Otros Descuentos (Opcional)", weight="bold", size="3"),
            rx.input(
                placeholder="Ej: 5000 (dejar vacío si no hay)",
                value=State.otros_descuentos,
                on_change=State.set_otros_descuentos,
                type="number",
                min="0",
                step="0.01",
                width="100%",
                size="3"
            ),
            width="100%",
            spacing="2"
        ),
        
        rx.hstack(
            rx.button(
                "Calcular Sueldo Neto",
                on_click=State.calcular_sueldo,
                size="3",
                color_scheme="blue",
                variant="solid"
            ),
            rx.button(
                "Limpiar",
                on_click=State.limpiar_formulario,
                size="3",
                color_scheme="gray",
                variant="outline"
            ),
            spacing="3",
            justify="center"
        ),
        
        rx.cond(
            State.error_message,
            rx.callout(
                State.error_message,
                icon="triangle_alert",
                color_scheme="red",
                size="2"
            )
        ),
        
        spacing="5",
        width="100%",
        align="center"
    )


def results_section() -> rx.Component:
    """Sección que muestra los resultados del cálculo"""
    return rx.cond(
        State.mostrar_resultados,
        rx.vstack(
            rx.heading("Resultados del Cálculo", size="6", color="green.600"),
            
            # Tabla de resultados principales
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Concepto"),
                        rx.table.column_header_cell("Monto", justify="end"),
                    )
                ),
                rx.table.body(
                    rx.table.row(
                        rx.table.row_header_cell("Sueldo Bruto"),
                        rx.table.cell(
                            rx.text(f"RD$ {State.sueldo_bruto_num:,.2f}", 
                                   weight="medium"),
                            justify="end"
                        ),
                    ),
                    rx.table.row(
                        rx.table.row_header_cell("(-) TSS (3.04%)"),
                        rx.table.cell(
                            rx.text(f"RD$ {State.descuento_tss:,.2f}", color="red.600"),
                            justify="end"
                        ),
                    ),
                    rx.table.row(
                        rx.table.row_header_cell("(-) Retención ISR"),
                        rx.table.cell(
                            rx.text(f"RD$ {State.retencion_isr:,.2f}", color="red.600"),
                            justify="end"
                        ),
                    ),
                    rx.table.row(
                        rx.table.row_header_cell("(-) Otros Descuentos"),
                        rx.table.cell(
                            rx.text(f"RD$ {State.otros_descuentos_num:,.2f}", color="red.600"),
                            justify="end"
                        ),
                    ),
                    rx.table.row(
                        rx.table.row_header_cell("(+) Bonificación (8.33%)"),
                        rx.table.cell(
                            rx.text(f"RD$ {State.bonificacion:,.2f}", color="green.600"),
                            justify="end"
                        ),
                    ),
                ),
                variant="surface",
                size="2",
                width="100%"
            ),
            
            # Resultado final destacado
            rx.card(
                rx.vstack(
                    rx.heading("SUELDO NETO", size="5", color="green.700"),
                    rx.text(
                        f"RD$ {State.sueldo_neto:,.2f}",
                        size="7",
                        weight="bold",
                        color="green.700"
                    ),
                    spacing="2",
                    align="center"
                ),
                size="3",
                width="100%",
                background="green.50"
            ),
            
            # Resumen adicional
            rx.hstack(
                rx.card(
                    rx.vstack(
                        rx.text("Total Descuentos", size="2", weight="medium", color="red.600"),
                        rx.text(f"RD$ {State.total_descuentos:,.2f}", size="4", weight="bold", color="red.600"),
                        spacing="1",
                        align="center"
                    ),
                    size="2",
                    flex="1"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Total Bonificaciones", size="2", weight="medium", color="green.600"),
                        rx.text(f"RD$ {State.bonificacion:,.2f}", size="4", weight="bold", color="green.600"),
                        spacing="1",
                        align="center"
                    ),
                    size="2",
                    flex="1"
                ),
                spacing="3",
                width="100%"
            ),
            
            spacing="4",
            width="100%"
        )
    )


def index() -> rx.Component:
    """Página principal de la aplicación"""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            input_section(),
            results_section(),
            spacing="8",
            align="center",
            min_height="90vh",
            padding_y="5"
        ),
        max_width="800px",
        padding="4"
    )


app = rx.App(
    style={
        "font_family": "Inter",
        "background_color": "gray.50"
    }
)
app.add_page(index, title="Calculadora de Sueldo Neto RD")