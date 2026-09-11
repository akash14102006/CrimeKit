import { create } from "zustand";
import type { AdminUser } from "../types/admin";
import type { AdminTab } from "../types/admin";

export type { AdminTab };

interface AdminState {
  activeTab: AdminTab;
  setActiveTab: (tab: AdminTab) => void;

  selectedUser: AdminUser | null;
  setSelectedUser: (user: AdminUser | null) => void;

  searchQuery: string;
  setSearchQuery: (q: string) => void;

  roleFilter: string;
  setRoleFilter: (r: string) => void;
}

export const useAdminStore = create<AdminState>((set) => ({
  activeTab: "overview",
  setActiveTab: (tab) => set({ activeTab: tab }),

  selectedUser: null,
  setSelectedUser: (user) => set({ selectedUser: user }),

  searchQuery: "",
  setSearchQuery: (q) => set({ searchQuery: q }),

  roleFilter: "",
  setRoleFilter: (r) => set({ roleFilter: r }),
}));
