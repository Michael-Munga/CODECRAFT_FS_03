import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "@/components/project-components/Navbar";
import Footer from "@/components/project-components/Footer";

export default function CustomerLayout() {
  return (
    <div className="min-h-screen w-full">
      <Navbar />
      <main className="flex-1 w-full">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
