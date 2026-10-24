from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import Documento


@login_required
@permission_required("documentos.my_ver_documentos", raise_exception=True)
def menu_documentos(request):
    return render(request, "documentos/menu.html", {"categorias": Documento.CATEGORIAS})


@login_required
@permission_required("documentos.my_ver_documentos", raise_exception=True)
def subir_documento(request, categoria):
    categorias_validas = dict(Documento.CATEGORIAS)
    if categoria not in categorias_validas:
        messages.error(request, "Categoría inválida.")
        return redirect("documentos:menu")

    if request.method == "POST":
        archivo = request.FILES.get("archivo")
        if not archivo:
            messages.error(request, "Tenés que seleccionar un archivo.")
            return render(request, "documentos/subir.html", {"categoria": categoria, "categoria_label": categorias_validas[categoria]})

        Documento.objects.create(
            categoria=categoria,
            archivo=archivo,
            nombre_original=archivo.name,
            descripcion=request.POST.get("descripcion", "").strip(),
            subido_por=request.user,
        )
        messages.success(request, "Archivo subido correctamente.")
        return redirect("documentos:listado")

    return render(request, "documentos/subir.html", {"categoria": categoria, "categoria_label": categorias_validas[categoria]})


@login_required
@permission_required("documentos.my_ver_documentos", raise_exception=True)
def listado_documentos(request):
    documentos = Documento.objects.select_related("subido_por").all()

    categoria = request.GET.get("categoria")
    if categoria:
        documentos = documentos.filter(categoria=categoria)

    paginator = Paginator(documentos, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "documentos/listado.html", {
        "page_obj": page_obj,
        "categorias": Documento.CATEGORIAS,
        "categoria_activa": categoria or "",
    })


@login_required
@permission_required("documentos.my_ver_documentos", raise_exception=True)
def eliminar_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if request.method == "POST":
        documento.archivo.delete(save=False)
        documento.delete()
        messages.success(request, "Documento eliminado.")
    return redirect("documentos:listado")
