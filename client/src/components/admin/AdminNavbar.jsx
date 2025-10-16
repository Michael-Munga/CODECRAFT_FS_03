import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut } from "lucide-react";
import { UserContext } from "@/context/UserContext";

export default function AdminNavbar({ name = "John Doe" }) {
  const navigate = useNavigate();
  const { setUser } = useContext(UserContext);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    setUser(null);

    navigate("/");
  };

  return (
    <nav
      className="flex items-center justify-between h-20 px-8 
                    bg-gradient-to-r from-[#d8c3a5] to-[#eae7dc]
                    text-[#3b3b3b] shadow-md border-b border-[#b9a47a]"
    >
      {/* Dashboard title */}
      <h1 className="text-2xl font-serif tracking-wide">Admin Dashboard</h1>

      {/* User info & Logout */}
      <div className="flex items-center gap-4">
        <span className="text-sm text-[#5a4634]">
          Logged in as <span className="font-medium">{name}</span>
        </span>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 bg-[#b2967d] hover:bg-[#a6846a]
                     text-white transition px-3 py-2 rounded-xl text-sm font-medium shadow-sm"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>
    </nav>
  );
}
