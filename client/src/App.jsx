import React from "react";
import { CartProvider } from "@/context/CartContext";
import { UserProvider } from "./context/UserContext";
import { Toaster } from "sonner";
import Layout from "./layouts/Layout";

export default function App() {
  return (
    <UserProvider>
      <CartProvider>
        <Layout />
        <Toaster position="top-center" richColors />
      </CartProvider>
    </UserProvider>
  );
}
