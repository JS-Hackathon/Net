# Feature 2: Resume Upload

## Overview
Implement secure file upload system that allows users to upload resumes in PDF and DOCX formats, stores them in Cloudflare R2 storage, and provides file management capabilities with validation and progress tracking.

## Goal
Create a reliable, user-friendly resume upload system that serves as the foundation for AI-powered resume analysis while ensuring file security, validation, and optimal user experience.

## User Story
As a **Candidate**,
I want to upload my resume to MockAI
So that I can get AI-powered analysis and career recommendations.

As a **Candidate**,
I want to manage multiple resumes
So that I can track different versions and use specific resumes for different opportunities.

## Functional Requirements
### File Upload System
- Support PDF and DOCX file formats only
- Maximum file size limit of 5MB per upload
- Drag-and-drop interface with click-to-browse fallback
- Upload progress indicator with cancel capability
- Multiple file upload support (one at a time for MVP)
- File validation before and after upload
- Secure direct upload to Cloudflare R2 storage

### File Management
- List all uploaded resumes for authenticated user
- View file metadata (name, size, upload date, format)
- Download original uploaded files
- Delete unwanted resume files
- File versioning with timestamps
- Set primary/default resume designation

### File Processing
- Extract text content for AI analysis preparation
- Generate file thumbnails/previews (optional for MVP) 
- Virus scanning integration (future enhancement)
- File format conversion capabilities (future enhancement)
- Metadata extraction (creation date, author, etc.)

## Non-functional Requirements
- Upload performance: Support files up to 5MB with progress tracking
- Storage security: Files accessible only by file owner
- File integrity: Checksums to verify upload completion
- Concurrent uploads: Handle multiple users uploading simultaneously
- Browser compatibility: Support major browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsiveness: Functional on mobile devices

## Backend Tasks
### Database Schema
```sql
-- Resume files table
CREATE TABLE resumes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL, -- Cloudflare R2 path
    file_size INTEGER NOT NULL, -- bytes
    file_type VARCHAR(10) NOT NULL, -- 'pdf' or 'docx'
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(64), -- SHA-256 for integrity checking
    upload_status VARCHAR(20) DEFAULT 'uploading', -- uploading, completed, failed, processing
    is_primary BOOLEAN DEFAULT FALSE, -- user's primary resume
    extracted_text TEXT, -- cached extracted text
    text_extraction_status VARCHAR(20), -- pending, completed, failed
    metadata JSONB, -- file metadata (creation date, author, etc.)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_upload_status ON resumes(upload_status);
CREATE UNIQUE INDEX idx_resumes_primary ON resumes(user_id, is_primary) WHERE is_primary = TRUE;
```

### File Upload Service
```python
class ResumeUploadService:
    def __init__(self, r2_client: R2Client, text_extractor: TextExtractor):
        self.r2_client = r2_client
        self.text_extractor = text_extractor
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_types = {'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}
    
    async def validate_file(self, file: UploadFile) -> FileValidationResult:
        # Check file size
        # Validate MIME type
        # Basic file header validation
        # Return validation result
        
    async def upload_resume(self, user_id: UUID, file: UploadFile) -> ResumeUploadResult:
        # Validate file
        # Generate unique file path
        # Upload to Cloudflare R2
        # Calculate file hash
        # Save metadata to database
        # Trigger text extraction
        # Return upload result
        
    async def get_user_resumes(self, user_id: UUID) -> List[ResumeMetadata]:
        # Retrieve user's resumes from database
        # Include upload status and metadata
        
    async def delete_resume(self, user_id: UUID, resume_id: UUID) -> bool:
        # Verify ownership
        # Delete from R2 storage
        # Remove database record
        # Handle primary resume reassignment
        
    async def set_primary_resume(self, user_id: UUID, resume_id: UUID) -> bool:
        # Verify ownership
        # Update primary resume designation
        
    async def download_resume(self, user_id: UUID, resume_id: UUID) -> SignedURL:
        # Verify ownership
        # Generate signed URL for download
        # Log access for audit
```

### Cloudflare R2 Integration
```python
class R2StorageClient:
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str):
        self.client = boto3.client('s3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket = bucket
    
    async def upload_file(self, file_content: bytes, key: str, content_type: str) -> str:
        # Upload file to R2 with proper metadata
        # Return file URL/path
        
    async def delete_file(self, key: str) -> bool:
        # Delete file from R2 storage
        
    async def generate_signed_url(self, key: str, expiry: int = 3600) -> str:
        # Generate signed URL for secure access
        
    async def get_file_metadata(self, key: str) -> Dict[str, Any]:
        # Retrieve file metadata from R2
```

### Text Extraction Service
```python
class TextExtractionService:
    async def extract_text_from_pdf(self, file_content: bytes) -> ExtractedText:
        # Use PyPDF2 or similar to extract text
        # Handle different PDF structures
        # Return extracted text with metadata
        
    async def extract_text_from_docx(self, file_content: bytes) -> ExtractedText:
        # Use python-docx to extract text
        # Preserve formatting information
        # Handle tables and special elements
        
    async def extract_text(self, file_content: bytes, file_type: str) -> ExtractedText:
        # Route to appropriate extraction method
        # Handle extraction errors gracefully
        # Cache results for future use
```

## Frontend Tasks
### File Upload Component
```tsx
interface FileUploadProps {
  onUploadSuccess: (resume: ResumeMetadata) => void;
  onUploadError: (error: string) => void;
  maxFileSize?: number;
  acceptedTypes?: string[];
}

const ResumeUploadZone: React.FC<FileUploadProps> = ({
  onUploadSuccess,
  onUploadError,
  maxFileSize = 5 * 1024 * 1024,
  acceptedTypes = ['.pdf', '.docx']
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);
  
  // Drag and drop handlers
  // File validation
  // Upload progress tracking
  // Error handling and display
  // Success feedback
};
```

### Resume List Component
```tsx
interface ResumeListProps {
  resumes: ResumeMetadata[];
  onDelete: (resumeId: string) => void;
  onSetPrimary: (resumeId: string) => void;
  onDownload: (resumeId: string) => void;
}

const ResumeList: React.FC<ResumeListProps> = ({
  resumes,
  onDelete,
  onSetPrimary,
  onDownload
}) => {
  // Resume cards with metadata
  // Primary resume indicator
  // Action buttons (delete, download, set primary)
  // Upload status indicators
  // Empty state when no resumes
};
```

### Upload Progress Indicator
```tsx
interface UploadProgressProps {
  progress: number; // 0-100
  fileName: string;
  fileSize: number;
  onCancel: () => void;
}

const UploadProgress: React.FC<UploadProgressProps> = ({
  progress,
  fileName,
  fileSize,
  onCancel
}) => {
  // Progress bar with percentage
  // File information display
  // Cancel button
  // Speed and ETA indicators
  // Success/error states
};
```

### File Validation Hook
```typescript
interface FileValidationResult {
  isValid: boolean;
  errors: string[];
}

const useFileValidation = () => {
  const validateFile = useCallback((file: File): FileValidationResult => {
    const errors: string[] = [];
    
    // Check file size
    if (file.size > 5 * 1024 * 1024) {
      errors.push('File size must be less than 5MB');
    }
    
    // Check file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      errors.push('Only PDF and DOCX files are allowed');
    }
    
    // Check file name
    if (file.name.length > 255) {
      errors.push('File name is too long');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }, []);
  
  return { validateFile };
};
```

## AI Service Tasks
### Text Extraction Pipeline
```python
class AITextExtractor:
    async def schedule_extraction(self, resume_id: UUID) -> bool:
        # Queue text extraction job
        # Update status to 'processing'
        # Return scheduling success
        
    async def extract_and_store_text(self, resume_id: UUID) -> ExtractedTextResult:
        # Retrieve file from R2
        # Extract text based on file type
        # Clean and normalize text
        # Store extracted text in database
        # Update extraction status
        
    async def get_extracted_text(self, resume_id: UUID) -> str:
        # Retrieve cached extracted text
        # Trigger extraction if not available
        # Handle extraction failures
```

## API Endpoints
### File Upload Endpoints
```
POST /resumes/upload
Content-Type: multipart/form-data
Headers: Authorization: Bearer <token>
Body: file (PDF/DOCX)
Response: {
  success: true,
  data: {
    id: "uuid",
    filename: "resume.pdf",
    file_size: 1024000,
    upload_status: "completed",
    created_at: "2024-01-01T00:00:00Z"
  }
}

GET /resumes
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    resumes: [
      {
        id: "uuid",
        filename: "resume.pdf",
        original_filename: "My Resume 2024.pdf",
        file_size: 1024000,
        file_type: "pdf",
        upload_status: "completed",
        is_primary: true,
        created_at: "2024-01-01T00:00:00Z"
      }
    ],
    total: 1
  }
}

GET /resumes/{resume_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    id: "uuid",
    filename: "resume.pdf",
    file_size: 1024000,
    download_url: "https://signed-url...",
    metadata: {
      pages: 2,
      created_date: "2024-01-01"
    }
  }
}

DELETE /resumes/{resume_id}
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    message: "Resume deleted successfully"
  }
}

PUT /resumes/{resume_id}/primary
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    message: "Primary resume updated"
  }
}

GET /resumes/{resume_id}/download
Headers: Authorization: Bearer <token>
Response: {
  success: true,
  data: {
    download_url: "https://signed-url-expires-in-1h...",
    expires_at: "2024-01-01T01:00:00Z"
  }
}
```

## Business Rules
### File Upload Rules
- Only authenticated users can upload resumes
- Maximum 10 resumes per user account
- File size limit: 5MB per file
- Allowed formats: PDF, DOCX only
- File names must be under 255 characters
- Duplicate file names are allowed with automatic versioning
- Users can designate one resume as "primary" for quick access

### File Access Rules
- Users can only access their own uploaded files
- Signed URLs expire after 1 hour for security
- File downloads are logged for audit purposes
- Deleted files are permanently removed after 30 days (soft delete)
- Primary resume cannot be deleted without setting a new primary

### Storage Management
- Files are stored with UUID-based paths for security
- Original filenames preserved in metadata
- File integrity verified with checksums
- Automatic cleanup of failed uploads after 24 hours
- Backup strategy for critical user data

## Validation Rules
### File Validation
```typescript
const fileValidationSchema = z.object({
  file: z.custom<File>()
    .refine(file => file.size <= 5 * 1024 * 1024, 'File size must be less than 5MB')
    .refine(file => ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(file.type), 
            'Only PDF and DOCX files are allowed')
    .refine(file => file.name.length <= 255, 'Filename too long')
    .refine(file => !file.name.includes('../'), 'Invalid filename characters')
});
```

### Upload Request Validation
- File presence validation
- MIME type verification against file extension
- Content-type header validation
- Request size limits
- User authentication verification

## UI Components
### Upload Components
- **ResumeUploadZone**: Drag-and-drop upload area with file browser
- **UploadProgress**: Progress bar with cancel capability
- **FilePreview**: File information display before upload
- **UploadSuccess**: Success message with next steps
- **UploadError**: Error display with retry options

### File Management Components
- **ResumeList**: Grid/list view of uploaded resumes
- **ResumeCard**: Individual resume display with actions
- **PrimaryBadge**: Indicator for primary resume
- **FileActions**: Download, delete, set primary actions
- **EmptyState**: Message when no resumes uploaded

### Status Indicators
- **UploadStatus**: Visual indicator for upload progress
- **FileSize**: Human-readable file size display
- **FileType**: Icon and label for file format
- **UploadDate**: Formatted timestamp display

## User Flow
### Upload Flow
1. User navigates to resume upload page
2. Drags file onto upload zone or clicks to browse
3. File validation performed client-side
4. Upload progress displayed with cancel option
5. File uploaded to Cloudflare R2 with metadata stored
6. Success message shown with option to upload another
7. Text extraction triggered in background
8. User can manage uploaded resumes

### File Management Flow
1. User views list of uploaded resumes
2. Can see upload status, file size, upload date
3. Set one resume as primary for default use
4. Download original files when needed
5. Delete unwanted resumes with confirmation
6. Upload new versions as separate files

### Error Handling Flow
1. File validation errors shown immediately
2. Upload errors displayed with retry option
3. Network errors handled with automatic retry
4. Server errors shown with helpful messages
5. Partial uploads cleaned up automatically

## Error Handling
### Upload Error Scenarios
- File too large: "File size exceeds 5MB limit. Please choose a smaller file."
- Invalid format: "Only PDF and DOCX files are supported."
- Network failure: "Upload failed due to network error. Please try again."
- Storage full: "Storage limit reached. Please delete some files and try again."
- Duplicate name: "A file with this name already exists. Upload anyway?"

### File Access Errors
- File not found: "The requested file could not be found."
- Access denied: "You don't have permission to access this file."
- Download failed: "Download failed. Please try again or contact support."
- Expired link: "Download link has expired. Please generate a new one."

### Graceful Degradation
- Fallback to basic file input if drag-and-drop not supported
- Progress estimation if exact progress unavailable
- Retry mechanism for failed uploads
- Offline detection and queue uploads when connection restored

## Acceptance Criteria
### File Upload Requirements
- [ ] Users can upload PDF and DOCX files up to 5MB
- [ ] Drag-and-drop interface works across major browsers
- [ ] Upload progress is displayed with cancel capability
- [ ] File validation prevents invalid uploads
- [ ] Files are securely stored in Cloudflare R2
- [ ] Upload status is tracked and displayed to users

### File Management Requirements
- [ ] Users can view list of uploaded resumes with metadata
- [ ] Download functionality works with secure signed URLs
- [ ] Delete functionality removes files from storage and database
- [ ] Primary resume designation works correctly
- [ ] Only file owners can access their uploads

### Performance Requirements
- [ ] File uploads complete within reasonable time for 5MB files
- [ ] Text extraction completes within 30 seconds for typical resumes
- [ ] File list loads quickly even with many uploaded files
- [ ] Download links generate immediately when requested

### Security Requirements
- [ ] File access restricted to authenticated file owners
- [ ] Signed URLs expire appropriately for security
- [ ] File validation prevents malicious uploads
- [ ] User data isolated between accounts
- [ ] File integrity maintained through checksums

## Definition of Done
- [ ] Complete file upload system implemented and tested
- [ ] Cloudflare R2 integration working with proper security
- [ ] File validation comprehensive and user-friendly
- [ ] Text extraction pipeline functional for PDF and DOCX
- [ ] User interface responsive and accessible
- [ ] Error handling covers all failure scenarios
- [ ] Performance requirements met for file operations
- [ ] Security testing passed for file access control
- [ ] Database schema optimized with proper indexes
- [ ] API endpoints documented and tested

## Dependencies
### Depends On
- **Feature 1**: Authentication System (user context and access control)
- **Feature 0.1**: Project Infrastructure (Cloudflare R2 setup, database)
- **Feature 0.2**: Design System (upload components, progress indicators)

### Used By
- **Feature 3**: Resume Parsing (processes uploaded resume files)
- **Feature 4**: Candidate Profile (displays resume information)
- **Feature 11**: Career Snapshot (includes resume data in snapshots)

### Produces
- Uploaded resume files in secure cloud storage
- File metadata and access control system
- Text extraction capability for AI processing
- File management interface for users

### Consumes
- Cloudflare R2 storage service
- File validation and processing libraries
- User authentication tokens
- Text extraction libraries (PyPDF2, python-docx)

## Related Features
- **Feature 3**: Resume Parsing (uses uploaded files for AI analysis)
- **Feature 4**: Candidate Profile (integrates resume information)
- **Feature 1**: Authentication (provides user context for file ownership)

## Notes
### Development Priorities
1. Basic file upload with validation
2. Cloudflare R2 integration and security
3. Text extraction for AI pipeline
4. File management interface
5. Upload progress and error handling
6. Performance optimization and testing

### Security Considerations
- File content scanning for malware (future enhancement)
- Rate limiting on upload endpoints
- Secure file deletion with overwriting
- Access logging for compliance
- Regular security audits of file handling

### Performance Optimizations
- Chunked uploads for large files (future enhancement)
- Client-side file compression
- Parallel text extraction processing
- Caching of extracted text
- CDN integration for faster downloads