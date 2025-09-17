import {
  Facebook,
  Instagram,
  Twitter,
  Mail,
  Phone,
  MapPin,
} from "lucide-react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="bg-gradient-to-r from-amber-700 via-rose-700 to-stone-800 text-stone-100 w-full ">
      <div className="mx-auto max-w-6xl px-6 py-10">
        {/* Top Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div>
            <h2 className="text-2xl font-serif font-bold">
              The Vintage Closet
            </h2>
            <p className="mt-3 text-sm opacity-80">
              Step into timeless fashion. Curated outfits, exclusive drops, and
              retro finds await you.
            </p>
          </div>

          {/* Quick Links */}
          <div className="flex flex-col">
            <h3 className="text-lg font-semibold">Quick Links</h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link to="/shop" className="hover:underline">
                  Shop
                </Link>
              </li>
              <li>
                <Link to="/arrivals" className="hover:underline">
                  New Arrivals
                </Link>
              </li>
              <li>
                <Link to="/collections" className="hover:underline">
                  Collections
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:underline">
                  Contact
                </Link>
              </li>

              <li>
                <Link to="/about" className="hover:underline">
                  About Us
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-lg font-semibold">Get in Touch</h3>
            <ul className="mt-3 space-y-3 text-sm">
              <li className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                <span>support@vintagecloset.com</span>
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-5 w-5" />
                <span>+254 103823251</span>
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                <span>Pwani Lane, Fashion City</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-10 border-t border-stone-200/30 pt-6 flex flex-col md:flex-row items-center justify-between text-sm">
          <p>
            &copy; {new Date().getFullYear()} The Vintage Closet. All rights
            reserved.
          </p>

          <div className="flex gap-5 mt-4 md:mt-0">
            <a href="#" className="hover:text-stone-200">
              <Facebook className="h-5 w-5" />
            </a>
            <a href="#" className="hover:text-stone-200">
              <Instagram className="h-5 w-5" />
            </a>
            <a href="#" className="hover:text-stone-200">
              <Twitter className="h-5 w-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
