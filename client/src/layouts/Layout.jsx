import React from "react";
import Navbar from "@/components/project-components/Navbar";
import Approutes from "@/Routes/Approutes";
import Footer from "@/components/project-components/Footer";

export default function Layout() {
  return (
    <>
      <div className=" min-h-screen w-full">
        <Navbar />
        <main className="flex-1 w-full">
          <Approutes />
        </main>
        <Footer />
      </div>
    </>
  );
}
