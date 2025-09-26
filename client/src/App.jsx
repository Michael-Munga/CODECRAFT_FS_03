import React from "react";
import { SidebarProvider } from "./components/ui/sidebar";
import { CartProvider } from "@/context/CartContext";
import { UserProvider } from "./context/UserContext";
import { Toaster } from "sonner";
import Layout from "./layouts/Layout";

export default function App() {
  return (
    <UserProvider>
      <CartProvider>
        <SidebarProvider>
          <Layout />
          <Toaster position="top-center" richColors />
        </SidebarProvider>
      </CartProvider>
    </UserProvider>
  );
}
