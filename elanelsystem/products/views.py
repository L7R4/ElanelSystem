from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import generic
from .models import Plan
import datetime
import os
import json
from dateutil.relativedelta import relativedelta

class CRUDPlanes(generic.View):
    template_name = "planes.html"
    model = Plan
    def get(self,request,*args,**kwargs):
        planes = Plan.objects.all()
        context = {"planes": planes}
        print(context)
        return render(request, self.template_name, context)
