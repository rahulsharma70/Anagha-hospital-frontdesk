import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Heart, User, Phone, Calendar, Clock, MapPin, Building2, FileText, ArrowRight, Briefcase, Package } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { z } from "zod";

const bookingSchema = z.object({
  representativeName: z.string().trim().min(2, { message: "Name is required" }),
  companyName: z.string().trim().min(2, { message: "Company name is required" }),
  phone: z.string().trim().min(10, { message: "Valid phone number is required" }),
  product1: z.string().trim().min(2, { message: "Product 1 is required" }),
  product2: z.string().optional(),
  product3: z.string().optional(),
  product4: z.string().optional(),
  date: z.string().min(1, { message: "Date is required" }),
  time: z.string().min(1, { message: "Time is required" }),
  doctor: z.string().min(1, { message: "Doctor is required" }),
  hospital: z.string().min(1, { message: "Hospital is required" }),
  purpose: z.string().min(1, { message: "Purpose is required" }),
  notes: z.string().optional(),
});

type FormErrors = Partial<Record<keyof z.infer<typeof bookingSchema>, string>>;

const doctors = [
  { name: "Dr. Rahul Sharma", specialty: "General Medicine" },
  { name: "Dr. Priya Patel", specialty: "Cardiology" },
  { name: "Dr. Amit Kumar", specialty: "Orthopedics" },
  { name: "Dr. Sneha Gupta", specialty: "Neurology" },
  { name: "Dr. Vikram Singh", specialty: "Dermatology" },
];

const hospitals = [
  "Anagha City Hospital",
  "Central Medical Center",
  "Apollo Healthcare",
  "Max Super Specialty",
  "Fortis Hospital",
];

const purposes = [
  "Product Presentation",
  "Sample Distribution",
  "Medical Conference Invite",
  "Research Collaboration",
  "General Meeting",
];

const PharmaBookAppointment = () => {
  const [formData, setFormData] = useState({
    representativeName: "",
    companyName: "",
    phone: "",
    product1: "",
    product2: "",
    product3: "",
    product4: "",
    date: "",
    time: "",
    doctor: "",
    hospital: "",
    purpose: "",
    notes: "",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({ ...prev, [field]: e.target.value }));
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const result = bookingSchema.safeParse(formData);
    
    if (!result.success) {
      const fieldErrors: FormErrors = {};
      result.error.errors.forEach((err) => {
        const field = err.path[0] as keyof FormErrors;
        fieldErrors[field] = err.message;
      });
      setErrors(fieldErrors);
      return;
    }

    setIsLoading(true);
    
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Appointment Requested!",
        description: `Your meeting request has been sent for ${formData.date} at ${formData.time}. You will receive confirmation once the doctor approves.`,
      });
    }, 1500);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="container mx-auto px-4 py-4">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-hero flex items-center justify-center shadow-soft">
              <Heart className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-bold text-xl text-foreground">Anagha Health</span>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 bg-secondary/50 text-secondary-foreground px-4 py-2 rounded-full text-sm mb-4">
              <Building2 className="w-4 h-4" />
              For Pharma Professionals
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Schedule Doctor Meeting
            </h1>
            <p className="text-muted-foreground">
              Request an appointment with healthcare providers
            </p>
          </div>

          {/* Form */}
          <div className="bg-card rounded-2xl shadow-elevated border border-border/50 p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-2 gap-4">
                {/* Representative Name */}
                <div className="space-y-2">
                  <Label htmlFor="representativeName" className="text-foreground font-medium">
                    Your Name
                  </Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="representativeName"
                      type="text"
                      placeholder="Full name"
                      value={formData.representativeName}
                      onChange={handleChange("representativeName")}
                      className={`pl-10 h-12 ${errors.representativeName ? "border-destructive" : ""}`}
                    />
                  </div>
                  {errors.representativeName && <p className="text-sm text-destructive">{errors.representativeName}</p>}
                </div>

                {/* Company Name */}
                <div className="space-y-2">
                  <Label htmlFor="companyName" className="text-foreground font-medium">
                    Company Name
                  </Label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="companyName"
                      type="text"
                      placeholder="Pharma company"
                      value={formData.companyName}
                      onChange={handleChange("companyName")}
                      className={`pl-10 h-12 ${errors.companyName ? "border-destructive" : ""}`}
                    />
                  </div>
                  {errors.companyName && <p className="text-sm text-destructive">{errors.companyName}</p>}
                </div>
              </div>

              {/* Phone */}
              <div className="space-y-2">
                <Label htmlFor="phone" className="text-foreground font-medium">
                  Phone Number
                </Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+91-XXXXXXXXXX"
                    value={formData.phone}
                    onChange={handleChange("phone")}
                    className={`pl-10 h-12 ${errors.phone ? "border-destructive" : ""}`}
                  />
                </div>
                {errors.phone && <p className="text-sm text-destructive">{errors.phone}</p>}
              </div>

              {/* Products Section */}
              <div className="space-y-3">
                <Label className="text-foreground font-medium">Products to Present</Label>
                <div className="grid grid-cols-2 gap-4">
                  {/* Product 1 */}
                  <div className="space-y-2">
                    <div className="relative">
                      <Package className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <Input
                        id="product1"
                        type="text"
                        placeholder="Product 1 *"
                        value={formData.product1}
                        onChange={handleChange("product1")}
                        className={`pl-10 h-12 ${errors.product1 ? "border-destructive" : ""}`}
                      />
                    </div>
                    {errors.product1 && <p className="text-sm text-destructive">{errors.product1}</p>}
                  </div>

                  {/* Product 2 */}
                  <div className="relative">
                    <Package className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="product2"
                      type="text"
                      placeholder="Product 2 (Optional)"
                      value={formData.product2}
                      onChange={handleChange("product2")}
                      className="pl-10 h-12"
                    />
                  </div>

                  {/* Product 3 */}
                  <div className="relative">
                    <Package className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="product3"
                      type="text"
                      placeholder="Product 3 (Optional)"
                      value={formData.product3}
                      onChange={handleChange("product3")}
                      className="pl-10 h-12"
                    />
                  </div>

                  {/* Product 4 */}
                  <div className="relative">
                    <Package className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="product4"
                      type="text"
                      placeholder="Product 4 (Optional)"
                      value={formData.product4}
                      onChange={handleChange("product4")}
                      className="pl-10 h-12"
                    />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {/* Date */}
                <div className="space-y-2">
                  <Label htmlFor="date" className="text-foreground font-medium">
                    Preferred Date
                  </Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={handleChange("date")}
                      className={`pl-10 h-12 ${errors.date ? "border-destructive" : ""}`}
                    />
                  </div>
                  {errors.date && <p className="text-sm text-destructive">{errors.date}</p>}
                </div>

                {/* Time */}
                <div className="space-y-2">
                  <Label htmlFor="time" className="text-foreground font-medium">
                    Preferred Time
                  </Label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <Input
                      id="time"
                      type="time"
                      value={formData.time}
                      onChange={handleChange("time")}
                      className={`pl-10 h-12 ${errors.time ? "border-destructive" : ""}`}
                    />
                  </div>
                  {errors.time && <p className="text-sm text-destructive">{errors.time}</p>}
                </div>
              </div>

              {/* Doctor */}
              <div className="space-y-2">
                <Label htmlFor="doctor" className="text-foreground font-medium">
                  Select Doctor
                </Label>
                <select
                  id="doctor"
                  value={formData.doctor}
                  onChange={handleChange("doctor")}
                  className={`w-full h-12 rounded-md border bg-background px-3 text-foreground ${errors.doctor ? "border-destructive" : "border-input"}`}
                >
                  <option value="">Select doctor</option>
                  {doctors.map((d) => (
                    <option key={d.name} value={d.name}>{d.name} - {d.specialty}</option>
                  ))}
                </select>
                {errors.doctor && <p className="text-sm text-destructive">{errors.doctor}</p>}
              </div>

              {/* Hospital */}
              <div className="space-y-2">
                <Label htmlFor="hospital" className="text-foreground font-medium">
                  Select Hospital
                </Label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                  <select
                    id="hospital"
                    value={formData.hospital}
                    onChange={handleChange("hospital")}
                    className={`w-full h-12 rounded-md border bg-background pl-10 pr-3 text-foreground ${errors.hospital ? "border-destructive" : "border-input"}`}
                  >
                    <option value="">Select hospital</option>
                    {hospitals.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </div>
                {errors.hospital && <p className="text-sm text-destructive">{errors.hospital}</p>}
              </div>

              {/* Purpose */}
              <div className="space-y-2">
                <Label htmlFor="purpose" className="text-foreground font-medium">
                  Purpose of Meeting
                </Label>
                <select
                  id="purpose"
                  value={formData.purpose}
                  onChange={handleChange("purpose")}
                  className={`w-full h-12 rounded-md border bg-background px-3 text-foreground ${errors.purpose ? "border-destructive" : "border-input"}`}
                >
                  <option value="">Select purpose</option>
                  {purposes.map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
                {errors.purpose && <p className="text-sm text-destructive">{errors.purpose}</p>}
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label htmlFor="notes" className="text-foreground font-medium">
                  Additional Notes (Optional)
                </Label>
                <div className="relative">
                  <FileText className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
                  <textarea
                    id="notes"
                    placeholder="Products to discuss, materials to bring..."
                    value={formData.notes}
                    onChange={handleChange("notes")}
                    rows={3}
                    className="w-full rounded-md border border-input bg-background pl-10 pr-3 py-3 text-foreground placeholder:text-muted-foreground"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                variant="hero"
                className="w-full h-12"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                    Requesting...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Request Meeting
                    <ArrowRight className="w-5 h-5" />
                  </span>
                )}
              </Button>
            </form>
          </div>

          {/* Back to Home */}
          <p className="text-center mt-6">
            <Link to="/" className="text-muted-foreground hover:text-foreground transition-colors text-sm">
              ← Back to Home
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PharmaBookAppointment;
