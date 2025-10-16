import React, { useContext } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { UserContext } from "@/context/UserContext";

export default function ProtectedRoute({ role }) {
  const { user } = useContext(UserContext);
  const currentUser = user || JSON.parse(localStorage.getItem("user"));

  if (!currentUser) return <Navigate to="/login" replace />;

  if (role === "admin" && currentUser.role !== "admin")
    return <Navigate to="/" replace />;

  return <Outlet />;
}
