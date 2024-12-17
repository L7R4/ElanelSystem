from django.forms import ValidationError
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin

from .mixins import TestLogin
from .models import ArqueoCaja, Ventas,CoeficientesListadePrecios,MovimientoExterno,CuentaCobranza
from users.models import Cliente, Sucursal,Usuario
from .models import Ventas
from products.models import Products,Plan
import datetime
import os,re
import json
from django.shortcuts import reverse
from dateutil.relativedelta import relativedelta
import locale
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import *
from collections import defaultdict
import elanelsystem.settings as settings
from elanelsystem.views import filterMainManage, convertirValoresALista
from django.forms.models import model_to_dict
from django.templatetags.static import static

from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from elanelsystem.utils import *

import pandas as pd
from django.core.files.storage import FileSystemStorage


class Resumen(TestLogin,PermissionRequiredMixin,generic.View):
    permission_required = "sales.my_ver_resumen"
    # login_url = "/ventas/caja/"
    template_name = 'resumen.html'

    def get(self,request,*args,**kwargs):
        ventas = Ventas.objects.all()
        context = {
            "ventas" : ventas,
        }
        # print(context)
        return render(request, self.template_name, context)
    
    def handle_no_permission(self):
        return redirect("users:list_customers")


#region API CRM
# def requestMovimientosCRM(request):
#     cuotas_data = requestCuotas(request)
#     movimientosExternos = requestMovimientosExternos(request)
    
#     # Combinar datos de cuotas y movimientos externos
#     all_movimientos = json.loads(cuotas_data.content) + json.loads(movimientosExternos.content)
#     all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha_pago'], '%d/%m/%Y %H:%M'),reverse=True)
   
#     response_data ={
#         "request": request.GET,
#         "movs": all_movimientosTidy
#     }
#     movs = filterMovs(response_data["movs"],response_data["request"])
    
#     # Crear un diccionario por mes y sumar los ingresos
#     ingresos_por_mes = defaultdict(float)
#     egresos_por_mes = defaultdict(float)
#     for mov in movs:
#         tipo_movimiento = mov.get('tipoMovimiento')
#         monto_pagado = mov.get('pagado', 0)
#         fecha_pago = mov.get('fecha_pago')

#         if tipo_movimiento == 'Ingreso' and fecha_pago:
#             mes = int(fecha_pago.split('-')[1])
#             ingresos_por_mes[mes] += monto_pagado
#         elif tipo_movimiento == 'Egreso' and fecha_pago:
#             mes = int(fecha_pago.split('-')[1])
#             egresos_por_mes[mes] += monto_pagado
#     # Crear la lista final de sumas por mes
#     sumasIngreso_por_mes = [ingresos_por_mes.get(mes, 0) for mes in range(1, 13)]
#     sumasEgreso_por_mes = [egresos_por_mes.get(mes, 0) for mes in range(1, 13)]
    
#     return JsonResponse({"sumasIngreso_por_mes": sumasIngreso_por_mes,"sumasEgreso_por_mes":sumasEgreso_por_mes}, safe=False)
#endregion

#region Ventas - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch') # Para no guardar el cache 
class CrearVenta(TestLogin,generic.DetailView):
    model = Cliente
    template_name = "create_sale.html"

    def get(self,request,*args, **kwargs):
        self.object = self.get_object()

        customers = Cliente.objects.all()
        products = Products.objects.all()
        sucursal = request.user.sucursales.all()[0]

        vendedores = Usuario.objects.filter(sucursales__in=[sucursal], rango__in=["Vendedor","Supervisor"])
        supervisores = Usuario.objects.filter(sucursales__in = [sucursal], rango="Supervisor")
        
        campaniasDelAño = getAllCampaniaOfYear()
        campaniaActual = getCampaniaActual()
        campaniaAnterior = campaniasDelAño[campaniasDelAño.index(campaniaActual) - 1]
        campaniasDisponibles = []

        #region Para determinar si se habilita la campaña anterior
        fechaActual = datetime.now()
        ultimo_dia_mes_pasado = datetime.now().replace(day=1) - relativedelta(days=1)
        diferencia_dias = (fechaActual - ultimo_dia_mes_pasado).days

        if(diferencia_dias > 5): # Si la diferencia de dias es mayor a 5 dias, no se puede asignar la campania porque ya paso el tiempo limite para dar de alta una venta en la campania anterior
            campaniasDisponibles = [campaniaActual]
        else:
            campaniasDisponibles = [campaniaActual,campaniaAnterior]
        #endregion
        context ={
            "object": self.object,
            'customers': customers, 
            'products': products, 
            'agencias': request.user.sucursales.all(), 
            'agenciaActual': request.user.sucursales.all()[0], 
            'campaniasDisponibles': campaniasDisponibles, 
            'vendedores': vendedores, 
            'supervisores': supervisores, 
        }

        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form =json.loads(request.body)
        errors ={}
        sale = Ventas()

        
        # Para guardar como objeto Producto
        producto = form["producto"]
        if producto and not Products.objects.filter(nombre=producto).exists():
            errors['producto'] = 'Producto invalido.' 
        else:
            producto = Products.objects.get(nombre=producto)
            sale.producto = producto

        # Validar la sucursal
        agencia = form["agencia"] 

        if agencia and not Sucursal.objects.filter(pseudonimo=agencia).exists():
            errors['agencia'] = 'Agencia invalida.'
        else:
            agencia = Sucursal.objects.get(pseudonimo=agencia)
            sale.agencia = agencia

        
        # Comprobar el vendendor
        vendedor = form['vendedor']
        if  not Usuario.objects.filter(nombre__iexact=vendedor).exists():
            errors['vendedor'] = 'Vendedor invalido.' 
        else:
            vendedor_instance = Usuario.objects.get(nombre__iexact=form['vendedor'])
            sale.vendedor = vendedor_instance

        # Comprobar el supervisor
        supervisor = form['supervisor']
        if not Usuario.objects.filter(nombre__iexact=supervisor).exists():
            errors['supervisor'] = 'Supervisor invalido.' 
        else:
            supervisor_instance = Usuario.objects.get(nombre__iexact=form['supervisor'])
            sale.supervisor = supervisor_instance
            
        # Para guardar la cantidad de contratos que se haga
        chances = []
        chance_counter = 1
        while f'nro_contrato_{chance_counter}' in form:

            # Obtenemos y validamos el nro de contrato
            nro_contrato = form.get(f'nro_contrato_{chance_counter}')
            if not re.match(r'^\d+$', nro_contrato):
                raise ValidationError({f'nro_contrato_{chance_counter}': 'Debe contener solo números.'})
            
            # Obtenemos y validamos el nro de orden
            nro_orden = form.get(f'nro_orden_{chance_counter}')
            if not re.match(r'^\d+$', nro_orden):
                raise ValidationError({f'nro_orden_{chance_counter}': 'Debe contener solo números.'})
            
            # Si ambos campos son validos, los añadimos a la lista de chances
            if nro_contrato and nro_orden:
                chances.append({
                    'nro_contrato': nro_contrato,
                    'nro_orden': nro_orden
                })
            chance_counter += 1

        # Guardar las chances en el campo JSONField
        sale.cantidadContratos = chances


        sale.nro_cliente = Cliente.objects.get(nro_cliente__iexact=self.get_object().nro_cliente)
        
        sale.modalidad = form['modalidad'] if form['modalidad'] else ""
        sale.importe = int(form['importe'])
        sale.primer_cuota = int(form['primer_cuota'])  if form['primer_cuota'] else 0
        sale.anticipo = int(form['anticipo']) if form['anticipo'] else 0
        sale.tasa_interes = float(form['tasa_interes']) if form['tasa_interes'] else 0
        sale.intereses_generados = int(form['intereses_generados']) if form['intereses_generados'] else 0
        sale.importe_x_cuota = int(form['importe_x_cuota']) if form['importe_x_cuota'] else 0
        sale.nro_cuotas = int(form['nro_cuotas'])
        sale.total_a_pagar = int(form['total_a_pagar']) if form['total_a_pagar'] else 0
        sale.fecha = form['fecha']
        sale.tipo_producto = form['tipo_producto']
        sale.paquete = form['paquete']
        sale.campania = form['campania']
        sale.observaciones = form['observaciones']
        sale.fecha = form['fecha'] + " 00:00"

        sale.crearCuotas()
        sale.setDefaultFields()

        
        try:
            sale.full_clean()
        except ValidationError as e:
            errors.update(e.message_dict)
       
        if len(errors) != 0:
            print(errors)
            return JsonResponse({'success': False, 'errors': errors}, safe=False)
        else:
            sale.save()

            return JsonResponse({'success': True,'urlRedirect': reverse('users:cuentaUser',args=[sale.nro_cliente.pk])}, safe=False)



def generarContratoParaImportar(index_start, index_end, file_path, agencia,nextIndiceBusquedaCuotas):
    print(f"Indices {index_start}-{index_end}")
    try:
            cantidadContratos = index_end - index_start

            # Leer la hoja "Cuotas" del archivo Excel
            sheetResumen = formatear_columnas(file_path, sheet_name="RESUMEN")
            sheetEstados = formatear_columnas(file_path, sheet_name="ESTADOS")
            # print(sheetEstados.columns)


            modelosProvisorios = ["Producto","Vendedor","Supervisor"]   
                

            rowVenta = sheetResumen.iloc[index_start] # Se extrae una fila nada mas para completar la Informacion general 
            # print(f"Numero de venta --> {rowVenta['id_venta']}")
            newVenta = Ventas()
            newVenta.nro_cliente = Cliente.objects.filter(nro_cliente = rowVenta["cod_cli"]).first()
            newVenta.modalidad = rowVenta["modalidad"].title()
            newVenta.nro_operacion = str(int(rowVenta['id_venta']))
            newVenta.importe = float(rowVenta["importe"]) * cantidadContratos
            newVenta.agencia = Sucursal.objects.get(pseudonimo = agencia)
            newVenta.tasa_interes = round((float(rowVenta["tasa_de_inte"]) * cantidadContratos) * 100,2)
            newVenta.producto = Products.objects.filter(nombre = handle_nan(rowVenta["producto"].title())).first()
            newVenta.fecha = format_date(rowVenta["fecha_incripcion"]) + " 00:00"
            newVenta.vendedor = Usuario.objects.filter(nombre = handle_nan(rowVenta["vendedor"]).title()).first()
            newVenta.supervisor = Usuario.objects.filter(nombre = handle_nan(rowVenta["superv"]).title()).first() 
            newVenta.paquete = rowVenta["paq"].capitalize() if rowVenta["paq"] != "BASE" else "Basico"
            newVenta.campania = obtenerCampaña_atraves_fecha(format_date(rowVenta["fecha_incripcion"]))
            newVenta.tipo_producto = Products.objects.filter(nombre = rowVenta["producto"].title()).first().tipo_de_producto if Products.objects.filter(nombre = rowVenta["producto"].title()).first() else ""
            newVenta.observaciones = handle_nan(rowVenta["comentarios__observaciones"]) 
            total_a_pagar = 0


            listaContratos = []

            for i in range(index_start, index_end):
                fila = sheetResumen.iloc[i]

                #region Guardar los contratos
                nro_contrato = str(int(fila["contrato"]))
                nro_orden = str(int(fila["nro_de_orden"]))
                listaContratos.append({"nro_contrato":nro_contrato, "nro_orden":nro_orden })
                #endregion
                
            newVenta.cantidadContratos = listaContratos    
    
            cuotas = []
            for i in range(nextIndiceBusquedaCuotas, len(sheetEstados)):
                filaEstado = sheetEstados.iloc[i]
                try:
                    if(int(filaEstado["id_venta"]) == int(rowVenta['id_venta'])):

                        cuota = filaEstado["cuotas"].replace(" ","").split("-")[1]
                        # print(f"Tipo de fecha de vencimiento {type(filaEstado['fecha_venc'])}")

                        # print(f"Fecha de vencimiento {filaEstado['fecha_venc']}")
                        
                        total_a_pagar += int(filaEstado["importe_cuotas"])
                        if(filaEstado["cuotas"] == "cuota -  0"):
                            info = {
                                "cuota" :f'Cuota {cuota}',
                                "nro_operacion": str(int(rowVenta['id_venta'])),
                                "status": str(filaEstado["estado"]).title() if filaEstado["estado"] not in ["Vencido", "BAJA"] else "Atrasado" ,
                                "total": int(filaEstado["importe_cuotas"]) * cantidadContratos,
                                "descuento": {'autorizado': "", 'monto': 0},
                                "bloqueada": False,
                                "fechaDeVencimiento":"", 
                                "diasRetraso": 0,
                                "pagos":[{
                                    "monto": int(filaEstado["importe_cuotas"]) * cantidadContratos,
                                    "metodoPago": filaEstado["medio_de_pago"].title(),
                                    "fecha": format_date(filaEstado["fecha_de_pago"]),
                                    "cobrador": filaEstado["cobrador"].capitalize(),
                                }],
                            }
                        
                        else:
                            info = {
                                "cuota" :f'Cuota {cuota}',
                                "nro_operacion": str(int(rowVenta['id_venta'])),
                                "status": str(filaEstado["estado"]).title() if filaEstado["estado"] not in ["Vencido", "BAJA"] else "Atrasado",
                                "total": int(filaEstado["importe_cuotas"]) * cantidadContratos,
                                "descuento": {'autorizado': "", 'monto': 0},
                                "bloqueada": False,
                                "fechaDeVencimiento":format_date(filaEstado["fecha_venc"]) + " 00:00", 
                                "diasRetraso": int(float(str(filaEstado["dias_de_mora"]).replace("-",""))),
                                "interesPorMora": 0,
                                "totalFinal": 0,
                            }
                            if(info["status"] == "Pagado"):
                                info["pagos"] = [{
                                    "monto": int(filaEstado["importe_cuotas"]) * cantidadContratos,
                                    "metodoPago": filaEstado["medio_de_pago"].title(),
                                    "fecha": format_date(filaEstado["fecha_de_pago"]),
                                    "cobrador": filaEstado["cobrador"].capitalize(),
                                }]
                            else:
                                info["pagos"] = []
                            
                        cuotas.append(info)
                    else:
                        # print(filaEstado)
                        break
                except Exception as e:
                    print(f"Error en la hoja de cuotas, en la fila {filaEstado}\n\n ------------------------------- \n\n")
                    print(f"Error: {e}")
                    raise
                    

                        
            cuotas.reverse()
            newVenta.total_a_pagar = float(total_a_pagar * cantidadContratos)
            newVenta.cuotas=bloquer_desbloquear_cuotas(cuotas)
            newVenta.primer_cuota = newVenta.cuotas[1]["total"]
            newVenta.anticipo = newVenta.cuotas[0]["total"]
            newVenta.intereses_generados = newVenta.total_a_pagar - newVenta.importe
            newVenta.importe_x_cuota = newVenta.cuotas[2]["total"]
            newVenta.nro_cuotas = len(cuotas)-1
            newVenta.setDefaultFields()
            newVenta.save()
            return nextIndiceBusquedaCuotas + (len(cuotas) * cantidadContratos)
    except Exception as e:
            print(f"Error en la venta en general, en la fila {index_start}\n\n ------------------------------- \n\n")
            print(rowVenta)
            print(f"Error {e}")
            raise


def importVentas(request):
    if request.method == "POST":
        # Obtener el archivo subido
        archivo_excel = request.FILES['file']
        agencia = request.POST.get('agencia')

        # Guardar temporalmente el archivo
        fs = FileSystemStorage()
        filename = fs.save(archivo_excel.name, archivo_excel)
        file_path = fs.path(filename)
        cantidad_nuevas_ventas = 0
        todosLosContratos = obtener_todos_los_contratos()

        
        try:
            # Leer la hoja "Cuotas" del archivo Excel
            sheetResumen = formatear_columnas(file_path, sheet_name="RESUMEN")

            index_pivot,row_pivot = next(sheetResumen.iterrows())
            i= -1
            nextIndiceBusquedaCuotas = 0 # Almacena la fila de la hoja de ESTADOs para continuar buscando las cuotas y no comenzar de 0
            while i < len(sheetResumen):
                i += 1
                if(cantidad_nuevas_ventas == 5):
                    break
                if not (str(sheetResumen.iloc[i]["contrato"]) in todosLosContratos):
                    if(Cliente.objects.filter(nro_cliente = sheetResumen.iloc[i]["cod_cli"]).exists()):
                        if(row_pivot["cod_cli"] != sheetResumen.iloc[i]["cod_cli"] or row_pivot["fecha_incripcion"] != sheetResumen.iloc[i]["fecha_incripcion"] or row_pivot["producto"] != sheetResumen.iloc[i]["producto"]):
                            cantidad_nuevas_ventas +=1
                            # print(f"Indice para continuar buscando las cuotas: --> {nextIndiceBusquedaCuotas}")
                            nextIndiceBusquedaCuotas = generarContratoParaImportar(index_pivot, i, file_path, agencia,nextIndiceBusquedaCuotas)
                            row_pivot = sheetResumen.iloc[i]
                            index_pivot = i
                            i -= 1
                        else:
                            print(f"El cliente no existe la fila {index_pivot} de la hoja de resumen\n\n ------------------------------- \n\n")
                            continue
                    else:
                        continue

            # Eliminar el archivo después de procesarlo
            fs.delete(filename)
            
            iconMessage = "/static/images/icons/checkMark.svg"
            message = f"Datos importados correctamente. Se agregaron {cantidad_nuevas_ventas} nuevas ventas"
            return JsonResponse({"message": message, "iconMessage": iconMessage, "status": True})

        except Exception as e:
            print(f"Error al importar: {e}")

            iconMessage = "/static/images/icons/error_icon.svg"
            message = "Error al procesar el archivo"
            return JsonResponse({"message": message, "iconMessage": iconMessage, "status": False})

    return render(request, 'importar_cuotas.html')


def requestVendedores_Supervisores(request):
    request = json.loads(request.body)
    sucursal = request["agencia"] if request["agencia"] else ""
    
    vendedores = []
    supervisores = []

    if request["agencia"] !="":
        vendedores = Usuario.objects.filter(sucursales__pseudonimo = sucursal, rango__in=["Vendedor","Supervisor"])
        supervisores = Usuario.objects.filter(sucursales__pseudonimo = sucursal, rango="Supervisor")
    
    vendedores = [vendedor.nombre for vendedor in vendedores]
    supervisores = [supervisor.nombre for supervisor in supervisores]

 

    return JsonResponse({"vendedores":vendedores,"supervisores":supervisores}, safe=False)

#region Detalle de ventas y funciones de ventas
class DetailSale(TestLogin,generic.DetailView):
    model = Ventas
    template_name = "detail_sale.html"

    def get(self,request,*args,**kwargs):
        context ={}
        self.object = self.get_object()
        request.session["ventaPK"] = self.object.pk
        sale_target = Ventas.objects.get(pk=self.object.id)
        self.object.testVencimientoCuotas()
        request.session["statusKeyPorcentajeBaja"] = False

        if(self.object.adjudicado):
            self.object.addPorcentajeAdjudicacion()
        context["changeTitularidad"] = list(reversed(self.object.cambioTitularidadField))
        context['cuotas'] = sale_target.cuotas
        context['cobradores'] = CuentaCobranza.objects.all()
        context["object"] = self.object
        context["nro_cuotas"] = sale_target.nro_cuotas
        context["urlRedirectPDF"] = reverse("sales:bajaPDF",args=[self.object.pk])
        context['urlUser'] = reverse("users:cuentaUser", args=[self.object.pk])
        context['deleteSaleUrl'] = reverse("sales:delete_sale", args=[self.object.pk])
        request.session["venta"] = model_to_dict(self.object)

        try:
            if len(self.object.cuotas_pagadas()) >= 6:
                context["porcetageDefault"] = 50
            else:
                context["porcetageDefault"] = 0
        except IndexError as e:
            context["porcetageDefault"] = 0
        
        
        return render(request,self.template_name,context)
    
# Eliminar una venta
def eliminarVenta(request,pk):
    form = json.loads(request.body)
    nro_operacion = form["nro_operacion_delete"]

    venta = Ventas.objects.get(pk=pk)
    if(venta.nro_operacion == int(nro_operacion)):
        try:
            venta.delete()
            return JsonResponse({"status": True,'urlRedirect': reverse('users:cuentaUser', args=[venta.nro_cliente.pk])}, safe=False)
        except Exception:
            return JsonResponse({"status": False,"message":"Error al eliminar la venta"}, safe=False)
    else:
        return JsonResponse({"status": False,"message":"Numero incorrecto"}, safe=False)


# Anula una cuota de una venta
def anularCuota(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            permisosUser = request.user.get_all_permissions()

            venta = Ventas.objects.get(pk=request.session["venta"]["id"])
            cuota = data.get('cuota')
            cuotasPagadas = venta.cuotas_pagadas()

            ultima_cuotaPagadaSinCredito = getCuotasPagadasSinCredito(cuotasPagadas)[-1]

            if  ultima_cuotaPagadaSinCredito["cuota"] == cuota and "sales.my_anular_cuotas" in permisosUser:            
                if(request.user.additional_passwords["anular_cuotas"]["password"] == data.get("password")):
                    venta.anularCuota(cuota)
                else:
                    return JsonResponse({"status": False,"password": False,"message":"Contraseña incorrecta"}, safe=False)
                
            return JsonResponse({"status": True,"password":True,"message":"Cuota anulada correctamente"}, safe=False)
        except Exception as error:
            print("Error")
            print(error)
            return JsonResponse({"status": False,"password":True,"message":"Error al anular la cuota","detalleError":str(error)}, safe=False)


# Aplica el descuento a una cuota
def aplicarDescuentoCuota(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            venta = Ventas.objects.get(pk=request.session["venta"]["id"])
            cuota = data.get('cuota')
            descuento = data.get('descuento')
            autorizado = data.get('autorizado')

            venta.aplicarDescuento(cuota,int(descuento),autorizado)

            return JsonResponse({"status": True,"message":"Descuento aplicado correctamente"}, safe=False)

        except Exception as error:   
            return JsonResponse({"status": False,"message":"Descuento fallido","detalleError":str(error)}, safe=False)


# Obtenemos una cuota
def getUnaCuotaDeUnaVenta(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            venta = Ventas.objects.get(pk=int(data.get("ventaID")))
            cuotas = venta.cuotas
            cuotaRequest = data.get("cuota")
            bloqueado_path = static('images/icons/iconBloqueado.png')
            permisosUser = request.user.get_all_permissions()
            buttonAnularCuota = '<button type="button" id="anularButton" onclick="htmlPassAnularCuota()" class="delete-button-default">Anular cuota</button>'

            cuotasPagadas_parciales = venta.cuotas_pagadas() + venta.cuotas_parciales()
            lista_cuotasPagadasSinCredito = getCuotasPagadasSinCredito(cuotasPagadas_parciales)
            
            for cuota in cuotas:
                if cuota["cuota"] == cuotaRequest:
                    cuota["styleBloqueado"] = f"background-image: url('{bloqueado_path}')"
                    if len(lista_cuotasPagadasSinCredito) != 0 and lista_cuotasPagadasSinCredito[-1]["cuota"] == cuota["cuota"] and "sales.my_anular_cuotas" in permisosUser:
                        cuota["buttonAnularCuota"] = buttonAnularCuota
                    return JsonResponse(cuota, safe=False)

        except Exception as error:
            return JsonResponse({"status": False,"message":"Error al obtener la cuota","detalleError":str(error)}, safe=False)


# Pagar una cuota
def pagarCuota(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            venta = Ventas.objects.get(pk=int(data.get("ventaID")))

            cuotaRequest = data.get("cuota")
            metodoPago = data.get("metodoPago")
            formaPago = data.get("typePayment") # Si es parcial o total
            cobrador = data.get('cobrador')
            monto = 0
            if(formaPago =="total"):
                cuota = list(filter(lambda x:x["cuota"] == cuotaRequest,venta.cuotas))[0]
                monto = cuota["total"]
            elif(formaPago =="parcial"):
                monto = data.get('valorParcial')

            venta.pagarCuota(cuotaRequest,int(monto),metodoPago,cobrador,request.user.nombre) #Funcion que paga parcialmente
                
            return JsonResponse({"status": True,"message":f"Pago de {cuotaRequest.lower()} exitosa"}, safe=False)
        except Exception as error:
            print(error)
            return JsonResponse({"status": False,"message":f"Error en el pago de {cuotaRequest.lower()}","detalleError":str(error)}, safe=False)


#Dar de baja una venta
def darBaja(request,pk):
    if(request.method == "POST"):
        try:
            # Obtenemos el formulario
            porcentage = json.loads(request.body)["porcentage"]
            motivoDetalle = json.loads(request.body)["motivo"]
            motivoDescripcion = json.loads(request.body)["motivoDescripcion"]
            responsable = request.user.nombre


            venta = get_object_or_404(Ventas, id=pk)
            porcentajeEsperado = venta.porcentajeADevolver() #El porcentaje valido sin modificaciones HABILITADAS
            porcentajeDeBajaHabilitado = porcentage if request.session["statusKeyPorcentajeBaja"] else porcentajeEsperado
            
            # Damos la baja 
            venta.darBaja("cliente",porcentajeDeBajaHabilitado,motivoDetalle,motivoDescripcion,responsable)
            venta.save()
            response_data = {
                'status': True,
                'urlPDF': reverse("sales:bajaPDF", args=[pk]),
                'urlUser': reverse("users:cuentaUser", args=[venta.nro_cliente.pk])
            }
            request.session["statusKeyPorcentajeBaja"] = False
            return JsonResponse(response_data, safe=False)
        except Exception as error:
            return JsonResponse({'status': False, 'message':str(error)}, safe=False)
            
#endregion 


class PlanRecupero(generic.DetailView):
    model = Ventas
    template_name = "plan_recupero.html"

    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        url = request.path
        cuotasPagadas = self.object.cuotas_pagadas()

        sucursal = request.user.sucursales.all()[0]

        vendedores = Usuario.objects.filter(sucursales__in=[sucursal], rango__in=["Vendedor","Supervisor"])
        supervisores = Usuario.objects.filter(sucursales__in = [sucursal], rango="Supervisor")

        # Suma las cuotas pagadas para calcular el total a adjudicar
        valoresCuotasPagadas = [item["pagado"] for item in cuotasPagadas]
        sumaCuotasPagadas = sum(valoresCuotasPagadas)
        campaniaActual = getCampaniaActual()

        #region Para determinar si se habilita la campaña anterior
        fechaActual = datetime.datetime.now()
        ultimo_dia_mes_pasado = datetime.datetime.now().replace(day=1) - relativedelta(days=1)
        diferencia_dias = (fechaActual - ultimo_dia_mes_pasado).days

        context = {
            'venta': self.object,
            'agencias': request.user.sucursales.all(), 
            'agenciaActual': request.user.sucursales.all()[0],
            'campania': campaniaActual,
            'sumaCuotasPagadas' : int(sumaCuotasPagadas),
            'autorizado_por':  Sucursal.objects.get(pseudonimo = request.user.sucursales.all()[0].pseudonimo).gerente.nombre,
            'cantidad_cuotas_pagadas': len(cuotasPagadas),
            'idCliente': self.object.nro_cliente.nro_cliente,
            'vendedores': vendedores, 
            'supervisores': supervisores, 
        }
        
        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form =json.loads(request.body)
        errors ={}
        sale = Ventas()

        
        # Para guardar como objeto Producto
        producto = form["producto"]
        if producto and not Products.objects.filter(nombre=producto).exists():
            errors['producto'] = 'Producto invalido.' 
        else:
            producto = Products.objects.get(nombre=producto)
            sale.producto = producto

        # Validar la sucursal
        agencia = form["agencia"] 

        if agencia and not Sucursal.objects.filter(pseudonimo=agencia).exists():
            errors['agencia'] = 'Agencia invalida.'
        else:
            agencia = Sucursal.objects.get(pseudonimo=agencia)
            sale.agencia = agencia

        
        # Comprobar el vendendor
        vendedor = form['vendedor']
        if  not Usuario.objects.filter(nombre__iexact=vendedor).exists():
            errors['vendedor'] = 'Vendedor invalido.' 
        else:
            vendedor_instance = Usuario.objects.get(nombre__iexact=form['vendedor'])
            sale.vendedor = vendedor_instance

        # Comprobar el supervisor
        supervisor = form['supervisor']
        if not Usuario.objects.filter(nombre__iexact=supervisor).exists():
            errors['supervisor'] = 'Supervisor invalido.' 
        else:
            supervisor_instance = Usuario.objects.get(nombre__iexact=form['supervisor'])
            sale.supervisor = supervisor_instance




        sale.nro_cliente = Cliente.objects.get(nro_cliente__iexact=self.get_object().nro_cliente.nro_cliente)
        
        sale.nro_contrato = form['nro_contrato']
        sale.modalidad = form['modalidad'] if form['modalidad'] else ""
        sale.importe = int(form['importe'])
        sale.primer_cuota = int(form['primer_cuota']) if form['primer_cuota'] else 0
        sale.anticipo = int(form['anticipo']) if form['anticipo'] else 0
        sale.tasa_interes = float(form['tasa_interes']) if form['tasa_interes'] else 0
        sale.intereses_generados = int(form['intereses_generados']) if form['intereses_generados'] else 0
        sale.importe_x_cuota = int(form['importe_x_cuota']) if form['importe_x_cuota'] else 0
        sale.nro_cuotas = int(form['nro_cuotas'])
        sale.total_a_pagar = int(form['total_a_pagar']) if form['total_a_pagar'] else 0
        sale.fecha = form['fecha']
        sale.tipo_producto = form['tipo_producto']
        sale.paquete = form['paquete']
        sale.nro_orden = form['nro_orden']
        sale.campania = form['campania']
        sale.observaciones = form['observaciones']
        
        try:
            sale.full_clean()
        except ValidationError as e:
            errors.update(e.message_dict)
       
        if len(errors) != 0:
            print(errors)
            return JsonResponse({'success': False, 'errors': errors}, safe=False)
        else:
            sale.fecha = form['fecha'] + " 00:00"
            sale.crearCuotas()
            sale.save()

            # Dar de baja la venta a la que se le aplico el plan de recupero
            self.object.planRecupero("plan recupero",request.user.nombre, sale.observaciones,sale.pk)
            self.object.save()
            return JsonResponse({'success': True,'urlRedirect': reverse('users:cuentaUser',args=[sale.nro_cliente.pk])}, safe=False)

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=True), name='dispatch') # Para no guardar el cache 
class CreateAdjudicacion(TestLogin,generic.DetailView):
    model = Ventas
    template_name = "create_adjudicacion.html"
    
    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        url = request.path
        cuotasPagadas_parciales = self.object.cuotas_pagadas() + self.object.cuotas_parciales()
        sumaDePagos = 0

        # Suma las cuotas pagadas para calcular el total a adjudicar
        for cuota in cuotasPagadas_parciales:
            pagos = cuota["pagos"]
            sumaDePagos += sum([pago["monto"] for pago in pagos])


        tipoDeAdjudicacion = "NEGOCIACIÓN" if "negociacion" in url else "SORTEO"
        
        intereses = CoeficientesListadePrecios.objects.all()
        
        context = {
            'venta': self.object,
            'intereses' : intereses,
            'agencias': Sucursal.objects.all(),
            'sumaCuotasPagadas' : int(sumaDePagos),
            'autorizado_por':  Sucursal.objects.get(pseudonimo = request.user.sucursales.all()[0].pseudonimo).gerente.nombre,
            'cantidad_cuotas_pagadas': len(self.object.cuotas_pagadas()),
            'tipoDeAdjudicacion' : tipoDeAdjudicacion,
            'idCliente': self.object.nro_cliente.nro_cliente,
        }
        
        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):

        form =json.loads(request.body)
        self.object = self.get_object()
        numeroOperacion = self.object.nro_operacion
        errors ={}
        cuotasPagadas_parciales = self.object.cuotas_pagadas() + self.object.cuotas_parciales()


        # Suma las cuotas pagadas para calcular el total a adjudicar
        sumaDePagos = 0
        for cuota in cuotasPagadas_parciales:
            pagos = cuota["pagos"]
            sumaDePagos += sum([pago["monto"] for pago in pagos])

        sale = Ventas()

        # Obtenemos el tipo de adjudicacion - - - - - - - - - - - - - - - - - - - -
        url = request.path
        tipo_adjudicacion = "sorteo" if "sorteo" in url else "negociacion"

        # Validar el producto
        producto = form['producto']

        if producto and not Products.objects.filter(nombre=producto).exists():
            errors['producto'] = 'Producto invalido.' 

        elif producto:
            producto = Products.objects.get(nombre=producto)
            sale.producto = producto



        # Validar la sucursal
        agencia = form['agencia']
        if agencia and not Sucursal.objects.filter(pseudonimo=agencia).exists():
            errors['agencia'] = 'Agencia invalida.' 

        elif agencia:
            agencia = Sucursal.objects.get(pseudonimo=agencia)
            sale.agencia = agencia

        contratoAdjudicado = form["nro_contrato"]
        sale.adjudicado["status"] = True
    
        sale.nro_cliente = Cliente.objects.get(pk=request.session["venta"]["nro_cliente"])
        sale.nro_operacion = request.session["venta"]["nro_operacion"]
        sale.agencia = Sucursal.objects.get(pseudonimo = form["agencia"])
        sale.vendedor = Usuario.objects.get(pk = request.session["venta"]["vendedor"])
        sale.supervisor = Usuario.objects.get(pk = request.session["venta"]["supervisor"])
        sale.cantidadContratos = request.session["venta"]["cantidadContratos"]
        sale.paquete = str(request.session["venta"]["paquete"])
        sale.campania = getCampaniaActual()
        sale.importe = int(form['importe'])
        sale.modalidad = form['modalidad']
        sale.nro_cuotas = int(form['nro_cuotas'])
        sale.tasa_interes = int(form['tasa_interes'])
        sale.intereses_generados = int(form['intereses_generados'])
        sale.importe_x_cuota = int(form['importe_x_cuota'])
        sale.total_a_pagar = int(form['total_a_pagar'])
        sale.tipo_producto = form['tipo_producto']
        sale.fecha = form['fecha']

        sale.observaciones = form['observaciones']
        sale.fecha = form['fecha'] + " 00:00"

        sale.setDefaultFields()
        sale.crearCuotas() # Crea las cuotas
        if(tipo_adjudicacion == "sorteo"):
            sale.acreditarCuotasPorAnticipo(sumaDePagos,request.user.nombre)
        sale.crearAdjudicacion(contratoAdjudicado,numeroOperacion,tipo_adjudicacion) # Crea la adjudicacion eliminando la cuota 0
        


        try:
            sale.full_clean()
        except ValidationError as e:
            errors.update(e.message_dict)
       
        if len(errors) != 0:
            print(errors)
            return JsonResponse({'success': False, 'errors': errors}, safe=False)  
        else:
            sale.save()
            
            self.object.darBaja("adjudicacion",0,"","",request.user.nombre) # Da de baja la venta que fue adjudicada
            self.object.save()

            
            # #region Para enviar el correo
            # subject = 'Se envio una adjudicacion'
            # template = 'adjudicacion_correo.html'
            # context = {'nombre': 'Usuario'}  # Contexto para renderizar el template
            # from_email = 'lautaror@elanelsys.com'
            # to_email = 'lautaro.rodriguez553@gmail.com'

            # send_html_email(subject, template, context, from_email, to_email)
            #endregion
            return JsonResponse({'success': True,'urlRedirect':reverse_lazy('users:cuentaUser',args=[request.session["venta"]["nro_cliente"]])}, safe=False)          
        

class ChangePack(TestLogin,generic.DetailView):
    model = Ventas
    template_name = "change_pack.html"

    def get(self,request,*args, **kwargs):
        self.object = self.get_object()

        customers = Cliente.objects.all()
        products = Products.objects.all()
        sucursal = request.user.sucursales.all()[0]

        vendedores = Usuario.objects.filter(sucursales__in=[sucursal], rango__in=["Vendedor","Supervisor"])
        supervisores = Usuario.objects.filter(sucursales__in = [sucursal], rango="Supervisor")


        cuotasPagadas_parciales = self.object.cuotas_pagadas() + self.object.cuotas_parciales()
        sumaDePagos = 0

        # Suma las cuotas pagadas para calcular el total a adjudicar
        for cuota in cuotasPagadas_parciales:
            pagos = cuota["pagos"]
            sumaDePagos += sum([pago["monto"] for pago in pagos])

        contratosAsociados = ""
        for contrato in self.object.cantidadContratos:
            contratosAsociados += f" {contrato['nro_contrato']} -"
        contratosAsociados = contratosAsociados[:-1] # Elimina el ultimo guion
        
        context = {
            'venta': self.object,
            'agencias': Sucursal.objects.all(),
            "contratosAsociados": contratosAsociados,
            'sumaCuotasPagadas' : int(sumaDePagos),
            'cantidad_cuotas_pagadas': len(self.object.cuotas_pagadas()),
            'idCliente': self.object.nro_cliente.nro_cliente,
            'customers': customers,
            'vendedores': vendedores, 
            'supervisores': supervisores, 
            'products': products, 
        }


        return render(request,self.template_name,context)
    

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form =json.loads(request.body)
        errors ={}
        cuotasPagadas_parciales = self.object.cuotas_pagadas() + self.object.cuotas_parciales()

        sumaDePagos = 0
        for cuota in cuotasPagadas_parciales:
            pagos = cuota["pagos"]
            sumaDePagos += sum([pago["monto"] for pago in pagos])

        sale = Ventas()

        # Validar el producto
        producto = form['producto']

        if producto and not Products.objects.filter(nombre=producto).exists():
            errors['producto'] = 'Producto invalido.' 

        elif producto:
            producto = Products.objects.get(nombre=producto)
            sale.producto = producto
    
        # Para guardar la cantidad de contratos que se haga
        chances = []
        chance_counter = 1
        while f'nro_contrato_{chance_counter}' in form:

            # Obtenemos y validamos el nro de contrato
            nro_contrato = form.get(f'nro_contrato_{chance_counter}')
            if not re.match(r'^\d+$', nro_contrato):
                raise ValidationError({f'nro_contrato_{chance_counter}': 'Debe contener solo números.'})
            
            # Obtenemos y validamos el nro de orden
            nro_orden = form.get(f'nro_orden_{chance_counter}')
            if not re.match(r'^\d+$', nro_orden):
                raise ValidationError({f'nro_orden_{chance_counter}': 'Debe contener solo números.'})
            
            # Si ambos campos son validos, los añadimos a la lista de chances
            if nro_contrato and nro_orden:
                chances.append({
                    'nro_contrato': nro_contrato,
                    'nro_orden': nro_orden
                })
            chance_counter += 1

        # Guardar las chances en el campo JSONField
        sale.cantidadContratos = chances

        sale.nro_cliente = Cliente.objects.get(pk=request.session["venta"]["nro_cliente"])
        sale.nro_operacion = request.session["venta"]["nro_operacion"]
        sale.agencia = self.object.agencia
        sale.vendedor = Usuario.objects.get(pk = request.session["venta"]["vendedor"])
        sale.supervisor = Usuario.objects.get(pk = request.session["venta"]["supervisor"])
        sale.paquete = str(request.session["venta"]["paquete"])
        sale.campania = getCampaniaActual()
        sale.importe = int(form['importe'])
        sale.modalidad = form['modalidad']
        sale.nro_cuotas = int(form['nro_cuotas'])
        sale.tasa_interes = float(form['tasa_interes'])
        sale.intereses_generados = int(form['intereses_generados'])
        sale.importe_x_cuota = int(form['importe_x_cuota'])
        sale.total_a_pagar = int(form['total_a_pagar'])
        sale.primer_cuota = int(form['primer_cuota'])
        sale.anticipo = int(form['anticipo'])
        sale.fecha = form['fecha']
        sale.tipo_producto = form['tipo_producto']
        sale.observaciones = form['observaciones']
        
        try:
            sale.full_clean()
        except ValidationError as e:
            errors.update(e.message_dict)
       
        if len(errors) != 0:
            return JsonResponse({'success': False, 'errors': errors}, safe=False) 
        else:
            sale.fecha = form['fecha'] + " 00:00"
            sale.crearCuotas()
            sale.acreditarCuotasPorAnticipo(sumaDePagos,request.user.nombre)
            sale.save()

            self.object.darBaja("cambio de pack",0,"","",request.user.nombre) # Da de baja la venta que fue cambiada de pack
            self.object.save()
            return JsonResponse({'success': True,'urlRedirect':reverse_lazy('sales:detail_sale',args=[sale.pk])}, safe=False)


class ChangeTitularidad(TestLogin,generic.DetailView):
    template_name = 'changeTitularidad.html'
    model = Ventas


    def get(self,request,*args, **kwargs):
        self.object = self.get_object()
        customers = Cliente.objects.all()
        context = {
            "customers": customers,
            "object": self.object,
        }
        return render(request, self.template_name,context)

    def post(self,request,*args,**kwargs):
        self.object = self.get_object()
        form = json.loads(request.body)
        newCustomer = form["customer"]

        dniNewCustomer = Cliente.objects.all().filter(dni=newCustomer)[0]
        if(dniNewCustomer == self.object.nro_cliente):
            return JsonResponse({'success': False, 'errors': "EL CLIENTE NUEVO NO PUEDE SER IGUAL AL ANTIGUO"}, safe=False)
        else:
            # Coloca los datos del cambio de titularidad
            cuotasPagadas_parciales = self.object.cuotas_pagadas() + self.object.cuotas_parciales()
            lastCuota = getCuotasPagadasSinCredito(cuotasPagadas_parciales)[-1]

            self.object.createCambioTitularidad(lastCuota,request.user.nombre,self.object.nro_cliente.nombre,dniNewCustomer.nombre,self.object.nro_cliente.pk,dniNewCustomer.pk)
            
            # Actualiza el dueño de la venta
            self.object.nro_cliente = dniNewCustomer
            self.object.save()
            return JsonResponse({'success': True,'urlRedirect': reverse("sales:detail_sale",args = [self.get_object().pk])}, safe=False) 

   
class PostVenta(TestLogin,generic.View):
    template_name = 'postVenta.html'

    def get(self,request,campania,*args,**kwargs):
        ventas = Ventas.objects.filter(campania=campania)
        sucursalDefault = searchSucursalFromStrings("Sucursal central")

        auditorias_realidas = Ventas.objects.filter(agencia=sucursalDefault,campania=campania,auditoria__0__realizada=True)
        auditorias_pendientes = Ventas.objects.filter(agencia=sucursalDefault,campania=campania,auditoria__0__realizada=False)

        auditorias_realidas_list = list(auditorias_realidas.values())
        auditorias_aprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == True,auditorias_realidas_list)))
        auditorias_desaprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == False,auditorias_realidas_list)))
        

        context = {
            "ventas": ventas,
            "amountVentas": ventas.count(),
            "sucursalDefault": Sucursal.objects.get(pseudonimo="Sucursal central"),
            "sucursales": Sucursal.objects.all(),
            "auditorias_pendientes": len(auditorias_pendientes),
            "auditorias_realizadas": len(auditorias_realidas),
            "auditorias_aprobadas": auditorias_aprobadas,
            "auditorias_desaprobadas": auditorias_desaprobadas,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if(HttpResponse.status_code == 200):
            response_data = {}
            grade = request.POST.get("grade")
            id_venta = request.POST.get("idVenta")
            venta = Ventas.objects.get(pk=id_venta)
            comentarios = request.POST.get("comentarioInput")

            new_dict_auditoria = {}
            ultimaAuditoria = venta.auditoria[-1]
            if grade == "a":
                    new_dict_auditoria["grade"] = True
                    response_data["message"] = "Auditoria aprobada exitosamente"
                    response_data["status"] = True
                    response_data["grade"] = True
                    response_data["gradeString"] = "Aprobada"

            elif grade == "d":
                new_dict_auditoria["grade"]  = False
                response_data["message"] = "Auditoria desaprobada exitosamente"
                response_data["grade"] = False
                response_data["status"] = True
                response_data["gradeString"] = "Desaprobada"

            new_dict_auditoria["realizada"] = True
            new_dict_auditoria["comentarios"] = comentarios
            new_dict_auditoria["fecha_hora"] = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")

            if ultimaAuditoria["version"] == 0:
                new_dict_auditoria["version"] = 1
                venta.auditoria[0] = new_dict_auditoria
            else:
                new_dict_auditoria["version"] = ultimaAuditoria["version"] + 1
                venta.auditoria.append(new_dict_auditoria)
            venta.save()
            
            response_data["comentarioString"] = comentarios
            response_data["fechaString"] = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")
            return JsonResponse(response_data, safe=False)
        else:
            response_data = {"status": False,"message": "Hubo un error al generar la auditoria"}
            return JsonResponse(response_data, safe=False)


class PanelVentasSuspendidas(TestLogin,generic.View):
    template_name = 'panel_ventas_suspendidas.html'

    def get(self,request,*args,**kwargs):
        context = {}
        return render(request, self.template_name, context)
    
    def post(self,request,*args,**kwargs):
        data = json.loads(request.body)
        sucursal = request.user.sucursales.all()[0]
        saldo_Afavor = 0
        try:
            venta = Ventas.objects.get(nro_operacion=data["nro_operacion"], suspendida=True, agencia=sucursal)
            for cuotaPagada in venta.cuotas_pagadas():
                pagosDeCuota = cuotaPagada["pagos"]
                saldo_Afavor += sum(pago["monto"] for pago in pagosDeCuota)

            cuotas_pagadas = len(venta.cuotas_pagadas())
            cuotas_atrasadas = len([cuota for cuota in venta.cuotas if cuota["status"] == "Atrasado"])

            context = {
                "cliente": venta.nro_cliente.nombre,
                "tipo_producto": venta.producto.tipo_de_producto,
                "producto": venta.producto.nombre,
                "importe": venta.producto.plan.valor_nominal,
                "nro_orden": 1,
                "fecha_inscripcion": venta.fecha,
                "nro_operacion": venta.nro_operacion,
                "cuotas_atrasadas": cuotas_atrasadas,
                "saldo_Afavor": saldo_Afavor,
                "cuotas_pagadas": cuotas_pagadas,
                "urlSimularPlanRecupero": reverse("sales:simuladorPlanrecupero",args=[venta.pk]),

            }
            return JsonResponse({"status": True,"venta":context}, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse({"status": True,"venta":None}, safe=False)


class SimuladorPlanRecupero(TestLogin,generic.DetailView):
    template_name = "simulador_plan_recupero.html"
    model = Ventas

    def get(self,request,*args,**kwargs):
        self.object = self.get_object()

        cuotasPagadas = self.object.cuotas_pagadas()

        # Suma las cuotas pagadas para calcular el total a adjudicar
        valoresCuotasPagadas = [item["pagado"] for item in cuotasPagadas]
        sumaCuotasPagadas = sum(valoresCuotasPagadas)

        context = {
            'venta' : self.object,
            'sumaCuotasPagadas' : int(sumaCuotasPagadas),
            'cantidad_cuotas_pagadas': len(cuotasPagadas),
        }
        return render(request, self.template_name, context)
        
#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#region PDFs - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def viewsPDFBaja(request,pk):
    operacionBaja = Ventas.objects.get(id=pk)
    context ={
                "nroContrato":operacionBaja.nro_contrato,
                "cliente": operacionBaja.nro_cliente.nombre,
                "domicilio": operacionBaja.nro_cliente.domic,
                "localidad": operacionBaja.nro_cliente.loc,
                "pack": operacionBaja.producto.plan.tipodePlan,
                "producto": operacionBaja.producto.nombre,
                "cantCuotasPagadas" : len(operacionBaja.cuotas_pagadas()),
                "cuotas" : operacionBaja.nro_cuotas,
                "agencia" : f'{operacionBaja.agencia.localidad}, {operacionBaja.agencia.provincia}',
                "motivo" : operacionBaja.deBaja["detalleMotivo"],
                "observacion" : operacionBaja.deBaja["observacion"],
                "dineroDevolver" : operacionBaja.calcularDineroADevolver(),
                "fecha" : operacionBaja.deBaja["fecha"],
            }
            
    bajaName = f'baja_venta_nro_contrato_{str(context["nroContrato"])}'
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "baja.pdf")
    
    printPDFBaja(context,request.build_absolute_uri(),urlPDF)

    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+bajaName+'.pdf'
        return response

def viewPDFTitularidad(request,pk,idCambio):
    operacionTitu = Ventas.objects.get(id=pk)
    newCustomer = operacionTitu.cambioTitularidadField[idCambio]["pkNewCustomer"]
    oldCustomer = operacionTitu.cambioTitularidadField[idCambio]["oldCustomer"]

    # Establece el idioma local en español
    locale.setlocale(locale.LC_TIME, 'es_AR.utf8')

    dateNow = datetime.date.today().strftime("%d de %B de %Y")
    context ={
                "fechaNow": dateNow,
                "oldCustomer": oldCustomer,
                "nroOperacion":operacionTitu.nro_operacion,
                "cliente": Cliente.objects.get(id=newCustomer).nombre,
                "domicilio": Cliente.objects.get(id=newCustomer).domic,
                "dni": Cliente.objects.get(id=newCustomer).dni,
                "localidad": Cliente.objects.get(id=newCustomer).loc,
                "provincia": Cliente.objects.get(id=newCustomer).prov,
                "estado_civil" : Cliente.objects.get(id=newCustomer).estado_civil,
                "fecha_nac" : Cliente.objects.get(id=newCustomer).fec_nacimiento,
                "ocupacion" : Cliente.objects.get(id=newCustomer).ocupacion,
                "telefono" : Cliente.objects.get(id=newCustomer).tel,
            }
            
    titularName = "Cambio de titular: " + str(Cliente.objects.get(id=newCustomer).nombre) + str(operacionTitu.nro_orden)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "titularidad.pdf")
    
    printPDFtitularidad(context,request.build_absolute_uri(),urlPDF)

    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+titularName+'.pdf'
        return response

def viewPDFArqueo(request,pk):
    
    # Establece el idioma local en español
    locale.setlocale(locale.LC_TIME, 'es_AR.utf8')
    arqueo = ArqueoCaja.objects.get(id=pk)

    # Para pasar los movimientos del dia
    #region Logica para obtener los movimientos segun los filtros aplicados 
    agencia = "Todas" if not request.GET.get("agencia") else request.GET.get("agencia")
    all_movimientos = dataStructureMoviemientosYCannons(agencia)
    all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha'], '%d/%m/%Y %H:%M'),reverse=True) # Ordenar de mas nuevo a mas viejo los movimientos
   
    
    #endregion
    movsToday = list(filter(lambda x: x["fecha"][:10] == arqueo.fecha,all_movimientosTidy))

    movsDetalles = [
        {
            "Moviem.": d.get("tipoMovimiento", "-"),
            "Compro.": "---" if d.get("tipoComprobante") is None or d.get("tipoComprobante") == "null" else d.get("tipoComprobante", "---"),
            "Nro Comprob.": "---" if d.get("nroComprobante") is None or d.get("nroComprobante") == "null" else d.get("nroComprobante", "---"),
            "Denominacion": "---" if d.get("denominacion") is None or d.get("denominacion") == "null" else d.get("denominacion", "---"),
            "T. de ID": "---" if d.get("tipoIdentificacion") is None or d.get("tipoIdentificacion") == "null" else d.get("tipoIdentificacion", "---"),
            "Nro de ID.": "---" if d.get("nroIdentificacion") is None or d.get("nroIdentificacion") == "null" else d.get("nroIdentificacion", "---"),
            "Sucursal": d.get("sucursal", "-"),
            "Moneda": "---" if d.get("tipoMoneda") is None or d.get("tipoMoneda") == "null" else d.get("tipoMoneda", "---"),
            "Dinero": d.get("pagado", "-"),
            "Metodo de pago": d.get("metodoPago", "-"),
            "Ente recau.": d.get("ente", "-"),
            "Concepto": d.get("concepto", "-"),
            "Fecha": d.get("fecha", "-"),
        }
        for d in movsToday
    ]
    
    # Para pasar el resumen de tipos de pagos
    resumenData = {}
    tiposDePago = {"efectivo":"Efectivo",
                       "banco":"Banco", 
                       "posnet":"Posnet", 
                       "merPago":"Mercado Pago", 
                       "transferencia":"Transferencia"}  
        
    montoTotal = 0
    for clave in tiposDePago.keys():
        itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], movsToday))
        montoTypePaymentEgreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Egreso'])
        montoTypePaymentIngreso = sum([monto['pagado'] for monto in itemsTypePayment if monto['tipoMovimiento'] == 'Ingreso'])
        montoTypePayment = montoTypePaymentIngreso - montoTypePaymentEgreso
        montoTotal += montoTypePayment 
        resumenData[clave] = montoTypePayment
    resumenData["total"] = montoTotal

    # Para pasar los datos del arqueo 
    arqueoData ={
                "fecha": arqueo.fecha,
                "agencia": arqueo.agencia,
                "responsable":arqueo.responsable,
                "admin": arqueo.admin,
                "totalPlanilla": arqueo.totalPlanilla,
                "totalSegunDiarioCaja": arqueo.totalSegunDiarioCaja,
                "diferencia": arqueo.diferencia,
                "observaciones": arqueo.observaciones,
                "p2000": arqueo.detalle["p2000"],
                "p1000": arqueo.detalle["p1000"],
                "p500": arqueo.detalle["p500"],
                "p200": arqueo.detalle["p200"],
                "p100": arqueo.detalle["p100"],
                "p50": arqueo.detalle["p50"],
                "p20": arqueo.detalle["p20"],
                "p10": arqueo.detalle["p10"],
                "p5": arqueo.detalle["p5"],
                "p2": arqueo.detalle["p2"],
            }
            
    arqueoName = "Arqueo de caja del: " + str(arqueo.fecha)
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "arqueo.pdf")
    
    printPDFarqueo({"arqueoData": arqueoData, "movsData": movsDetalles,"resumenData": resumenData},request.build_absolute_uri(),urlPDF)

    # Para enviar PDF
    fechaYHoraHoy = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")

    url_referer = request.META.get('HTTP_REFERER', '')
    if reverse("sales:oldArqueos") not in url_referer:
        sendEmailPDF("",os.path.join(settings.BASE_DIR, 'pdfs/arqueo.pdf'),"Cierre de caja del: " + fechaYHoraHoy)
    


    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+arqueoName+'.pdf'
        return response

def viewsPDFInforme(request):
    # Establece el idioma local en español
    # locale.setlocale(locale.LC_TIME, 'es_AR.utf8')
    datos = request.session.get('informe_data', {})

    # Para pasar el detalles de los movs

    datos_modificado = [
        {
            "Moviem.": d.get("tipo_mov", "-"),
            "Compro.": "---" if d.get("tipoComprobante") is None or d.get("tipoComprobante") == "null" else d.get("tipoComprobante", "---"),
            "Nro Comprob.": "---" if d.get("nroComprobante") is None or d.get("nroComprobante") == "null" else d.get("nroComprobante", "---"),
            "Denominacion": "---" if d.get("denominacion") is None or d.get("denominacion") == "null" else d.get("denominacion", "---"),
            "T. de ID": "---" if d.get("tipoIdentificacion") is None or d.get("tipoIdentificacion") == "null" else d.get("tipoIdentificacion", "---"),
            "Nro de ID.": "---" if d.get("nroIdentificacion") is None or d.get("nroIdentificacion") == "null" else d.get("nroIdentificacion", "---"),
            "Sucursal": d.get("sucursal", "-"),
            "Moneda": "---" if d.get("tipoMoneda") is None or d.get("tipoMoneda") == "null" else d.get("tipoMoneda", "---"),
            "Dinero": d.get("monto", "-"),
            "Metodo de pago": d.get("metodoPago", "-"),
            "Ente recau.": d.get("ente") if d.get("ente") is not None else d.get("cobrador"),
            "Concepto": d.get("concepto", "-"),
            "Fecha": d.get("fecha", "-"),
        }
        for d in datos
    ]
    # Para pasar el resumen de tipos de pagos 

    metodosPagosResumen={}
    tiposDePago = {"efectivo":"Efectivo",
                   "banco":"Banco", 
                   "posnet":"Posnet", 
                   "merPago":"Mercado Pago", 
                   "transferencia":"Transferencia"}  
    
    montoTotal = 0
    for clave in tiposDePago.keys():
        itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], datos))
        montoTypePaymentEgreso = sum([monto['monto'] for monto in itemsTypePayment if monto['tipo_mov'] == 'Egreso'])
        montoTypePaymentIngreso = sum([monto['monto'] for monto in itemsTypePayment if monto['tipo_mov'] == 'Ingreso'])
        montoTypePayment = montoTypePaymentIngreso - montoTypePaymentEgreso
        montoTotal += montoTypePayment 
        metodosPagosResumen[clave] = montoTypePayment
    metodosPagosResumen["total"] = montoTotal

    informeName = "Informe"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "liquidacion.pdf")
    
    # printPDFinforme({"data":datos_modificado},request.build_absolute_uri(),urlPDF)
    printPDFinforme({"data":datos_modificado,"metodosPagosResumen":metodosPagosResumen},request.build_absolute_uri(),urlPDF)

    
    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+informeName+'.pdf'
        return response

def viewPDFInformeAndSend(request):
    # Para enviar PDF
    fechaYHoraHoy = datetime.datetime.today().strftime("%d/%m/%Y %H:%M")
    sendEmailPDF("valerossi2004@hotmail.com",os.path.join(settings.BASE_DIR, 'pdfs/informe.pdf'),"Informe del: " + fechaYHoraHoy)
    return viewsPDFInforme(request)

def viewsPDFInformePostVenta(request):
    datos = request.session.get('postVenta_info', {})

    # Para pasar el detalles de los movs
    datos_modificado = [
        {
            "Nro Orden": d.get("nroOrden", "---"),
            "Camp": d.get("campania","---"),
            "Cliente": d.get("cliente","---"),
            "DNI": d.get("dni","---"),
            "Fec insc": d.get("fec_insc","---"),
            "Tel": d.get("tel","---"),
            "CP": d.get("cp", "---"),
            "Prov": d.get("prov","---"),
            "Loc": d.get("loc", "---"),
            "Direc": d.get("direc", "---"),
            "Vendedor": d.get("vendedor", "---"),
            "Supervisor": d.get("supervisor", "---"),
            "Auditoria": d.get("auditoria", "---"),
        }
        for d in datos["ventas"]
    ]

    # CONFIG PARA VER PDF 
    informeName = "Informe Post-Venta"
    urlPDF= os.path.join(settings.PDF_STORAGE_DIR, "postVentaInforme.pdf")
    
    printPDFinformePostVenta({"data":datos_modificado},request.build_absolute_uri(),urlPDF)

    
    with open(urlPDF, 'rb') as pdf_file:
        response = HttpResponse(pdf_file,content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename='+informeName+'.pdf'
        return response

#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#region Caja - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Caja(TestLogin,generic.View):
    template_name = "caja.html"
    FILTROS_EXISTENTES = (
        ("tipo_mov","Tipo de movimiento"),
        ("metodoPago", "Metodo de pago"),
        ("fecha", "Fecha"),
        ("cobrador","Cobrador"),
        ("agencia","Agencia"),
    )

    def get(self,request,*args, **kwargs):
        context ={}
        context["cobradores"] = CuentaCobranza.objects.all()
        context["agencias"] = Sucursal.objects.all()
        context["agenciasDisponibles"] = request.user.sucursales.all()
        
        # print(os.path.join(settings.BASE_DIR, "templates/mailPlantilla.html"))
        paramsDict = (request.GET).dict()
        clearContext = {key: value for key, value in paramsDict.items() if value != '' and key != 'page'}

        
        # Extrae las tuplas segun los querys filtrados en clearContext
        filtros_activados = list(filter(lambda x: x[0] in clearContext, self.FILTROS_EXISTENTES))

        # Por cada tupla se coloca de llave el valor 1 y se extrae el valor mediante su key de clearContext ( Por eso es [x[0]] )
        # Es lo mismo que decir clearContext["metodoPago"], etc, etc
        context["filtros"] = list(map(lambda x: {x[1], clearContext[x[0]]}, filtros_activados))
        
        return render(request, self.template_name, context)
        

class CierreCaja(TestLogin,generic.View):

    template_name = 'cierreDeCaja.html'

    def get(self,request,*args,**kwargs):
        context = {}
        json_data = requestMovimientos(request)
        movsData = json.loads(json_data.content)
        
        today = datetime.date.today().strftime("%d/%m/%Y %H:%M")
        movimientosHoy = filtroMovimientos_fecha(str(today),movsData["data"],str(today))

        # FILTRA LOS MOVIMIENTOS SEGUN SE TIPO DE MOVIMIENTO
        movimientos_Ingreso_Hoy = list(filter(lambda x: x["tipo_mov"] == "Ingreso" and x["tipo_pago"] == "Efectivo", movimientosHoy))
        movimientos_Egreso_Hoy = list(filter(lambda x:x["tipo_mov"] == "Egreso" and x["tipo_pago"] == "Efectivo", movimientosHoy))

        # SUMA EL TOTAL DE SEGUN EL TIPO DE MOVIMIENTO
        montoTotal_Ingreso_Hoy = sum([item["pagado"] for item in movimientos_Ingreso_Hoy])
        montoTotal_Egreso_Hoy = sum([item["pagado"] for item in movimientos_Egreso_Hoy])

        if len(movimientosHoy) == 0:
            context["movs"] = 0
        else:
            context["movs"] = int(montoTotal_Ingreso_Hoy - montoTotal_Egreso_Hoy)

        context["sucursal"] = request.user.sucursal
        context["sucursales"] = Sucursal.objects.all()
        context["fecha"] =  datetime.date.today().strftime("%d/%m/%Y")
        context["admin"]= request.user
        
        return render(request, self.template_name, context)
    

    def post(self,request,*args,**kwargs):
        context= {}
        arqueo = ArqueoCaja()
        BILLETES = [2000,1000,500,200,100,50,20,10,5,2]
        
        # OBTIENE LOS DATOS----------------------------------------------------
        sucursal = request.POST.get("sucursal")
        localidad_buscada, provincia_buscada = map(str.strip, sucursal.split(","))
        sucursalObject = Sucursal.objects.get(localidad = localidad_buscada, provincia = provincia_buscada)

        fecha =  datetime.date.today().strftime("%d/%m/%Y %H:%M")
        admin = request.user
        responsable = request.POST.get("responsable")
        totalSegunDiarioCaja = request.POST.get("saldoSegunCaja")
        observaciones = request.POST.get("observaciones")
        
        total=0
        for b in BILLETES:
            billeteCantidad = request.POST.get("p"+ str(b))
            if(billeteCantidad == ""):
                billeteCantidad = 0
            
            billeteItem = {}
            billeteItem["cantidad"] = int(billeteCantidad)
            billeteItem["importeTotal"] = int(billeteCantidad) * b
            total += int(billeteCantidad) * b
            arqueo.detalle["p"+ str(b)] = billeteItem

        # ---------------------------------------------------------------------

        # COLOCA LOS DATOS ---------------------------------------------------
        
        arqueo.agencia = sucursalObject
        arqueo.fecha = fecha
        arqueo.admin = admin
        arqueo.responsable = responsable
        arqueo.totalPlanilla = total
        arqueo.totalSegunDiarioCaja = float(totalSegunDiarioCaja)
        arqueo.diferencia = total - float(totalSegunDiarioCaja)
        arqueo.observaciones = observaciones
        # ---------------------------------------------------------------------

        arqueo.save()

        response_data = {
            'success': True,
            'urlPDF': reverse("sales:arqueoPDF", args=[ArqueoCaja.objects.latest('pk').pk]),
            'urlCaja': reverse("sales:caja")
        }
        
        return JsonResponse(response_data, safe=False)


class OldArqueosView(TestLogin,generic.View):
    model = ArqueoCaja
    template_name= "listaDeArqueos.html"

    def get(self,request,*args, **kwargs):
        arqueos = ArqueoCaja.objects.filter(agencia = request.user.sucursal)
        context = {
            "arqueos": reversed(arqueos)
        }
        arqueos_list = []
        for a in arqueos:
            data_arqueo = {}
            data_arqueo["pk"] = a.pk
            data_arqueo["sucursal"] = a.agencia
            data_arqueo["fecha"] = a.fecha
            data_arqueo["admin"] = a.admin
            data_arqueo["responsable"] = a.responsable
            data_arqueo["totalPlanilla"] = a.totalPlanilla
            arqueos_list.append(data_arqueo)

        arqueos_list.reverse()
        data = json.dumps(arqueos_list)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponse(data, 'application/json')
        return render(request, self.template_name,context)
#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#region Specifics Functions - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def requestMovimientos(request):
    #region Logica para obtener los movimientos segun los filtros aplicados 
    agencia = request.user.sucursales.first().pseudonimo if not request.GET.get("agencia") else request.GET.get("agencia") # Si no hay agencia seleccionada, se coloca la primera sucursal del usuario
    
    all_movimientos = dataStructureMoviemientosYCannons(agencia)

    all_movimientosTidy = sorted(all_movimientos, key=lambda x: datetime.datetime.strptime(x['fecha'], '%d/%m/%Y %H:%M'),reverse=True) # Ordenar de mas nuevo a mas viejo los movimientos
    
    #region Limpiar los cannos que tienen pagos en forma de credito
    movsDePagosEnFormaCredito = [mov for mov in all_movimientosTidy if mov["metodoPago"] == "Credito"]

    #Elimina los pagos en forma de credito segun los indices
    for movs in movsDePagosEnFormaCredito:
        if (movs in all_movimientosTidy):
            all_movimientosTidy.remove(movs)
    #endregion

    response_data ={
        "request": request.GET,
        "movs": all_movimientosTidy
    }
    movs = filterMainManage(response_data["request"], response_data["movs"])
    
    #endregion
    
    #region Logica para pasar al template los filtros aplicados a los movimientos
    paramsDict = (request.GET).dict()
    FILTROS_EXISTENTES = (
        ("tipo_mov","Tipo de movimiento"),
        ("metodoPago", "Metodo de pago"),
        ("fecha", "Fecha"),
        ("cobrador","Cobrador"),
        ("agencia","Agencia"),
    )
    clearContext = {key: value for key, value in paramsDict.items() if value != '' and key != 'page'}

    # Extrae las tuplas segun los querys filtrados en clearContext
    filtros_activados = list(filter(lambda x: x[0] in clearContext, FILTROS_EXISTENTES))
    
    # Por cada tupla se coloca de llave el valor 1 y se extrae el valor mediante su key de clearContext ( Por eso es [x[0]] )
    # Es lo mismo que decir clearContext["metodoPago"], etc, etc
    filtros = list(map(lambda x: {x[1]: clearContext[x[0]]}, filtros_activados))
    #endregion
    
    request.session["informe_data"] = movs # Por si se quiere imprimir el informe

    # region Logica para obtener el resumen de cuenta de los diferentes tipos de pagos
    resumenEstadoCuenta={}
    tiposDePago = {"efectivo":"Efectivo",
                   "banco":"Banco", 
                   "posnet":"Posnet", 
                   "merPago":"Mercado Pago", 
                   "transferencia":"Transferencia"}  

    montoTotal = 0
    for clave in tiposDePago.keys():
        itemsTypePayment = list(filter(lambda x: x['metodoPago'] == tiposDePago[clave], movs))
        montoTypePaymentEgreso = sum([monto['monto'] for monto in itemsTypePayment if monto['tipo_mov'] == 'Egreso'])
        montoTypePaymentIngreso = sum([monto['monto'] for monto in itemsTypePayment if monto['tipo_mov'] == 'Ingreso'])
        montoTypePayment = montoTypePaymentIngreso - montoTypePaymentEgreso  
        montoTotal += montoTypePayment 
        resumenEstadoCuenta[clave] = montoTypePayment
    resumenEstadoCuenta["total"] = montoTotal

    #endregion

    #region Paginación
    page = request.GET.get('page')
    items_per_page = 10  # Número de elementos por página
    paginator = Paginator(movs, items_per_page)

    try:
        movs = paginator.page(page)
    except PageNotAnInteger:
        movs = paginator.page(1)
    except EmptyPage:
        movs = paginator.page(paginator.num_pages)
    #endregion -----------------------------------------------------

    return JsonResponse({"data": list(movs), "numbers_pages": paginator.num_pages,"filtros":filtros,"estadoCuenta":resumenEstadoCuenta}, safe=False)

# Funcion para crear un nuevo movimiento externo
def createNewMov(request):
    if request.method == 'POST':
        newMov = MovimientoExterno()
        movimiento = request.POST.get("movimiento")
        newMov.movimiento=movimiento
        newMov.agencia = Sucursal.objects.get(pseudonimo = request.POST.get('agencia'))
        newMov.metodoPago= request.POST.get('metodoPago')
        newMov.ente= request.POST.get('ente')
        newMov.fecha=datetime.datetime.today().strftime("%d/%m/%Y %H:%M")
        newMov.concepto= request.POST.get('concepto')
        newMov.metodoPago= request.POST.get('tipoPago')
        newMov.dinero= float(request.POST.get('dinero'))

        if movimiento == 'Ingreso':
            newMov.tipoMoneda = request.POST.get('tipoMoneda')
        elif movimiento == 'Egreso':
            newMov.tipoIdentificacion=request.POST.get('tipoID')
            newMov.nroIdentificacion=request.POST.get('nroIdentificacion')
            newMov.tipoComprobante=request.POST.get('tipoComprobante')
            newMov.nroComprobante=request.POST.get('nroComprobante')
            newMov.denominacion=request.POST.get('denominacion')
            if(request.POST.get('adelanto_premio') == "premio"):
                newMov.premio= True
            elif(request.POST.get('adelanto_premio') == "adelanto"):
                newMov.adelanto = True
        else:
            return HttpResponseBadRequest('Fallo en el servidor', status=405)
                 
        newMov.save()
        return JsonResponse({'status': True, 'message': 'Movimiento creado exitosamente'})
        

    return JsonResponse({'status': False, 'message': ' Ha sucedido un error y no se pudo completar la operacion'})

# Funcion para devolver las ventas (Utilizada en el sector de auditorias)
def requestVentas(request):
    if(request.method == "GET"):
        sucursal = request.GET.get('sucursal')
        campaign = request.GET.get('campania')
        responseData = {"ventas": [],"resumenAuditorias":{"pendientes": 0, "realizadas":0, "aprobadas":0, "desaprobadas":0}}
        
        sucursal = searchSucursalFromStrings(sucursal)
        allVentas = Ventas.objects.filter(campania=campaign, agencia=sucursal)

        auditorias_realidas = allVentas.filter(auditoria__0__realizada=True)
        responseData["resumenAuditorias"]["realizadas"] = len(auditorias_realidas)

        auditorias_pendientes = allVentas.filter(auditoria__0__realizada=False)
        responseData["resumenAuditorias"]["pendientes"] = len(auditorias_pendientes)

        auditorias_realidas_list = list(auditorias_realidas.values())
        auditorias_aprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == True,auditorias_realidas_list)))
        responseData["resumenAuditorias"]["aprobadas"] = auditorias_aprobadas

        auditorias_desaprobadas = len(list(filter(lambda x: x["auditoria"][-1]["grade"] == False,auditorias_realidas_list)))
        responseData["resumenAuditorias"]["desaprobadas"] = auditorias_desaprobadas

        for v in allVentas:
            ventaToDict = {
                "id": v.pk,
                "nroOrden": v.nro_orden,
                "campania": v.campania,
                "cliente": v.nro_cliente.nombre,
                "dni": v.nro_cliente.dni,
                "fec_insc": v.fecha,
                "tel": v.nro_cliente.tel,
                "cp": v.nro_cliente.cod_postal,
                "prov": v.nro_cliente.prov,
                "loc": v.nro_cliente.loc,
                "direc": v.nro_cliente.domic,
                "vendedor": str(v.vendedor),
                "supervisor": str(v.supervisor),
                "auditoria": v.auditoria,
            }
            responseData["ventas"].append(ventaToDict)
        request.session["postVenta_info"] = responseData

        return JsonResponse(responseData, safe=False)
   
#endregion - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


