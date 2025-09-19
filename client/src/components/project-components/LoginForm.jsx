import { useState } from "react";
import { Mail, Lock, Eye, EyeOff, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";

export default function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      alert("Welcome back to The Vintage Closet!");
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="relative flex  items-center justify-center">
      <div className="relative z-10 w-full max-w-3xl bg-white rounded-[32px] shadow-2xl overflow-hidden border border-stone-200">
        <div className="grid md:grid-cols-2">
          {/* Left */}
          <div className="hidden md:flex flex-col justify-center bg-gradient-to-b from-amber-700 via-rose-700 to-stone-800 p-12 text-white">
            <h1 className="mb-4 text-4xl creek leading-tight">
              The Vintage Closet
            </h1>
            <p className="opacity-90 text-3xl felipa">
              Step into timeless fashion. Sign in to access curated outfits,
              exclusive drops, and retro finds.
            </p>
          </div>

          {/* Right */}
          <div className="flex flex-col justify-center p-10">
            <div className="mx-auto w-full max-w-md">
              <div className="mb-8 text-center">
                <h2 className="text-3xl   text-[#992b31]  creek">
                  Welcome Back
                </h2>
                <p className="mt-2 text-black text-lg felipa">
                  Your style journey continues here
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Email */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    Email address
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <Mail className="h-5 w-5" />
                    </span>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-3 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    Password
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <Lock className="h-5 w-5" />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-12 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-stone-400 hover:text-stone-600"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="
                    relative flex w-full items-center justify-center 
                    rounded-lg px-4 py-3 text-sm font-medium text-white
                    bg-gradient-to-r from-amber-700 via-rose-700 to-stone-800
                    hover:opacity-90 transition-all duration-300
                    shadow-lg
                  "
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span className="ml-2">Signing in...</span>
                    </>
                  ) : (
                    "Sign in to your account"
                  )}
                </button>
              </form>

              <div className="mt-8 text-center text-sm text-stone-600">
                Don’t have an account?{" "}
                <Link
                  to="/signup"
                  className="font-medium text-amber-700 hover:underline"
                >
                  Join The Vintage Closet
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
