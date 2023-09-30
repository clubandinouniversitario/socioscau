from ..models import ShortNotice
from django.http import HttpResponse
import io
from django.shortcuts import get_object_or_404

def PDFNoticeView(request, pk):
    buff = io.BytesIO()
    notice = get_object_or_404(ShortNotice, pk=pk)
    pdf_name = "Aviso de Salida - " + notice.location
    pdf_name = pdf_name.replace(',', ' - ')

    doc = notice.createPDF(buff, pdf_name)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + pdf_name + '.pdf'
    response.write(buff.getvalue())

    buff.close()
    return response


