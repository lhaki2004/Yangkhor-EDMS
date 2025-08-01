from django.core.management.base import BaseCommand
from django.conf import settings
from mayan.apps.documents.models import Document
from mayan.apps.tags.models import Tag
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test tag creation and attachment'

    def handle(self, *args, **options):
        self.stdout.write("Testing tag creation and attachment...")
        
        # Test 1: Create a tag
        tag_name = "Test Memo Tag"
        self.stdout.write(f"Creating tag: {tag_name}")
        
        try:
            tag, created = Tag.objects.get_or_create(
                label=tag_name,
                defaults={'color': '#000000'}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created new tag: {tag}"))
            else:
                self.stdout.write(f"Used existing tag: {tag}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create tag: {e}"))
            return
        
        # Test 2: Find a recent document
        from datetime import datetime, timedelta
        recent_documents = Document.objects.filter(
            datetime_created__gte=datetime.now() - timedelta(minutes=10)
        ).order_by('-datetime_created')
        
        if not recent_documents.exists():
            self.stdout.write(self.style.WARNING("No recent documents found"))
            return
            
        document = recent_documents.first()
        self.stdout.write(f"Found document: {document.label} (ID: {document.pk})")
        
        # Test 3: Attach tag to document
        try:
            tag.attach_to(document=document)
            self.stdout.write(self.style.SUCCESS(f"Successfully attached tag '{tag_name}' to document {document.pk}"))
            
            # Verify attachment
            document_tags = document.tags.all()
            self.stdout.write(f"Document now has {document_tags.count()} tags:")
            for doc_tag in document_tags:
                self.stdout.write(f"  - {doc_tag}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to attach tag: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc()) 