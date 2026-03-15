import React, { createContext, useContext, useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useSubmitTrial } from "@/hooks/use-trial";
import { Zap, Loader2 } from "lucide-react";

interface TrialContextType {
  openTrialModal: () => void;
}

const TrialContext = createContext<TrialContextType>({ openTrialModal: () => {} });

export function TrialProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <TrialContext.Provider value={{ openTrialModal: () => setIsOpen(true) }}>
      {children}
      <TrialModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </TrialContext.Provider>
  );
}

export const useTrial = () => useContext(TrialContext);

function TrialModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const { toast } = useToast();
  const mutation = useSubmitTrial();
  const [formData, setFormData] = useState({ name: "", email: "", storeUrl: "" });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.email) return;

    mutation.mutate(formData, {
      onSuccess: () => {
        toast({
          title: "Trial Started Successfully!",
          description: "Check your email for access instructions.",
          variant: "default",
        });
        setFormData({ name: "", email: "", storeUrl: "" });
        onClose();
      },
      onError: (error) => {
        toast({
          title: "Something went wrong",
          description: error.message,
          variant: "destructive",
        });
      },
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] bg-card/95 backdrop-blur-xl border-white/10 shadow-2xl shadow-primary/20">
        <DialogHeader>
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/20 mb-4 mx-auto">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <DialogTitle className="text-2xl font-display text-center">Start your 14-day free trial</DialogTitle>
          <DialogDescription className="text-center text-muted-foreground">
            No credit card required. Cancel anytime.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="name">Full Name</Label>
            <Input
              id="name"
              placeholder="Sarah Connor"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="bg-background border-white/10 focus-visible:ring-primary/50"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="email">Work Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="sarah@example.com"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              className="bg-background border-white/10 focus-visible:ring-primary/50"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="storeUrl">Amazon Store URL (Optional)</Label>
            <Input
              id="storeUrl"
              placeholder="https://amazon.com/..."
              value={formData.storeUrl}
              onChange={(e) => setFormData({ ...formData, storeUrl: e.target.value })}
              className="bg-background border-white/10 focus-visible:ring-primary/50"
            />
          </div>

          <Button 
            type="submit" 
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold h-12 text-lg shadow-lg shadow-primary/25 transition-all"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Setting up workspace...
              </>
            ) : (
              "Get Started Now"
            )}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
