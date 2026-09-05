import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const apiClient = axios.create({
      baseURL,
      headers: {
            "Content-Type": "application/json",
      },
});

apiClient.interceptors.request.use((config) => {
      if (config.data instanceof FormData) {
            const headers = config.headers;
            if (headers && typeof headers.delete === "function") {
                  headers.delete("Content-Type");
            } else if (headers) {
                  delete headers["Content-Type"];
            }
      }
      return config;
});


apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error: ", error);
    return Promise.reject(error);
  }
);

