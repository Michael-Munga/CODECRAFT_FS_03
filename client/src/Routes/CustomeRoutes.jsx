import React from "react";
import { Route, Routes } from "react-router-dom";
import LoginPage from "@/Pages/customer/LoginPage";
import SignUpPage from "@/Pages/customer/SignUpPage";
import HomePage from "@/Pages/customer/HomePage";
import ProductsPage from "@/Pages/customer/ProductsPage";
import CartPage from "@/Pages/customer/CartPage";
import AboutPage from "@/Pages/customer/AboutPage";
import ContactPage from "@/Pages/customer/ContactPage";

export default function CustomerRoutes() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/products" element={<ProductsPage />} />
      <Route path="/cart" element={<CartPage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
    </Routes>
  );
}
