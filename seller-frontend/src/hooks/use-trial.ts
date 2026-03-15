import { useMutation } from "@tanstack/react-query";
import { submitTrialSignup } from "@/lib/api";

export interface TrialInput {
  name: string;
  email: string;
  storeUrl: string;
}

export function useSubmitTrial() {
  return useMutation({
    mutationFn: async (data: TrialInput) => {
      return submitTrialSignup({
        name: data.name,
        email: data.email,
        storeUrl: data.storeUrl || undefined,
      });
    },
  });
}
