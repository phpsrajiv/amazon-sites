import {
  AlertTriangle, SearchX, TrendingDown, Clock,
  Zap, BrainCircuit, PenTool, Key, BarChart3,
  Link2, Rocket, Sparkles, Target, Users,
  Bot, MessageCircle, type LucideIcon,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  "alert-triangle": AlertTriangle,
  "search-x": SearchX,
  "trending-down": TrendingDown,
  "clock": Clock,
  "zap": Zap,
  "brain-circuit": BrainCircuit,
  "pen-tool": PenTool,
  "key": Key,
  "bar-chart-3": BarChart3,
  "link-2": Link2,
  "rocket": Rocket,
  "sparkles": Sparkles,
  "target": Target,
  "users": Users,
  "bot": Bot,
  "message-circle": MessageCircle,
};

export function getIcon(name: string): LucideIcon {
  return iconMap[name] || Sparkles;
}
