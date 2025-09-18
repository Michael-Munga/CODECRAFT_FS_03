import { useId } from "react";
import { SearchIcon, ShoppingCart, User } from "lucide-react";
import { Link } from "react-router-dom";

import { Input } from "@/components/ui/input";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuContent,
} from "@/components/ui/navigation-menu";

// Navigation links array
const navigationLinks = [
  { to: "/", label: "Home", active: true },
  { to: "/products", label: "Shop" },
  { to: "/new-arrivals", label: "New Arrivals" },
  { to: "/about", label: "About Us" },
  { to: "/contact", label: "Contact" },
];

export default function Navbar() {
  const id = useId();

  return (
    <header className="sticky top-0 z-50 border-b border-stone-300 bg-gradient-to-r from-amber-700 via-rose-700 to-stone-800 text-white shadow-md">
      {/* Top row-->brand and search */}
      <div className="flex h-16 items-center justify-between gap-4 px-4 md:px-8">
        {/* Brand */}
        <div className="flex flex-1 items-center">
          <Link
            to="/"
            className="text-2xl font-serif font-bold tracking-wide text-white hover:text-amber-200 transition-colors"
          >
            Vintage Closet
          </Link>
        </div>

        {/* Search */}
        <div className="grow max-w-lg">
          <div className="relative w-full">
            <Input
              id={id}
              className="peer h-9 rounded-lg border-stone-400 bg-stone-100/90 ps-9 pe-10 text-stone-800 placeholder-stone-500 focus:border-amber-500 focus:ring-2 focus:ring-amber-500"
              placeholder="Search vintage gems..."
              type="search"
            />
            <div className="absolute inset-y-0 start-0 flex items-center ps-2 text-stone-500">
              <SearchIcon size={18} />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom navigation */}
      <div className="border-t border-stone-400 bg-stone-50/70 backdrop-blur-sm py-2 px-4 md:px-8">
        <div className="flex items-center justify-between">
          {/* Navigation menu */}
          <NavigationMenu>
            <NavigationMenuList className="gap-4">
              {navigationLinks.map((link, label) => (
                <NavigationMenuItem key={label}>
                  <NavigationMenuLink
                    active={link.active}
                    asChild
                    className={`px-3 py-1.5 font-medium text-stone-700 transition-colors ${
                      link.active
                        ? "text-amber-700 border-b-2 border-amber-700"
                        : "hover:text-rose-700"
                    }`}
                  >
                    <Link to={link.to}>{link.label}</Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>
              ))}
            </NavigationMenuList>
          </NavigationMenu>

          {/* Right side--> account + cart */}
          <div className="flex items-center gap-6">
            {/* My Account */}
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger className="flex items-center gap-1 text-sm font-medium text-stone-700 hover:text-amber-700 transition-colors">
                    <User size={18} />
                    <span>My Account</span>
                  </NavigationMenuTrigger>
                  <NavigationMenuContent className="z-50 w-40 rounded-lg bg-white shadow-lg ring-1 ring-stone-300 p-3">
                    <NavigationMenuLink asChild>
                      <Link
                        to="/login"
                        className="block w-full rounded-lg bg-amber-500 px-4 py-2 text-center text-sm font-medium text-stone-900 shadow hover:bg-amber-600 transition"
                      >
                        Login
                      </Link>
                    </NavigationMenuLink>
                  </NavigationMenuContent>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>

            {/* Cart */}
            <button className="relative flex items-center gap-1 text-sm font-medium text-stone-700 hover:text-amber-700 transition-colors">
              <ShoppingCart size={18} />
              <span>Cart</span>
              <span className="absolute -top-1 -right-2 h-4 w-4 rounded-full bg-amber-600 text-[10px] font-bold text-white flex items-center justify-center">
                2
              </span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
