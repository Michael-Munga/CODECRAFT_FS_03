import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Users, Clock, CheckCircle, ShoppingBag, Building } from "lucide-react";

const StatItem = ({
  value,
  label,
  icon,
  color = "from-amber-700 to-rose-600",
}) => {
  return (
    <div
      className={cn(
        "group border-stone-300/30 bg-stone-50 relative overflow-hidden rounded-xl border p-6 shadow-md",
        "dark:bg-stone-900 dark:border-stone-700"
      )}
    >
      <div
        className={cn(
          "absolute -top-6 -right-6 h-24 w-24 rounded-full bg-gradient-to-br opacity-20 blur-2xl",
          color
        )}
      />

      <div className="flex items-center gap-4">
        <div
          className={cn(
            "flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br text-white",
            color
          )}
        >
          {icon}
        </div>

        <div className="flex flex-col">
          <h3 className="flex items-baseline text-3xl font-bold tracking-tight text-amber-900 smokum">
            {value}
          </h3>
          <p className="text-stone-600 text-sm font-medium">{label}</p>
        </div>
      </div>
    </div>
  );
};

export default function AboutPage() {
  const stats = [
    {
      value: "500+",
      label: "Happy Local Customers",
      icon: <Users className="h-5 w-5" />,
      color: "from-amber-600 to-yellow-500",
    },
    {
      value: "2020",
      label: "Year We Started",
      icon: <Clock className="h-5 w-5" />,
      color: "from-blue-500 to-cyan-500",
    },
    {
      value: "100+",
      label: "Unique Vintage Pieces",
      icon: <CheckCircle className="h-5 w-5" />,
      color: "from-green-500 to-emerald-500",
    },
    
  ];

  return (
    <section className="relative w-full overflow-hidden py-16 md:py-24">
      <div className="relative z-10 container mx-auto max-w-5xl px-4 md:px-6">
        {/* Header Section */}
        <div className="mx-auto mb-12 max-w-2xl text-center">
          <Badge
            variant="outline"
            className="border-amber-600/20 bg-amber-50 rounded-full px-4 py-1 text-sm font-medium text-amber-700"
          >
            About Us
          </Badge>

          <h1 className="bg-gradient-to-b from-amber-800 to-amber-600 bg-clip-text text-4xl font-bold tracking-tight text-transparent sm:text-5xl smokum mt-4">
            Our Vintage Story
          </h1>

          <p className="mt-4 text-lg text-stone-600 oswald">
            A Classic Vintage shop with a big love for timeless fashion, opened in
            2020.
          </p>
        </div>

        {/* Stats Section */}
        <div className="mb-16">
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {stats.map((stat, index) => (
              <StatItem
                key={index}
                value={stat.value}
                label={stat.label}
                icon={stat.icon}
                color={stat.color}
              />
            ))}
          </div>
        </div>

        {/* About Content */}
        <div className="grid gap-12 md:grid-cols-2">
          <div className="space-y-6">
            <div className="from-amber-700 to-rose-500 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br text-white shadow-lg">
              <ShoppingBag className="h-6 w-6" />
            </div>

            <h2 className="text-2xl font-bold tracking-tight text-amber-900 smokum">
              Our Mission
            </h2>

            <p className="text-stone-600 text-base leading-relaxed">
              We started this shop in 2020 with one goal: to bring affordable,
              authentic vintage fashion to our community. Every item we source
              is handpicked, with care and love for timeless style.
            </p>
          </div>

          <div className="space-y-6">
            <div className="from-blue-500 to-cyan-500 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-gradient-to-br text-white shadow-lg">
              <Building className="h-6 w-6" />
            </div>

            <h2 className="text-2xl font-bold tracking-tight text-amber-900 smokum">
              Our Roots
            </h2>

            <p className="text-stone-600 text-base leading-relaxed">
              What began as a small corner shop has grown into a welcoming place
              where vintage lovers gather, share stories, and find unique
              treasures that bring back memories and create new ones.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
