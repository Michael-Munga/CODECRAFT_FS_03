import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// Layouts
import CustomerLayout from "@/layouts/CustomerLayout";
import AdminLayout from "@/layouts/AdminLayout";

// Customer pages
import HomePage from "@/Pages/customer/HomePage";
import LoginPage from "@/Pages/customer/LoginPage";
import SignUpPage from "@/Pages/customer/SignUpPage";
import ProductsPage from "@/Pages/customer/ProductsPage";
import CartPage from "@/Pages/customer/CartPage";
import AboutPage from "@/Pages/customer/AboutPage";
import ContactPage from "@/Pages/customer/ContactPage";

// Admin pages
import AdminDashboard from "@/Pages/admin/AdminDashboard";
import AdminProducts from "@/Pages/admin/AdminProducts";

// Auth route protection
import ProtectedRoute from "@/components/auth/ProtectedRoute";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Customer routes */}
      <Route element={<CustomerLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
      </Route>

      {/* Protected Admin routes */}
      <Route element={<ProtectedRoute role="admin" />}>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="/admin/dashboard" replace />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="products" element={<AdminProducts />} />
        </Route>
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
