import pandas as pd
import numpy as np
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField

# Cargar tablas termodinámicas desde CSV
tabla_temp = pd.read_csv('saturacion_temperatura.csv')
tabla_pres = pd.read_csv('saturacion_presion.csv')
tabla_temp_r134a = pd.read_csv('saturacion_temperatura_r134a.csv')
tabla_pres_r134a = pd.read_csv('saturacion_presion_r134a.csv')
tabla_aire = pd.read_csv('gas_ideal_aire.csv')

class CustomizeScreen(MDBoxLayout):
    pass

class Screen1(Screen):
    tipo_propiedad = None
    unidad_presion = None

    def set_tipo_propiedad(self, tipo):
        self.tipo_propiedad = tipo
        self.ids.boton_temperatura.md_bg_color = (0.3, 0.3, 0.3, 1)
        self.ids.boton_presion.md_bg_color = (0.3, 0.3, 0.3, 1)
        self.ids[f'boton_{tipo}'].md_bg_color = (0.1, 0.6, 0.6, 1)

        if tipo == 'presion':
            self.ids.layout_unidad_presion.opacity = 1
        else:
            self.ids.layout_unidad_presion.opacity = 0

    def set_unidad_presion(self, unidad):
        self.unidad_presion = unidad
        self.ids.boton_mpa.md_bg_color = (0.3, 0.3, 0.3, 1)
        self.ids.boton_kpa.md_bg_color = (0.3, 0.3, 0.3, 1)
        self.ids[f'boton_{unidad.lower()}'].md_bg_color = (0.1, 0.6, 0.6, 1)

    def interpolar(self, valor, tabla, columna_clave):
        if valor in tabla[columna_clave].values:
            return tabla[tabla[columna_clave] == valor].iloc[0]
        else:
            tabla_ordenada = tabla.sort_values(by=columna_clave)
            menores = tabla_ordenada[tabla_ordenada[columna_clave] <= valor].tail(1)
            mayores = tabla_ordenada[tabla_ordenada[columna_clave] > valor].head(1)

            if menores.empty or mayores.empty:
                return None

            interpolado = {}
            for columna in tabla.columns:
                if columna != columna_clave:
                    x0, x1 = menores[columna_clave].values[0], mayores[columna_clave].values[0]
                    y0, y1 = menores[columna].values[0], mayores[columna].values[0]
                    interpolado[columna] = np.interp(valor, [x0, x1], [y0, y1])
            interpolado[columna_clave] = valor
            return interpolado

    def consultar_tabla(self, valor, tipo, unidad):
        if tipo == 'temperatura':
            return self.interpolar(valor, tabla_temp, 'T (°C)')
        elif tipo == 'presion':
            if unidad == 'kPa':
                valor /= 1000  # Convertir kPa a MPa
            return self.interpolar(valor, tabla_pres, 'P (MPa)')
        else:
            raise ValueError("Tipo no válido. Usa 'temperatura' o 'presion'.")

    def calcular_propiedades(self):
        valor_str = self.ids.input_valor.text.replace(',', '.')
        
        # Verificar si el campo está vacío
        if not valor_str:
            self.ids.resultado.text = "No ingresó ningún valor."
            return
        
        try:
            valor = float(valor_str)
        except ValueError:
            self.ids.resultado.text = "Valor no válido. Ingrese un número."
            return
        
        tipo = self.tipo_propiedad
        unidad = self.unidad_presion if tipo == 'presion' else None
        resultado = self.consultar_tabla(valor, tipo, unidad)

        self.ids.resultado.text = ""
        if resultado is not None:
            for columna, valor in resultado.items():
                self.ids.resultado.text += f"{columna}: {valor}\n"  # Mostrar todos los decimales
        else:
            self.ids.resultado.text = f"El valor {valor_str} está fuera del rango."

class Screen2(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tipo_propiedad = None
        self.unidad_presion = None

    def set_tipo_propiedad(self, tipo):
        self.tipo_propiedad = tipo
        self.ids.boton_temperatura.md_bg_color = (0.3, 0.3, 0.3, 1)  # Resetear color
        self.ids.boton_presion.md_bg_color = (0.3, 0.3, 0.3, 1)  # Resetear color

        if tipo == 'temperatura':
            self.ids.boton_temperatura.md_bg_color = (0.1, 0.7, 0.1, 1)  # Color para Temperatura
            self.ids.layout_unidad_presion.opacity = 0  # Ocultar unidades de presión
        else:
            self.ids.boton_presion.md_bg_color = (0.1, 0.7, 0.1, 1)  # Color para Presión
            self.ids.layout_unidad_presion.opacity = 1  # Mostrar unidades de presión

    def set_unidad_presion(self, unidad):
        self.unidad_presion = unidad
        self.ids.boton_kpa.md_bg_color = (0.3, 0.3, 0.3, 1)  # Resetear color

        if unidad == 'kPa':
            self.ids.boton_kpa.md_bg_color = (0.1, 0.7, 0.1, 1)  # Color para kPa

    def interpolar(self, valor, tabla, columna_clave):
        if valor in tabla[columna_clave].values:
            return tabla[tabla[columna_clave] == valor].iloc[0]
        else:
            tabla_ordenada = tabla.sort_values(by=columna_clave)
            menores = tabla_ordenada[tabla_ordenada[columna_clave] <= valor].tail(1)
            mayores = tabla_ordenada[tabla_ordenada[columna_clave] > valor].head(1)

            if menores.empty or mayores.empty:
                return None

            interpolado = {}
            for columna in tabla.columns:
                if columna != columna_clave:
                    x0, x1 = menores[columna_clave].values[0], mayores[columna_clave].values[0]
                    y0, y1 = menores[columna].values[0], mayores[columna].values[0]
                    interpolado[columna] = np.interp(valor, [x0, x1], [y0, y1])
            interpolado[columna_clave] = valor
            return interpolado

    def consultar_tabla(self, valor, tipo, unidad):
        if tipo == 'temperatura':
            return self.interpolar(valor, tabla_temp_r134a, 'Temperatura (°C)')
        elif tipo == 'presion':
            if unidad == 'kPa':
                valor /= 1000
            return self.interpolar(valor, tabla_pres_r134a, 'Presion (kPa)')
        else:
            raise ValueError("Tipo no válido. Usa 'temperatura' o 'presion'.")

    def calcular_propiedades(self):
        valor_str = self.ids.input_valor.text.replace(',', '.')
        if not valor_str:  # Verificar si el campo está vacío
            self.ids.resultado.text = "No ingresó ningún valor."
            return

        valor = float(valor_str)
        tipo = self.tipo_propiedad
        unidad = self.unidad_presion if tipo == 'presion' else None
        resultado = self.consultar_tabla(valor, tipo, unidad)

        self.ids.resultado.text = ""
        if resultado is not None:
            for columna, valor in resultado.items():
                self.ids.resultado.text += f"{columna}: {valor:.6f}\n"  # Mostrar todos los decimales
        else:
            self.ids.resultado.text = f"El valor {valor_str} está fuera del rango."


class Screen3(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def interpolar(self, valor):
        if valor in tabla_aire['T (K)'].values:
            return tabla_aire[tabla_aire['T (K)'] == valor].iloc[0]
        else:
            tabla_ordenada = tabla_aire.sort_values(by='T (K)')
            menores = tabla_ordenada[tabla_ordenada['T (K)'] <= valor].tail(1)
            mayores = tabla_ordenada[tabla_ordenada['T (K)'] > valor].head(1)

            if menores.empty or mayores.empty:
                return None

            interpolado = {}
            for columna in tabla_aire.columns:
                x0, x1 = menores['T (K)'].values[0], mayores['T (K)'].values[0]
                y0, y1 = menores[columna].values[0], mayores[columna].values[0]
                interpolado[columna] = np.interp(valor, [x0, x1], [y0, y1])
            return interpolado

    def calcular_propiedades(self):
        valor_str = self.ids.input_valor.text.replace(',', '.')
        if not valor_str:  # Verificar si el campo está vacío
            self.ids.resultado.text = "No ingresó ningún valor."
            return

        valor = float(valor_str)
        resultado = self.interpolar(valor)

        self.ids.resultado.text = ""
        if resultado is not None:
            for columna, valor in resultado.items():
                self.ids.resultado.text += f"{columna}: {valor:.6f}\n"  # Mostrar todos los decimales
        else:
            self.ids.resultado.text = f"El valor {valor_str} está fuera del rango."

class Ui(ScreenManager):
    pass

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'
        self.theme_cls.primary_palette = 'Teal'
        return Ui()

    def change_style(self, checked, value):
        if value:
            self.theme_cls.theme_style = 'Light'
        else:
            self.theme_cls.theme_style = 'Dark'

if __name__ == "__main__":
    MainApp().run()
