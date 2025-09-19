import React, { useState } from "react";
import { Mail, Phone, MapPin, Send, Instagram, Facebook } from "lucide-react";
import { Link } from "react-router-dom";

export default function ContactPage() {
  const [state, setState] = useState({
    name: "",
    email: "",
    message: "",
    submitting: false,
    submitted: false,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    setState({ ...state, submitting: true });

 
    console.log("Form submitted:", {
      name: state.name,
      email: state.email,
      message: state.message,
    });

    setState({
      ...state,
      submitting: false,
      submitted: true,
    });
  };

  return (
    <section className="w-full max-w-5xl mx-auto px-4 py-16">
      {/* Header */}
      <h2 className="text-center text-4xl font-bold smokum text-amber-900 mb-4">
        Get in Touch
      </h2>
      <p className="text-center text-stone-600 oswald mb-10">
        We’d love to hear from you! Whether it’s a question, feedback, or just a
        hello.
      </p>

      <div className="grid md:grid-cols-2 gap-10 bg-stone-50 border border-stone-200 rounded-xl shadow-lg p-8">
        {/* Contact Form */}
        <form className="space-y-6" onSubmit={handleSubmit}>
          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-stone-700"
            >
              Name
            </label>
            <input
              id="name"
              type="text"
              required
              placeholder="Enter your name"
              className="w-full mt-1 px-3 py-2 border border-stone-300 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
              value={state.name}
              onChange={(e) => setState({ ...state, name: e.target.value })}
            />
          </div>

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-stone-700"
            >
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              placeholder="Enter your email"
              className="w-full mt-1 px-3 py-2 border border-stone-300 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500"
              value={state.email}
              onChange={(e) => setState({ ...state, email: e.target.value })}
            />
          </div>

          <div>
            <label
              htmlFor="message"
              className="block text-sm font-medium text-stone-700"
            >
              Message
            </label>
            <textarea
              id="message"
              required
              placeholder="Write your message..."
              className="w-full mt-1 px-3 py-2 border border-stone-300 rounded-lg shadow-sm focus:ring-amber-500 focus:border-amber-500 min-h-[120px]"
              value={state.message}
              onChange={(e) => setState({ ...state, message: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={state.submitting}
            className="w-full bg-amber-700 text-white font-medium py-2 rounded-lg shadow-md hover:bg-amber-800 transition"
          >
            {state.submitting ? "Sending..." : "Send Message"}
            <Send className="inline ml-2 h-4 w-4" />
          </button>
        </form>

        {/* Contact Info */}
        <div className="space-y-8">
          <div className="flex items-start gap-4">
            <Mail className="h-6 w-6 text-amber-700" />
            <div>
              <p className="font-semibold text-stone-800">Email</p>
              <p className="text-stone-600">support@vintagecloset.com</p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <Phone className="h-6 w-6 text-amber-700" />
            <div>
              <p className="font-semibold text-stone-800">Phone</p>
              <p className="text-stone-600">+254 103823251</p>
            </div>
          </div>

          <div className="flex items-start gap-4">
            <MapPin className="h-6 w-6 text-amber-700" />
            <div>
              <p className="font-semibold text-stone-800">Location</p>
              <p className="text-stone-600">Pwani Lane, Fashion City</p>
            </div>
          </div>

          <div className="flex space-x-6">
            <Link to="#" className="text-stone-600 hover:text-amber-700">
              <Instagram className="h-6 w-6" />
            </Link>
            <Link to="#" className="text-stone-600 hover:text-amber-700">
              <Facebook className="h-6 w-6" />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
