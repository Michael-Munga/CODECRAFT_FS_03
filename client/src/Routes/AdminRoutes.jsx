import React from "react";
import AdminDashboard from "@/Pages/AdminDashboard";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route path="/" element={<AdminDashboard />} />
    </Routes>
  );
}
