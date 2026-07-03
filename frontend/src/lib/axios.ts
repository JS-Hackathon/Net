import axios from "axios";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

// Configure progress bar
NProgress.configure({ showSpinner: false, speed: 400 });

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor
api.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      NProgress.start();
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    if (typeof window !== "undefined") {
      NProgress.done();
    }
    return Promise.reject(error);
  }
);

// Response Interceptor
api.interceptors.response.use(
  (response) => {
    if (typeof window !== "undefined") {
      NProgress.done();
    }
    return response;
  },
  (error) => {
    if (typeof window !== "undefined") {
      NProgress.done();
    }
    return Promise.reject(error);
  }
);

export default api;
