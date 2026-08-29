import { tenders, getTenderById } from "../data/tenders";

export const tenderService = {
  async getAll() {
    return [...tenders];
  },

  async getById(id) {
    return getTenderById(id) || null;
  },

  async search(query) {
    const q = query.toLowerCase();
    return tenders.filter(
      (t) =>
        t.name.toLowerCase().includes(q) ||
        t.id.toLowerCase().includes(q) ||
        t.department.toLowerCase().includes(q)
    );
  },

  async getByStatus(status) {
    if (!status || status === "All") return [...tenders];
    return tenders.filter((t) => t.status === status);
  },
};

export default tenderService;
