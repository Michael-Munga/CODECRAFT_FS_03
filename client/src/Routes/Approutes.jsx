import React from "react";
import { Route, Routes } from "react-router-dom";
import LoginPage from "@/Pages/LoginPage";
import SignUpPage from "@/Pages/SignUpPage";

export default function Approutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />
    </Routes>
  );
}
