from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class SupabaseDocumentStorage(S3Boto3Storage):
    """
    Storage privado sobre el bucket de Supabase (endpoint S3-compatible).
    Genera URLs firmadas (presigned) porque querystring_auth queda en True
    y el bucket del lado de Supabase se crea como privado.
    """
    bucket_name = settings.SUPABASE_STORAGE_BUCKET
    endpoint_url = settings.SUPABASE_S3_ENDPOINT_URL
    region_name = settings.SUPABASE_S3_REGION
    access_key = settings.SUPABASE_S3_ACCESS_KEY_ID
    secret_key = settings.SUPABASE_S3_SECRET_ACCESS_KEY
    querystring_auth = True
    querystring_expire = settings.SUPABASE_SIGNED_URL_EXPIRE
    file_overwrite = False
    default_acl = None
    addressing_style = "path"
    signature_version = "s3v4"
