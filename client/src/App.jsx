import React from "react";
import { CartProvider } from "@/context/CartContext";
import { UserProvider } from "@/context/UserContext";
import { Toaster } from "sonner";
import AppRoutes from "@/Routes/AppRoutes";

export default function App() {
  return (
    <UserProvider>
      <CartProvider>
        <AppRoutes />
        <Toaster position="top-center" richColors />
      </CartProvider>
    </UserProvider>
  );
}
