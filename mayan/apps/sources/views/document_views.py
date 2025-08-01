import logging
import requests
import tempfile
import os
from datetime import datetime, timedelta

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
            # Process documents normally
            result = source_backend_instance.process_documents(
                document_type=self.external_object, forms=forms,
                request=self.request
            )
            
            # Get the uploaded documents - they might not be returned directly
            # So we'll get them from the database
            from mayan.apps.documents.models import Document
            recent_documents = Document.objects.filter(
                document_type=self.external_object,
                datetime_created__gte=datetime.now() - timedelta(minutes=5)
            ).order_by('-datetime_created')
            
            logger.info(f"Found {recent_documents.count()} recent documents for auto-tagging")
            
            # Auto-tag the uploaded documents synchronously
            if recent_documents.exists():
                logger.info(f"Found {recent_documents.count()} documents to auto-tag")
                for doc in recent_documents:
                    logger.info(f"Document: {doc.label} (ID: {doc.pk})")
                
                auto_tagged_count = self.auto_tag_documents_sync(recent_documents)
                logger.info(f"Auto-tagging returned count: {auto_tagged_count}")
                
                if auto_tagged_count > 0:
                    messages.success(
                        message=_(
                            f'Document uploaded successfully. Auto-tagged {auto_tagged_count} document(s).'
                        ), request=self.request
                    )
                else:
                    messages.success(
                        message=_(
                            'Document uploaded successfully. No tags were auto-detected.'
                        ), request=self.request
                    )
            else:
                logger.warning("No recent documents found for auto-tagging")
                messages.success(
                    message=_(
                        'Document uploaded successfully.'
                    ), request=self.request
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

        return HttpResponseRedirect(
            redirect_to='{}?{}'.format(
                reverse(
                    viewname=self.request.resolver_match.view_name,
                    kwargs=self.request.resolver_match.kwargs
                ), self.request.META['QUERY_STRING']
            ),
        )

    def auto_tag_documents_sync(self, documents):
        """
        Synchronously auto-tag uploaded documents using the Auto-Tag microservice
        """
        auto_tagged_count = 0
        
        try:
            from django.conf import settings
            from mayan.apps.tags.models import Tag
            
            # Check if auto-tagging is enabled
            auto_tag_enabled = getattr(settings, 'AUTO_TAG_ENABLED', True)
            logger.info(f"Auto-tagging enabled: {auto_tag_enabled}")
            
            if not auto_tag_enabled:
                logger.debug("Auto-tagging is disabled, skipping")
                return auto_tagged_count
            
            logger.info(f"Starting auto-tagging for {documents.count()} documents")
            
            for document in documents:
                logger.info(f"Processing document: {document.label} (ID: {document.pk})")
                
                # Get the latest file of the document
                document_file = document.file_latest
                if not document_file:
                    logger.warning(f"No file found for document {document.pk}")
                    continue
                
                logger.info(f"Found file: {document_file.filename}")
                
                # Call Auto-Tag API synchronously
                suggested_tags = self.call_auto_tag_api_sync(document_file)
                
                logger.info(f"API returned tags: {suggested_tags}")
                
                # Create and attach tags
                if suggested_tags:
                    attached_count = self.attach_suggested_tags_sync(document, suggested_tags)
                    if attached_count > 0:
                        auto_tagged_count += 1
                        logger.info(f"Auto-tagged document {document.pk} with {attached_count} tags: {suggested_tags}")
                    else:
                        logger.warning(f"Failed to attach tags to document {document.pk}")
                else:
                    logger.info(f"No tags detected for document {document.pk}")
                    
        except Exception as e:
            logger.error(f"Auto-tag process failed: {e}", exc_info=True)
            # Don't fail the upload, just log the error
        
        logger.info(f"Auto-tagging completed. Tagged {auto_tagged_count} documents")
        return auto_tagged_count

    def call_auto_tag_api_sync(self, document_file):
        """
        Synchronously call the Auto-Tag microservice API
        """
        try:
            from django.conf import settings
            
            # Get settings
            api_url = getattr(settings, 'AUTO_TAG_API_URL', 'http://localhost:8080/predict')
            timeout = getattr(settings, 'AUTO_TAG_TIMEOUT', 30)
            
            logger.info(f"Calling Auto-Tag API: {api_url}")
            
            # Create a temporary file for the API call
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                # Write document file content to temp file
                file_size = 0
                for chunk in document_file.open().chunks():
                    tmp_file.write(chunk)
                    file_size += len(chunk)
                tmp_file.flush()
                
                logger.info(f"Prepared file for API: {document_file.filename} ({file_size} bytes)")
                
                # Prepare file for API call
                with open(tmp_file.name, 'rb') as file_obj:
                    files = {'files': (document_file.filename, file_obj, 'application/octet-stream')}
                    
                    # Call Auto-Tag API synchronously
                    logger.info(f"Sending request to Auto-Tag API...")
                    response = requests.post(
                        api_url,
                        files=files,
                        timeout=timeout
                    )
                    
                    logger.info(f"API response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        results = response.json()
                        logger.info(f"API response: {results}")
                        
                        suggested_tags = []
                        logger.info(f"Processing {len(results)} API results")
                        for result in results:
                            logger.info(f"Processing result: {result}")
                            if 'predicted_tag' in result and result['predicted_tag']:
                                suggested_tags.append(result['predicted_tag'])
                                logger.info(f"Added tag: {result['predicted_tag']}")
                            elif 'error' in result:
                                logger.warning(f"API error: {result['error']}")
                        
                        logger.info(f"Final extracted tags: {suggested_tags}")
                        return suggested_tags
                    else:
                        logger.error(f"Auto-tag API returned status {response.status_code}: {response.text}")
                        
        except Exception as e:
            logger.error(f"Auto-tag API call failed: {e}", exc_info=True)
        
        return []

    def attach_suggested_tags_sync(self, document, suggested_tags):
        """
        Synchronously create tags and attach them to the document
        """
        try:
            from mayan.apps.tags.models import Tag
            
            logger.info(f"Attaching {len(suggested_tags)} tags to document {document.pk}")
            logger.info(f"Document label: {document.label}")
            logger.info(f"Tags to attach: {suggested_tags}")
            
            attached_count = 0
            for tag_name in suggested_tags:
                if tag_name and tag_name.strip():
                    logger.info(f"Processing tag: '{tag_name}'")
                    
                    # Create tag if it doesn't exist
                    tag, created = Tag.objects.get_or_create(
                        label=tag_name.strip(),
                        defaults={'color': '#000000'}  # Default color
                    )
                    
                    logger.info(f"Tag object: {tag} (created: {created})")
                    
                    # Attach to document
                    try:
                        tag.attach_to(document=document)
                        attached_count += 1
                        logger.info(f"Successfully attached tag '{tag_name}' to document {document.pk}")
                    except Exception as attach_error:
                        logger.error(f"Failed to attach tag '{tag_name}' to document {document.pk}: {attach_error}")
                    
                    if created:
                        logger.info(f"Created new tag: {tag_name}")
                    else:
                        logger.info(f"Used existing tag: {tag_name}")
                else:
                    logger.warning(f"Skipping empty tag name: '{tag_name}'")
            
            logger.info(f"Successfully attached {attached_count} tags to document {document.pk}")
            return attached_count
                    
        except Exception as e:
            logger.error(f"Failed to attach tags to document {document.pk}: {e}", exc_info=True)
            return 0

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
