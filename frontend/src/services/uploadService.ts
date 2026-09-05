import { uploadApi } from "../api/uploadApi";
import { type UploadPayload } from "../types/upload";

export const uploadService = {
      async upload(
            payload: UploadPayload,
            onProgress?: (progress: number) => void
      ) {
            const formData = new FormData();
            const fallbackTitle = payload.file.name.replace(/\.[^/.]+$/, "") || payload.file.name;
            formData.append("title", payload.title.trim() || fallbackTitle);

            if(payload.type === "image") {
                  formData.append("image", payload.file);

                  return uploadApi.uploadImage(formData, onProgress);
            }

            formData.append("file", payload.file);

            return uploadApi.uploadFile(formData, onProgress);
      },
};



