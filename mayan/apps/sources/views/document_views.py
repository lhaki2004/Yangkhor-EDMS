import logging

from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.permissions import permission_document_create
from mayan.apps.views.mixins import ExternalObjectViewMixin

from ..forms import NewDocumentForm
from ..forms import DocumentSingleUploadForm
from ..icons import icon_document_create_multiple
from ..models import Source

from .base import UploadBaseView

__all__ = ('DocumentUploadInteractiveView',)
logger = logging.getLogger(name=__name__)


class DocumentUploadInteractiveView(ExternalObjectViewMixin, UploadBaseView):
    external_object_class = DocumentType
    external_object_permission = permission_document_create
    document_form = NewDocumentForm
    object_permission = permission_document_create
    view_icon = icon_document_create_multiple

    def forms_valid(self, forms):
        source_backend_instance = self.source.get_backend_instance()

        try:
            source_backend_instance.process_documents(
                document_type=self.external_object, forms=forms,
                request=self.request
            )
        except Exception as exception:
            message = _(
                'Error processing source document upload; '
                '%(exception)s'
            ) % {
                'exception': exception,
            }
            logger.critical(msg=message, exc_info=True)
            if self.request.is_ajax():
                return JsonResponse(
                    data={'error': force_text(s=message)}, status=500
                )
            else:
                messages.error(
                    message=message.replace('\n', ' '),
                    request=self.request
                )
                raise type(exception)(message)
        else:
            messages.success(
                message=_(
                    'New document queued for upload and will be '
                    'available shortly.'
                ), request=self.request
            )

        return HttpResponseRedirect(
            redirect_to='{}?{}'.format(
                reverse(
                    viewname=self.request.resolver_match.view_name,
                    kwargs=self.request.resolver_match.kwargs
                ), self.request.META['QUERY_STRING']
            ),
        )

    def get_active_tab_links(self):
        sources = AccessControlList.objects.restrict_queryset(
            permission=permission_document_create,
            queryset=Source.objects.interactive().filter(enabled=True),
            user=self.request.user
        )
        return [
            UploadBaseView.get_tab_link_for_source(source=source)
            for source in sources
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'document_type': self.external_object,
                'title': _(
                    'Upload a document of type "%(document_type)s" from '
                    'source: %(source)s'
                ) % {
                    'document_type': self.external_object,
                    'source': self.source.label
                }
            }
        )

        return context

    def get_form_extra_kwargs__document_form(self):
        return {
            'document_type': self.external_object
        }

    def get_form_extra_kwargs__source_form(self):
        return {
            'source': self.source
        }

    def get_pk_url_kwargs(self):
        return {
            'pk': self.request.GET.get(
                'document_type_id', self.request.POST.get('document_type_id')
            )
        }


class DocumentCreateSinglePageView(FormView):
    template_name = 'appearance/document_single_upload.html'
    form_class = DocumentSingleUploadForm
    success_url = reverse_lazy('documents:document_list')

    def form_valid(self, form):
        # Here you would implement the logic to create the document, assign tags/cabinets, and save the file.
        # For now, just print cleaned_data for demonstration.
        print(form.cleaned_data)
        # TODO: Implement actual document creation logic.
        return super().form_valid(form)
