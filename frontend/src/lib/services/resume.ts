import api from "@/lib/axios";

export interface Resume {
  id: string;
  filename: string;
  originalFilename: string;
  fileSize: number;
  fileType: string;
  uploadStatus: string;
  isPrimary: boolean;
  textExtractionStatus: string | null;
  createdAt: string;
  updatedAt: string;
}

const mapResume = (r: any): Resume => ({
  id: r.id,
  filename: r.filename,
  originalFilename: r.original_filename,
  fileSize: r.file_size,
  fileType: r.file_type,
  uploadStatus: r.upload_status,
  isPrimary: r.is_primary,
  textExtractionStatus: r.text_extraction_status,
  createdAt: r.created_at,
  updatedAt: r.updated_at,
});

export const resumeService = {
  async uploadResume(file: File): Promise<Resume> {
    const formData = new FormData();
    formData.append("file", file);
    const response = await api.post("/api/v1/resumes/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return mapResume(response.data.data);
  },

  async listResumes(): Promise<Resume[]> {
    const response = await api.get("/api/v1/resumes");
    const list = response.data.data.resumes || [];
    return list.map(mapResume);
  },

  async deleteResume(resumeId: string): Promise<void> {
    await api.delete(`/api/v1/resumes/${resumeId}`);
  },

  async setPrimaryResume(resumeId: string): Promise<Resume> {
    const response = await api.put(`/api/v1/resumes/${resumeId}/primary`);
    return mapResume(response.data.data);
  },

  async getDownloadUrl(resumeId: string): Promise<string> {
    const response = await api.get(`/api/v1/resumes/${resumeId}/download`);
    return response.data.data.download_url;
  },
};
