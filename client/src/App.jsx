import React from "react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { SideBar } from "./components/project-components/Sidebar";
import Navbar from "./components/project-components/Navbar";
import Approutes from "./Routes/Approutes";
import Footer from "./components/project-components/Footer";

import { CartProvider } from "@/context/CartContext";
import { UserProvider } from "./context/UserContext";
import { Toaster } from "sonner";

export default function App() {
  return (
    <UserProvider>
      <CartProvider>
        <SidebarProvider>
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

          <Toaster position="top-center" richColors />
        </SidebarProvider>
      </CartProvider>
    </UserProvider>
  );
}
