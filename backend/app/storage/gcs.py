from google.cloud import storage


class GCSStorageClient:
    def __init__(self) -> None:
        self._client = storage.Client()

    def download_gcs_uri_as_bytes(
            self,
            gcs_uri: str,
    ) -> bytes:
        bucket_name, blob_name = self._parse_gcs_uri(gcs_uri)

        bucket = self._client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        return blob.download_as_bytes()

    @staticmethod
    def _parse_gcs_uri(
            gcs_uri: str,
    ) -> tuple[str, str]:
        if not gcs_uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")

        path = gcs_uri.removeprefix("gs://")
        parts = path.split("/", 1)

        if len(parts) != 2:
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")

        bucket_name, blob_name = parts
        if not bucket_name or not blob_name:
            raise ValueError(f"Invalid GCS URI: {gcs_uri}")

        return bucket_name, blob_name
