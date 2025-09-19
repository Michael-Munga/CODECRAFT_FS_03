import React from "react";
import { Route, Routes } from "react-router-dom";
import LoginPage from "@/Pages/LoginPage";
import SignUpPage from "@/Pages/SignUpPage";
import HomePage from "@/Pages/HomePage";
import ProductsPage from "@/Pages/ProductsPage";
import CartPage from "@/Pages/CartPage";
import AboutPage from "@/Pages/AboutPage";

export default function Approutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/products" element={<ProductsPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/about" element={<AboutPage />} />
    </Routes>
  );
}
