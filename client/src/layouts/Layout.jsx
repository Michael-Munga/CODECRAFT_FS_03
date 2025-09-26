import React from "react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { SideBar } from "@/components/project-components/Sidebar";
import Navbar from "@/components/project-components/Navbar";
import Approutes from "@/Routes/Approutes";
import Footer from "@/components/project-components/Footer";

export default function Layout() {
  return (
    <>
      {/* Sidebar */}
      <SideBar />

      {/* Main content area */}
      <div className="flex flex-col min-h-screen w-full">
        <Navbar />
        <main className="flex-1 w-full">
          <SidebarTrigger />
          <Approutes />
        </main>
        <Footer />
      </div>
    </>
  );
}
