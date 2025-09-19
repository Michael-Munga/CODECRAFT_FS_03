import LoginForm from "@/components/project-components/LoginForm";
import React from "react";

export default function LoginPage() {
  return (
    <div className="min-h-screen px-4 py-8">
      <div className="text-center mb-6">
        <h1 className="text-6xl font-bold text-amber-900 vint">
          Your Fashion Journey continues here
        </h1>
        <h2 className="text-3xl font-bold text-rose-950 creek mt-4">
          Sign In Below To Access Your Account
        </h2>
      </div>

      {/* Login Form */}
      <div className="w-full max-w-3xl mx-auto">
        <LoginForm />
      </div>
    </div>
  );
}
