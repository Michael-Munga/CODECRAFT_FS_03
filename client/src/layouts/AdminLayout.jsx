import React from "react";
import { Outlet } from "react-router-dom";
import AdminNavbar from "@/components/admin/AdminNavbar";
import Footer from "@/components/project-components/Footer";

export default function AdminLayout() {
  return (
    <div className="min-h-screen w-full">
      <AdminNavbar />
      <main className="flex-1 w-full">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
