from django import forms
from .models import Ventas,MovimientoExterno
from users.models import Cliente, Usuario
from products.models import Products

import re
from datetime import datetime

getCustomerNumber = Cliente.objects.all()
getCustomerName = Cliente.objects.all()
getProducts = Products.objects.all()
getVendedores = Usuario.objects.all()
getSupervisores = Usuario.objects.all()
modalidades = Ventas.MODALIDADES
# agencias = Ventas.AGENCIAS
paquetes = Products.PAQUETES
tipoProductos = Products.TIPO_PRODUCTO

class FormCreateVenta(forms.Form):

    #  Campos que se desean mostrar en el formulario
    nro_contrato = forms.CharField(required=True, max_length=10)
    modalidad = forms.CharField(required=True, max_length=30)
    nro_cuotas = forms.IntegerField(required=True)
    anticipo = forms.IntegerField(required=True)
    primer_cuota = forms.IntegerField(required=True)
    importe = forms.FloatField(required=True)
    tasa_interes = forms.FloatField(required=True)
    intereses_generados = forms.FloatField(required=True)
    importe_x_cuota = forms.FloatField(required=True)
    total_a_pagar = forms.FloatField(required=True)
    fecha = forms.CharField(required=True, max_length=10)
    tipo_producto = forms.CharField(required=True)
    producto = forms.CharField(required=True)
    paquete = forms.CharField(required=True)
    nro_orden = forms.CharField(required=True)
    vendedor = forms.CharField(required=True)
    supervisor = forms.CharField(required=True)
    observaciones = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5,'class':'input-read-write-default'}))


    # Widgets de los campos
    nro_contrato.widget.attrs.update({'class': 'input-read-write-default','oninput': "this.value = this.value.replace(/[^0-9]/g, '');"})
    modalidad.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly', 'value':'Mensual'})
    nro_cuotas.widget.attrs.update({'class': 'input-read-write-default'})
    anticipo.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    primer_cuota.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    importe.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    tasa_interes.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    intereses_generados.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    importe_x_cuota.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    total_a_pagar.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    fecha.widget.attrs.update({'class': 'input-read-write-default'})
    tipo_producto.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    producto.widget.attrs.update({'class': 'input-read-write-default'})
    paquete.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly'})
    nro_orden.widget.attrs.update({'class': 'input-read-write-default','readonly':'readonly','oninput': "this.value = this.value.replace(/[^0-9]/g, '');"})
    vendedor.widget.attrs.update({'class': 'input-read-write-default'})
    supervisor.widget.attrs.update({'class': 'input-read-write-default'})

    
    


    def clean_producto(self):
        producto_input = self.cleaned_data['producto']
        producto_permitidos = [p.nombre.lower() for p in getProducts]

        if producto_input.lower() not in producto_permitidos:
            raise forms.ValidationError('Producto no válido')

        return producto_input
    

    def clean_modalidad(self):
        modalidad_input = self.cleaned_data['modalidad']
        modalidades_permitidas = [m[0].lower() for m in modalidades]

        if modalidad_input.lower() not in modalidades_permitidas:
            raise forms.ValidationError('Modalidad no válida')

        return modalidad_input
    

    def clean_tipo_producto(self):
        tipo_producto_input = self.cleaned_data['tipo_producto']
        tipo_producto_permitidas = [m[0].lower() for m in tipoProductos]

        if tipo_producto_input.lower() not in tipo_producto_permitidas:
            raise forms.ValidationError('Tipo de producto no válido')

        return tipo_producto_input
    

    def clean_paquete(self):
        paquete_input = self.cleaned_data['paquete']
        paquetes_permitidas = [m[0].lower() for m in paquetes]

        if paquete_input.lower() not in paquetes_permitidas:
            raise forms.ValidationError('Paquete no válido')

        return paquete_input

        
    def clean_nro_contrato(self):
        nro_contrato_input = self.cleaned_data['nro_contrato']

        # Verificar que el valor ingresado sea un número
        if not nro_contrato_input.isdigit():
            raise forms.ValidationError('El numero de solicitud debe ser un valor numérico.')
        
        return str(nro_contrato_input)
    
    
    def clean_nro_orden(self):
        nro_orden_input = self.cleaned_data['nro_orden']
        nro_contrato_input = self.cleaned_data['nro_contrato']

        # Verificar que el valor ingresado sea un número
        if not nro_orden_input.isdigit():
            raise forms.ValidationError('El numero de orden debe ser un valor numérico.')
        
        if not nro_contrato_input.endswith(nro_orden_input):
            raise forms.ValidationError('N° Orden invalido.')
        return nro_orden_input


    def clean_fecha(self):
    
        fecha_input = self.cleaned_data['fecha']

        # Validar que la fecha tenga el formato "dd/mm/yyyy" usando una expresión regular
        pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        if not pattern.match(fecha_input):
            raise forms.ValidationError('El formato de la fecha debe ser "dd/mm/yyyy".')

        # Validar que la fecha sea válida en el calendario
        try:
            fecha_valida = datetime.strptime(fecha_input, '%d/%m/%Y')
        except ValueError:
            raise forms.ValidationError('Fecha no válida en el calendario.')
        if(datetime.strptime(fecha_input, '%d/%m/%Y') > datetime.today()):
            raise forms.ValidationError('Fecha no válida.')
        
        # Si es necesario, puedes devolver la fecha como objeto datetime
        # return fecha_valida
        hora = datetime.now().strftime(" %H:%M")
        return fecha_input + hora


    def clean_vendedor(self):
        vendedor_input = self.cleaned_data['vendedor']
        vendedores_permitidos = [p.nombre.lower() for p in getVendedores]

        if vendedor_input.lower() not in vendedores_permitidos:
            raise forms.ValidationError('Vendedor no válido')

        return vendedor_input


    def clean_supervisor(self):
        supervisor_input = self.cleaned_data['supervisor']
        supervisores_permitidos = [p.nombre.lower() for p in getSupervisores]

        if supervisor_input.lower() not in supervisores_permitidos:
            raise forms.ValidationError('Supervisor no válido')

        return supervisor_input
    

# class FormCreateAdjudicacion(forms.Form):
#     nro_contrato = forms.CharField(required=True, max_length=10)
#     modalidad = forms.CharField(required=True,max_length=30)
#     nro_cuotas = forms.IntegerField(required=True)
#     anticipo = forms.IntegerField(required=True)
#     importe = forms.FloatField(required=True)    
#     tasa_interes = forms.FloatField(required=True)
#     intereses_generados = forms.FloatField(required=True)
#     importe_x_cuota =forms.FloatField(required=True)
#     total_a_pagar = forms.FloatField(required=True)
#     fecha = forms.CharField(required=True,max_length=10)
#     tipo_producto =forms.CharField(required=True)
#     producto = forms.CharField(required=True)
#     agencia = forms.CharField(required=True)
#     observaciones = forms.CharField(required=False,widget=forms.Textarea(attrs={"rows": 5}))

#     def clean_producto(self):
#         producto_input = self.cleaned_data['producto']
#         producto_permitidos = [p.nombre.lower() for p in getProducts]

#         if producto_input.lower() not in producto_permitidos:
#             raise forms.ValidationError('Producto no válido')

#         return producto_input
    

#     def clean_modalidad(self):
#         modalidad_input = self.cleaned_data['modalidad']
#         modalidades_permitidas = [m[0].lower() for m in modalidades]

#         if modalidad_input.lower() not in modalidades_permitidas:
#             raise forms.ValidationError('Modalidad no válida')

#         return modalidad_input
    

#     def clean_tipo_producto(self):
#         tipo_producto_input = self.cleaned_data['tipo_producto']
#         tipo_producto_permitidas = [m[0].lower() for m in tipoProductos]

#         if tipo_producto_input.lower() not in tipo_producto_permitidas:
#             raise forms.ValidationError('Tipo de producto no válido')

#         return tipo_producto_input
    
        
#     def clean_nro_solicitud(self):
#         nro_solicitud_input = self.cleaned_data['nro_solicitud']

#         # Verificar que el valor ingresado sea un número
#         if not nro_solicitud_input.isdigit():
#             raise forms.ValidationError('El numero de solicitud debe ser un valor numérico.')
        
#         return nro_solicitud_input
    
    
#     def clean_nro_orden(self):
#         nro_orden_input = self.cleaned_data['nro_orden']

#         # Verificar que el valor ingresado sea un número
#         if not nro_orden_input.isdigit():
#             raise forms.ValidationError('El numero de orden debe ser un valor numérico.')
        
#         return nro_orden_input


#     def clean_fecha(self):
    
#         fecha_input = self.cleaned_data['fecha']

#         # Validar que la fecha tenga el formato "dd/mm/yyyy" usando una expresión regular
#         pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
#         if not pattern.match(fecha_input):
#             raise forms.ValidationError('El formato de la fecha debe ser "dd/mm/yyyy".')

#         # Validar que la fecha sea válida en el calendario
#         try:
#             fecha_valida = datetime.strptime(fecha_input, '%d/%m/%Y')
#         except ValueError:
#             raise forms.ValidationError('Fecha no válida en el calendario.')
#         if(datetime.strptime(fecha_input, '%d/%m/%Y') > datetime.today()):
#             raise forms.ValidationError('Fecha no válida.')
        
#         # Si es necesario, puedes devolver la fecha como objeto datetime
#         # return fecha_valida
#         return fecha_input


#     # def clean_agencia(self):
#     #     agencia_input = self.cleaned_data['agencia']
#     #     agencias_permitidos = [a[0].lower() for a in agencias]

#     #     if agencia_input.lower() not in agencias_permitidos:
#     #         raise forms.ValidationError('Agencia no válido')

#     #     return agencia_input
    

class FormChangePAck(forms.Form):
    nro_solicitud = forms.CharField(required=True, max_length=10)
    modalidad =forms.CharField(required=True,max_length=30)
    nro_cuotas = forms.IntegerField(required=True)
    anticipo = forms.IntegerField(required=True)
    # primer_cuota = forms.IntegerField(required=True)
    importe = forms.FloatField(required=True)    
    tasa_interes = forms.FloatField(required=True)
    intereses_generados = forms.FloatField(required=True)
    importe_x_cuota =forms.FloatField(required=True)
    total_a_pagar = forms.FloatField(required=True)
    fecha = forms.CharField(required=True,max_length=10)
    tipo_producto =forms.CharField(required=True)
    producto = forms.CharField(required=True)
    paquete = forms.CharField(required=True)
    nro_orden = forms.CharField(required=True)
    vendedor =forms.CharField(required=True)
    supervisor = forms.CharField(required=True)
    observaciones = forms.CharField(required=False,widget=forms.Textarea(attrs={"rows": 5}))

    def clean_producto(self):
        producto_input = self.cleaned_data['producto']
        producto_permitidos = [p.nombre.lower() for p in getProducts]
        print(producto_permitidos)

        if producto_input.lower() not in producto_permitidos:
            raise forms.ValidationError('Producto no válido')

        return producto_input
    

    def clean_modalidad(self):
        modalidad_input = self.cleaned_data['modalidad']
        modalidades_permitidas = [m[0].lower() for m in modalidades]

        if modalidad_input.lower() not in modalidades_permitidas:
            raise forms.ValidationError('Modalidad no válida')

        return modalidad_input
    

    def clean_tipo_producto(self):
        tipo_producto_input = self.cleaned_data['tipo_producto']
        tipo_producto_permitidas = [m[0].lower() for m in tipoProductos]

        if tipo_producto_input.lower() not in tipo_producto_permitidas:
            raise forms.ValidationError('Tipo de producto no válido')

        return tipo_producto_input
    

    def clean_paquete(self):
        paquete_input = self.cleaned_data['paquete']
        paquetes_permitidas = [m[0].lower() for m in paquetes]

        if paquete_input.lower() not in paquetes_permitidas:
            raise forms.ValidationError('Paquete no válido')

        return paquete_input

        
    def clean_nro_solicitud(self):
        nro_solicitud_input = self.cleaned_data['nro_solicitud']

        # Verificar que el valor ingresado sea un número
        if not nro_solicitud_input.isdigit():
            raise forms.ValidationError('El numero de solicitud debe ser un valor numérico.')
        
        return nro_solicitud_input
    
    
    def clean_nro_orden(self):
        nro_orden_input = self.cleaned_data['nro_orden']

        # Verificar que el valor ingresado sea un número
        if not nro_orden_input.isdigit():
            raise forms.ValidationError('El numero de orden debe ser un valor numérico.')
        
        return nro_orden_input


    def clean_fecha(self):
    
        fecha_input = self.cleaned_data['fecha']

        # Validar que la fecha tenga el formato "dd/mm/yyyy" usando una expresión regular
        pattern = re.compile(r'^\d{2}/\d{2}/\d{4}$')
        if not pattern.match(fecha_input):
            raise forms.ValidationError('El formato de la fecha debe ser "dd/mm/yyyy".')

        # Validar que la fecha sea válida en el calendario
        try:
            fecha_valida = datetime.strptime(fecha_input, '%d/%m/%Y')
        except ValueError:
            raise forms.ValidationError('Fecha no válida en el calendario.')
        if(datetime.strptime(fecha_input, '%d/%m/%Y') > datetime.today()):
            raise forms.ValidationError('Fecha no válida.')
        
        # Si es necesario, puedes devolver la fecha como objeto datetime
        # return fecha_valida
        return fecha_input


    def clean_vendedor(self):
        vendedor_input = self.cleaned_data['vendedor']
        vendedores_permitidos = [p.nombre.lower() for p in getVendedores]
        print(vendedores_permitidos)

        if vendedor_input.lower() not in vendedores_permitidos:
            raise forms.ValidationError('Vendedor no válido')

        return vendedor_input


    def clean_supervisor(self):
        supervisor_input = self.cleaned_data['supervisor']
        supervisores_permitidos = [p.nombre.lower() for p in getSupervisores]
        print(supervisores_permitidos)

        if supervisor_input.lower() not in supervisores_permitidos:
            raise forms.ValidationError('Supervisor no válido')

        return supervisor_input
    