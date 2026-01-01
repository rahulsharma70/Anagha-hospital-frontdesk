import { Button } from "@/components/ui/button";
import { Check, Star } from "lucide-react";
import { useNavigate } from "react-router-dom";

const plans = [
  {
    name: "Starter",
    description: "For 1 Doctor / 1 Hospital",
    installationPrice: 5000,
    monthlyPrice: 1000,
    features: [
      "1 Doctor profile",
      "1 Hospital",
      "Appointment management",
      "Email reminders",
      "Basic analytics",
      "Email support",
    ],
    popular: false,
    cta: "Get Started",
  },
  {
    name: "Professional",
    description: "For 5 Doctors in 1 Hospital",
    installationPrice: 10000,
    monthlyPrice: 2000,
    features: [
      "Up to 5 Doctor profiles",
      "1 Hospital",
      "SMS & Email reminders",
      "Advanced analytics",
      "Custom booking page",
      "Payment integration",
      "Priority support",
    ],
    popular: true,
    cta: "Get Started",
  },
  {
    name: "Enterprise",
    description: "For 10 Doctors & 5 Hospitals",
    installationPrice: 20000,
    monthlyPrice: 5000,
    features: [
      "Up to 10 Doctor profiles",
      "Up to 5 Hospitals (same ownership)",
      "Multi-location support",
      "Custom integrations",
      "Dedicated account manager",
      "24/7 phone support",
      "White-label option",
    ],
    popular: false,
    cta: "Contact Sales",
  },
];

const Pricing = () => {
  const navigate = useNavigate();

  const handlePlanClick = (plan: typeof plans[0]) => {
    // Navigate to hospital registration page with plan details
    const registrationUrl = `/register-hospital?plan=${encodeURIComponent(plan.name)}&amount=${plan.installationPrice}`;
    window.location.href = registrationUrl;
  };

  return (
    <section id="pricing" className="py-16 lg:py-24 relative">
      <div className="absolute inset-0 bg-gradient-subtle opacity-50" />
      
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="inline-block px-4 py-2 rounded-full bg-secondary text-secondary-foreground text-sm font-semibold mb-4">
            Pricing Plans
          </span>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-foreground mb-6">
            Simple, <span className="text-gradient">Transparent Pricing</span>
          </h2>
          <p className="text-lg text-muted-foreground">
            Choose the perfect plan for your practice. All plans include core features with no hidden fees.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative bg-card rounded-2xl p-6 lg:p-8 border transition-all duration-300 hover:-translate-y-1 ${
                plan.popular
                  ? "border-primary shadow-glow scale-105 lg:scale-110"
                  : "border-border/50 shadow-card hover:shadow-elevated"
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <div className="flex items-center gap-1 px-4 py-1.5 bg-gradient-hero rounded-full text-primary-foreground text-sm font-semibold shadow-soft">
                    <Star className="w-4 h-4" />
                    Most Popular
                  </div>
                </div>
              )}

              <div className="text-center mb-6 pt-2">
                <h3 className="text-xl font-bold text-foreground mb-2">{plan.name}</h3>
                <p className="text-muted-foreground text-sm">{plan.description}</p>
              </div>

              <div className="text-center mb-6 space-y-2">
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-3xl lg:text-4xl font-bold text-foreground">
                    ₹{plan.installationPrice.toLocaleString('en-IN')}
                  </span>
                  <span className="text-muted-foreground">/installation</span>
                </div>
                <div className="flex items-baseline justify-center gap-1">
                  <span className="text-xl font-semibold text-primary">
                    + ₹{plan.monthlyPrice.toLocaleString('en-IN')}
                  </span>
                  <span className="text-muted-foreground text-sm">/month maintenance</span>
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <span className="text-muted-foreground text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant={plan.popular ? "hero" : "outline"}
                className="w-full"
                size="lg"
                onClick={() => handlePlanClick(plan)}
                type="button"
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>

        <p className="text-center text-muted-foreground mt-8">
          All plans include setup assistance and dedicated support
        </p>
      </div>
    </section>
  );
};

export default Pricing;
