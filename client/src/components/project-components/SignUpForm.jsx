import { useState } from "react";
import { Mail, Lock, Eye, EyeOff, Loader2, User, Phone } from "lucide-react";
import { Link } from "react-router-dom";

export default function SignUpForm() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      alert(`Welcome ${formData.firstName}! Your account has been created.`);
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center ">
      <div className="relative z-10 w-full max-w-5xl bg-white rounded-[32px] shadow-2xl overflow-hidden border border-stone-200">
        <div className="grid md:grid-cols-2">
          {/* Left */}
          <div className="hidden md:flex flex-col justify-center bg-gradient-to-b from-amber-700 via-rose-700 to-stone-800 p-12 text-white">
            <h1 className="mb-4 text-4xl creek leading-tight">
              The Vintage Closet
            </h1>
            <p className="opacity-90 text-3xl felipa">
              Step into timeless fashion. Sign up to access curated outfits,
              exclusive drops, and retro finds.
            </p>
          </div>

          {/* Right */}
          <div className="flex flex-col justify-center p-10">
            <div className="mx-auto w-full max-w-3xl">
              <div className="mb-8 text-center">
                <h2 className="text-3xl oswald  text-[#992b31] ">
                  Create Account
                </h2>
                <p className="mt-2 text-stone-600 felipa text-lg">
                  Join The Vintage Closet community
                </p>
              </div>

              <form
                onSubmit={handleSubmit}
                className="grid grid-cols-1 md:grid-cols-2 gap-6"
              >
                {/* First Name */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    First Name
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <User className="h-5 w-5" />
                    </span>
                    <input
                      type="text"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-3 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="First Name"
                    />
                  </div>
                </div>

                {/* Last Name */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    Last Name
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <User className="h-5 w-5" />
                    </span>
                    <input
                      type="text"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-3 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Last Name"
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    Email Address
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <Mail className="h-5 w-5" />
                    </span>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-3 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Email"
                    />
                  </div>
                </div>

                {/* Phone */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    Phone Number
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <Phone className="h-5 w-5" />
                    </span>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-3 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Phone Number"
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
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-12 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-stone-400 hover:text-stone-600"
                    >
                      {showPassword ? (
                        <Eye className="h-5 w-5" />
                      ) : (
                        <EyeOff className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Confirm Password */}
                <div>
                  <label className="mb-2 block text-sm font-medium text-stone-700">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-stone-400">
                      <Lock className="h-5 w-5" />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      required
                      className="block w-full rounded-lg border border-stone-300 bg-stone-50 py-3 pl-10 pr-12 text-sm text-stone-800 focus:border-amber-600 focus:ring-2 focus:ring-amber-600"
                      placeholder="Confirm Password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 flex items-center pr-3 text-stone-400 hover:text-stone-600"
                    >
                      {showPassword ? (
                        <Eye className="h-5 w-5" />
                      ) : (
                        <EyeOff className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <div className="md:col-span-2">
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
                        <span className="ml-2">Signing up...</span>
                      </>
                    ) : (
                      "Create Account"
                    )}
                  </button>
                </div>
              </form>

              <div className="mt-8 text-center text-sm text-stone-600 md:col-span-2">
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="font-medium text-amber-700 hover:underline"
                >
                  Back to Login
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
