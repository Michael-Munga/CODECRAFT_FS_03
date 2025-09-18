import React from "react";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center min-h-screen p-6">
      {/* Text content */}
      <div className="text-center">
        <h1 className="text-6xl font-bold text-amber-800 vint">
          Welcome to The Vintage Closet
        </h1>
        <h1 className="text-6xl font-bold text-amber-800 smokun">
          One Brand Unlimited Quality
        </h1>
        <p className="mt-2 text-3xl felipa">
          Step into timeless fashion and explore curated outfits, exclusive
          drops, and retro finds.
        </p>
      </div>

      <div className="mt-6 flex justify-center w-full">
        <div className="h-20 w-2/3 bg-gradient-to-r from-amber-700 via-rose-700 to-stone-800 rounded-4xl flex items-center justify-center">
          <h1 className="text-4xl rocker text-white">A Taste Of Quality</h1>
        </div>
      </div>
    </div>
  );
}
