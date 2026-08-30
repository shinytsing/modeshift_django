"""Persisted requirement documents and their retrievable RAG chunks."""

from django.contrib.auth.models import User
from django.db import models


class RequirementDocument(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requirement_documents", null=True, blank=True)
    title = models.CharField(max_length=255)
    source_file = models.FileField(upload_to="rag_requirements/%Y/%m/%d/")
    source_type = models.CharField(max_length=10)
    extracted_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["owner", "created_at"])]

    def __str__(self):
        return self.title


class RequirementChunk(models.Model):
    document = models.ForeignKey(RequirementDocument, on_delete=models.CASCADE, related_name="chunks")
    sequence = models.PositiveIntegerField()
    content = models.TextField()
    vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["document_id", "sequence"]
        constraints = [models.UniqueConstraint(fields=["document", "sequence"], name="unique_requirement_chunk")]
        indexes = [models.Index(fields=["document", "sequence"])]

    def __str__(self):
        return f"{self.document.title}#{self.sequence}"
