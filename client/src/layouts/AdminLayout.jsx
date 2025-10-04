import React from "react";
import AdminNavbar from "@/components/admin/AdminNavbar";
import Footer from "@/components/project-components/Footer";
import AdminRoutes from "@/Routes/AdminRoutes";
export default function AdminLayout() {
  return (
    <>
      <div className=" min-h-screen w-full">
        <AdminNavbar />
        <main className="flex-1 w-full">
          <AdminRoutes />
        </main>
        <Footer />
      </div>
    </>
  );
}
