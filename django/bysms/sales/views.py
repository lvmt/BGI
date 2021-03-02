from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse

from common.models import Customer


from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('sales/'))
template = env.get_template('customers.html')


def listorders(request):
    cmd = '''
    <div> this is test 
        <br>
        <h1> this is a title </h1>
        <p style="color:green; font:bold"> guss what i am </p>
    </div>
    '''
    return HttpResponse(cmd)


def people(request):
    return HttpResponse('<p style="color: green"> list all people</p>')


def helloworld(request):
    return HttpResponse('<p style="font:bold; color:orange"> hello world, lvmengting</p>')

# def listcustomers(request):
#     # 返回一个 QuerySet 对象 ，包含所有的表记录
#     # 每条表记录都是是一个dict对象，
#     # key 是字段名，value 是 字段值
#     qs = Customer.objects.values()

#     # 定义返回字符串
#     retStr = ''
#     for customer in  qs:
#         for name,value in customer.items():
#             retStr += f'{name} : {value} | '

#         # <br> 表示换行
#         retStr += '<br>'

#     return HttpResponse(retStr) 

# def listcustomers(request):
#     # 返回一个 QuerySet 对象 ，包含所有的表记录
#     qs = Customer.objects.values()

#     # 检查url中是否有参数phonenumber
#     ph =  request.GET.get('phonenumber',None)

#     # 如果有，添加过滤条件
#     if ph:
#         qs = qs.filter(phonenumber=ph)

#     # 定义返回字符串
#     retStr = ''
#     for customer in  qs:
#         for name,value in customer.items():
#             retStr += f'{name} : {value} | '
#         # <br> 表示换行
#         retStr += '<br>'

#     return HttpResponse(retStr)


# def listcustomers(request):
#     # 返回一个 QuerySet 对象 ，包含所有的表记录
#     qs = Customer.objects.values()

#     # 检查url中是否有参数phonenumber
#     ph =  request.GET.get('phonenumber',None)

#     # 如果有，添加过滤条件
#     if ph:
#         qs = qs.filter(phonenumber=ph)

#     # 生成html模板中要插入的html片段内容
#     tableContent = ''
#     for customer in  qs:
#         tableContent += '<tr>'

#         for name,value in customer.items():
#             tableContent += f'<td>{value}</td>'

#         tableContent += '</tr>'

#     return HttpResponse(html_template%tableContent)



def listcustomers(request):
    # 返回一个 QuerySet 对象 ，包含所有的表记录
    qs = Customer.objects.values()

    # 检查url中是否有参数phonenumber
    ph =  request.GET.get('phonenumber',None)

    # 如果有，添加过滤条件
    if ph:
        qs = qs.filter(phonenumber=ph)

    # 传入渲染模板需要的参数
    rendered = template.render(customers=qs)


    return HttpResponse(rendered)