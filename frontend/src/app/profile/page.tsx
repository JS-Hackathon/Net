"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/lib/store/authStore";
import api from "@/lib/axios";
import { toast } from "sonner";
import { 
  User as UserIcon, 
  Mail, 
  Shield, 
  CheckCircle2, 
  LogOut, 
  Edit3, 
  Save, 
  Camera, 
  Calendar, 
  Loader2,
  Home
} from "lucide-react";

export default function ProfilePage() {
  const router = useRouter();
  const { user, updateProfile, logout, checkAuth, isInitialized, isLoading } = useAuthStore();
  
  const [fullName, setFullName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [isEditing, setIsEditing] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Thiết lập các giá trị form khi user đã load xong
  useEffect(() => {
    if (user) {
      setFullName(user.fullName || "");
      setAvatarUrl(user.avatarUrl || "");
      setPreviewUrl(user.avatarUrl || "");
    } else if (isInitialized && !user) {
      // Nếu đã chạy kiểm tra đăng nhập nhưng không tìm thấy user, chuyển hướng về login
      router.push("/login");
    }
  }, [user, isInitialized, router]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      toast.error("Họ và tên không được để trống");
      return;
    }

    setIsUpdating(true);
    try {
      let finalAvatarUrl = avatarUrl;
      
      if (avatarFile) {
        const formData = new FormData();
        formData.append("file", avatarFile);
        
        const uploadRes = await api.post("/api/v1/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        
        if (uploadRes.data?.success) {
          finalAvatarUrl = uploadRes.data.data.url;
          setAvatarUrl(finalAvatarUrl);
        }
      }

      await updateProfile({ fullName, avatarUrl: finalAvatarUrl });
      toast.success("Cập nhật thông tin hồ sơ thành công!");
      setIsEditing(false);
      setAvatarFile(null);
    } catch (error: any) {
      const msg = error.response?.data?.message || "Cập nhật hồ sơ thất bại";
      toast.error(msg);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Đăng xuất thành công!");
      router.push("/login");
    } catch (e) {
      toast.error("Lỗi khi đăng xuất");
    }
  };

  // Hiển thị trạng thái tải ban đầu khi chưa khởi tạo xong
  if (!isInitialized || (isLoading && !user)) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-zinc-50 dark:bg-black font-sans">
        <Loader2 className="h-10 w-10 text-primary animate-spin" />
        <p className="mt-4 text-sm text-muted-foreground font-medium">Đang tải thông tin tài khoản...</p>
      </div>
    );
  }

  // Fallback an toàn nếu chưa kịp redirect
  if (!user) return null;

  // Lấy tên viết tắt hiển thị avatar mặc định
  const getInitials = (name: string) => {
    if (!name) return "U";
    return name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-foreground pb-12 select-none">
      {/* Header Bar */}
      <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold text-white text-md">
              M
            </div>
            <span className="font-bold tracking-wide">MockAI Candidate Portal</span>
          </Link>
          
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="flex items-center gap-2 py-2 px-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 hover:border-primary/30 transition duration-200"
            >
              <Home className="h-4 w-4" />
              Trang chủ
            </Link>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 py-2 px-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm font-semibold hover:text-red-500 hover:border-red-200 dark:hover:border-red-950 transition duration-200"
            >
              <LogOut className="h-4 w-4" />
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-5xl mx-auto px-6 mt-8 grid gap-8 md:grid-cols-12">
        {/* Cột Trái: Tổng quan tài khoản */}
        <div className="md:col-span-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm space-y-6 self-start">
          <div className="flex flex-col items-center text-center space-y-4">
            {/* Avatar container */}
            <div className="relative group">
              {previewUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={previewUrl}
                  alt={user.fullName}
                  className="h-24 w-24 rounded-full object-cover border-4 border-zinc-100 dark:border-zinc-800"
                />
              ) : (
                <div className="h-24 w-24 rounded-full bg-gradient-to-tr from-primary/20 to-secondary/20 border-4 border-zinc-100 dark:border-zinc-800 text-primary flex items-center justify-center font-bold text-2xl">
                  {getInitials(user.fullName)}
                </div>
              )}
              {isEditing && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity">
                  <Camera className="h-6 w-6 text-white" />
                </div>
              )}
            </div>

            <div className="space-y-1">
              <h3 className="text-xl font-bold">{user.fullName}</h3>
              <span className="inline-flex items-center gap-1 py-1 px-2.5 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider">
                <Shield className="h-3 w-3" />
                {user.role}
              </span>
            </div>
          </div>

          <div className="border-t border-zinc-100 dark:border-zinc-800 pt-6 space-y-4">
            <div className="flex items-center gap-3 text-sm">
              <Mail className="h-5 w-5 text-zinc-400" />
              <div className="space-y-0.5">
                <span className="text-xs text-muted-foreground block">Email</span>
                <span className="font-medium">{user.email}</span>
              </div>
            </div>
            
            <div className="flex items-center gap-3 text-sm">
              <CheckCircle2 className="h-5 w-5 text-success" />
              <div className="space-y-0.5">
                <span className="text-xs text-muted-foreground block">Xác thực Email</span>
                <span className="font-semibold text-success">Đã xác thực</span>
              </div>
            </div>
          </div>
        </div>

        {/* Cột Phải: Chỉnh sửa thông tin hồ sơ */}
        <div className="md:col-span-8 space-y-8">
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 sm:p-8 shadow-sm">
            <div className="flex items-center justify-between pb-6 border-b border-zinc-100 dark:border-zinc-800">
              <div className="space-y-1">
                <h2 className="text-2xl font-extrabold tracking-tight">Hồ sơ cá nhân</h2>
                <p className="text-sm text-muted-foreground">
                  Xem và cập nhật thông tin tài khoản ứng viên của bạn
                </p>
              </div>

              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-1.5 py-2 px-4 rounded-xl bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 font-semibold text-sm transition duration-200"
                >
                  <Edit3 className="h-4 w-4" />
                  Chỉnh sửa
                </button>
              )}
            </div>

            <form onSubmit={handleUpdate} className="pt-6 space-y-5">
              {/* Full Name */}
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                  Họ và tên
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  disabled={!isEditing || isUpdating}
                  className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/30 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 disabled:opacity-75 disabled:cursor-not-allowed transition duration-200"
                  required
                />
              </div>

              {/* Avatar Url */}
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                  Ảnh đại diện
                </label>
                <div className="flex items-center gap-4">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        setAvatarFile(file);
                        setPreviewUrl(URL.createObjectURL(file));
                      }
                    }}
                    disabled={!isEditing || isUpdating}
                    className="w-full text-sm text-zinc-500 dark:text-zinc-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Action buttons */}
              {isEditing && (
                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={isUpdating}
                    className="flex items-center gap-1.5 py-2.5 px-5 rounded-xl bg-primary text-white font-semibold hover:opacity-95 active:scale-[0.98] disabled:opacity-50 transition duration-200"
                  >
                    {isUpdating ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Lưu thay đổi
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setFullName(user.fullName || "");
                      setAvatarUrl(user.avatarUrl || "");
                      setPreviewUrl(user.avatarUrl || "");
                      setAvatarFile(null);
                      setIsEditing(false);
                    }}
                    disabled={isUpdating}
                    className="py-2.5 px-5 rounded-xl border border-zinc-200 dark:border-zinc-800 font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition duration-200"
                  >
                    Hủy
                  </button>
                </div>
              )}
            </form>
          </div>

          {/* Block: System Integration / Dashboard Status */}
          <div className="bg-gradient-to-r from-primary/10 via-tertiary/10 to-secondary/10 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="space-y-1 text-center sm:text-left">
              <h4 className="font-extrabold text-lg">Bạn đã sẵn sàng phỏng vấn?</h4>
              <p className="text-xs text-muted-foreground leading-normal max-w-md">
                Tài khoản của bạn đã được cấu hình với vai trò ứng viên (candidate). Bạn có quyền truy cập toàn bộ ngân hàng câu hỏi và bắt đầu các bài luyện tập với AI.
              </p>
            </div>
            <button
              onClick={() => {
                toast.info("Tính năng Mock Interview với AI đang chuẩn bị mở ở Phase sau!");
              }}
              className="py-3 px-6 rounded-xl bg-zinc-950 text-white font-semibold dark:bg-white dark:text-zinc-950 hover:opacity-90 active:scale-[0.98] transition duration-200 whitespace-nowrap text-sm shadow-md"
            >
              Luyện phỏng vấn ngay
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
