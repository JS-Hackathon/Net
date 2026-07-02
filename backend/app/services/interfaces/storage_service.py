from typing import Protocol

class StorageService(Protocol):
    async def upload_file(self, file_data: bytes, filename: str) -> str:
        """Upload a file to R2 or local storage.

        Args:
            file_data (bytes): Raw file bytes.
            filename (str): Name of the file.

        Returns:
            str: URL or file path pointing to the stored file.
        """
        ...

    async def download_file(self, filename: str) -> bytes:
        """Download file bytes.

        Args:
            filename (str): Name of the file.

        Returns:
            bytes: Raw file bytes.
        """
        ...

    async def delete_file(self, filename: str) -> bool:
        """Delete a file.

        Args:
            filename (str): Name of the file.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        ...
