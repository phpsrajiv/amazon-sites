import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { LogIn, Loader2 } from "lucide-react";
import * as api from "@/lib/api";
import type { AuthUser } from "@/types/api";

interface AuthContextType {
  user: AuthUser | null;
  isLoggedIn: boolean;
  openLoginModal: () => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoggedIn: false,
  openLoginModal: () => {},
  logout: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [logoutToken, setLogoutToken] = useState<string | null>(null);
  const [isLoginOpen, setIsLoginOpen] = useState(false);
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const savedUser = sessionStorage.getItem("auth_user");
    const savedLogoutToken = sessionStorage.getItem("logout_token");
    if (savedUser && savedLogoutToken) {
      try {
        setUser(JSON.parse(savedUser));
        setLogoutToken(savedLogoutToken);
        api.fetchCsrfToken().catch(() => {
          sessionStorage.removeItem("auth_user");
          sessionStorage.removeItem("logout_token");
          setUser(null);
          setLogoutToken(null);
        });
      } catch {
        sessionStorage.removeItem("auth_user");
        sessionStorage.removeItem("logout_token");
      }
    }
  }, []);

  const handleLogin = useCallback(
    async (username: string, password: string) => {
      setIsLoggingIn(true);
      try {
        const response = await api.login(username, password);
        const authUser: AuthUser = {
          uid: response.current_user.uid,
          name: response.current_user.name,
        };
        setUser(authUser);
        setLogoutToken(response.logout_token);
        sessionStorage.setItem("auth_user", JSON.stringify(authUser));
        sessionStorage.setItem("logout_token", response.logout_token);
        setIsLoginOpen(false);
        toast({
          title: "Logged in",
          description: `Welcome back, ${authUser.name}!`,
        });
      } catch (error) {
        toast({
          title: "Login failed",
          description:
            error instanceof Error
              ? error.message
              : "Invalid credentials. Please try again.",
          variant: "destructive",
        });
      } finally {
        setIsLoggingIn(false);
      }
    },
    [toast]
  );

  const handleLogout = useCallback(async () => {
    if (!logoutToken) return;
    try {
      await api.logout(logoutToken);
    } catch {
      // Clear local state even if server-side logout fails
    }
    setUser(null);
    setLogoutToken(null);
    sessionStorage.removeItem("auth_user");
    sessionStorage.removeItem("logout_token");
    toast({
      title: "Logged out",
      description: "You have been signed out.",
    });
  }, [logoutToken, toast]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoggedIn: !!user,
        openLoginModal: () => setIsLoginOpen(true),
        logout: handleLogout,
      }}
    >
      {children}
      <LoginModal
        isOpen={isLoginOpen}
        onClose={() => setIsLoginOpen(false)}
        onLogin={handleLogin}
        isLoggingIn={isLoggingIn}
      />
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

function LoginModal({
  isOpen,
  onClose,
  onLogin,
  isLoggingIn,
}: {
  isOpen: boolean;
  onClose: () => void;
  onLogin: (username: string, password: string) => Promise<void>;
  isLoggingIn: boolean;
}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) return;
    onLogin(username, password);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] bg-card/95 backdrop-blur-xl border-white/10 shadow-2xl shadow-primary/20">
        <DialogHeader>
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/20 mb-4 mx-auto">
            <LogIn className="w-6 h-6 text-primary" />
          </div>
          <DialogTitle className="text-2xl font-display text-center">
            Sign in to your account
          </DialogTitle>
          <DialogDescription className="text-center text-muted-foreground">
            Enter your credentials to log in.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label htmlFor="login-username">Username</Label>
            <Input
              id="login-username"
              placeholder="Your username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="bg-background border-white/10 focus-visible:ring-primary/50"
              autoComplete="username"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="login-password">Password</Label>
            <Input
              id="login-password"
              type="password"
              placeholder="Your password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="bg-background border-white/10 focus-visible:ring-primary/50"
              autoComplete="current-password"
            />
          </div>
          <Button
            type="submit"
            className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold h-12 text-lg shadow-lg shadow-primary/25 transition-all"
            disabled={isLoggingIn}
          >
            {isLoggingIn ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Signing in...
              </>
            ) : (
              "Sign In"
            )}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
